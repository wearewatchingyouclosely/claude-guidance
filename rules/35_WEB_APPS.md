# 35 — Web apps

Three kinds of web app, all built the same careful way:
- **Hosted sites:** React + Vite on Netlify, with Netlify Functions as the back end (§1–§6).
- **Local tool GUIs:** a Python tool serves its own page and JSON API, on the desktop or a home server (§7).
- **Device panels:** a small box (SBC, server) with a login, behind a reverse proxy (§8).

Rules 00 and 40 apply. Rule 30 §7 covers the tools behind a local GUI (dry run, undo, jobs). Rule 32 covers
single-file generated *reports*; this rule covers apps people use. Lessons are *seen once* unless marked.

## 1. Hosted sites: stack and layout
```
<site>/
  index.html  vite.config.mjs  package.json  package-lock.json  netlify.toml
  src/            pages/  components/<feature>/  hooks/  utils/  themes/
  public/         static files served as is
  netlify/functions/   one file per endpoint, plus shared helpers (store, auth, responses)
  docs/screenshots/    one per screen and per user flow
  .env.example    every key the site reads, values empty
```
- **`netlify.toml` holds the build:** `command = "npm run build"`, `publish = "dist"`, the functions directory,
  `node_bundler = "esbuild"`. Make sure every npm package a function `require`s is installed on deploy: the
  root `package.json` is the safe place. If it's only in a `netlify/functions/package.json`, check a deploy log
  that it was installed, or the build passes and the function crashes at its first call.
- **SPA routing:** one `/* → /index.html 200` rule, either in `netlify.toml` or `public/_redirects`, not both.
  Functions under `/.netlify/functions/*` are matched first.
- **Local dev = `netlify dev`**, never plain `vite`: Vite doesn't mount the functions, so every API call fails
  and looks like a front-end bug. With a non-default Vite port, add `[dev] command = "vite"`, `targetPort = 5173`,
  `framework = "#custom"`. Script it as `"netlify:dev": "npx netlify dev"`, and run every `package.json` script
  once after editing it (a missing space, as in `npxnetlify`, breaks a script and nothing warns you).
- **One feature, one folder:** a sub-site or section (a podcast player, a points store) gets
  `pages/<Feature>.jsx`, `components/<feature>/` with its own CSS, and its own hooks, so it can be removed whole.
- **Lockfile is committed.** Don't ignore `package-lock.json`: without it every deploy can pull different versions.
  Use one package manager per repo (a stray `deno.lock` next to `package-lock.json` means two).
- Keep major versions in step across your sites when you can (Vite 4 vs 5, plugin-react 4 vs 5). When you upgrade
  one, note it in the README.

## 2. Netlify Functions
- **Shape:** check the method first (`405`), parse the body inside try/catch (`400 Invalid JSON`), validate every
  field (type, trimmed, length, number > 0, value in an allowlist), then act. Return JSON with a correct status:
  `400` bad input, `401` wrong password, `404` missing item, `405` wrong method, `409` conflict, `500` server misconfigured.
- **Share the helpers.** JSON responses (`ok()`, `err()`), the admin check and the store go in one module that
  every function imports. Copy-pasted versions drift (seen: three different names for the admin-password variable).
- **Netlify Blobs from a `exports.handler` (Lambda-style) function needs `connectLambda(event)`** before
  `getStore(...)`, so pass `event` down to the store helper. Without it, Blobs has no context and fails. *Seen twice.*
  An explicit site ID plus token (`NETLIFY_BLOBS_SITE_ID`/`NETLIFY_BLOBS_TOKEN`) also works, for scripts.
- **A local-file fallback store is for `netlify dev` only.** Choose it explicitly (e.g. `NETLIFY_DEV` set, or no
  Blobs context *and* not on Netlify), report which mode is active (`mode: "blobs" | "local-file"`), and never
  fall back silently in production: a function's filesystem is temporary, so the data just disappears.
- **Scheduled functions:** declare the schedule in one place (`netlify.toml` *or* `exports.config`, not both),
  remember it runs in **UTC**, and log a start/success/failure line with the request id and a short result summary.
  Make the scheduled job a thin wrapper around the same function an admin button can run by hand.
- **Syncing data from an outside source** (a published spreadsheet CSV, another API):
  - fetch with `Cache-Control: no-cache`, try the candidate URLs in order;
  - **validate before overwriting:** not empty, required columns present. On failure keep the last good copy
    and report the error, so a broken source never blanks the site;
  - normalise spreadsheet CSVs: strip a BOM, skip a `sep=,` line, map header aliases (`username`/`user` →
    `user_name`), look for the header in the first ~20 lines;
  - store the data and an `updated-at` stamp side by side, and show the stamp on the page.
- **Proxying a third-party feed** (RSS, an API) to the browser:
  - the feed URL and any token in it come from an environment variable, never the source (rule 40 §7);
  - pass on only `https://` URLs, and only from the domains you expect; strip HTML from text fields;
  - an in-memory cache with a TTL only lives as long as a warm instance; that's fine for "don't refetch on every
    request", not as storage.
- Don't return `error.message` from unexpected exceptions to the public. Log it; return a short generic message.

## 3. Secrets and config
- **Anything prefixed `VITE_` is built into the public JavaScript bundle.** Never put a password, token or key
  in a `VITE_` variable, and never compare a password in the browser: the check belongs in a function, against a
  server-only variable. A "local mode" password in the front end counts too: it ships in `dist/` to everyone.
- **Server-only variables** (`ADMIN_PASSWORD`, API keys, mail keys, feed URLs) are set in `.env` locally and in the
  site's environment settings on Netlify. One name per setting, documented in `.env.example` and the README.
- **No real defaults in code** for recipient e-mail addresses, spreadsheet IDs, account names or feed URLs: a
  public repo publishes them. Read them from the environment; if one is missing, fail with a clear message
  ("Server is missing X").
- An e-mail notification that can't be sent (settings missing, provider down) doesn't fail the user's request:
  return `ok` with `emailSent: false` and a warning, and keep the record in storage so nothing depends on the mail.

## 4. Admin pages
- **The password is checked by a function on every admin request**, not once at "login": send it as
  `Authorization: Bearer <password>` and compare it on the server with a constant-time comparison
  (`crypto.timingSafeEqual` on equal-length buffers). Keep it in memory or `sessionStorage`, not `localStorage`.
- If the password variable is unset, return `500 Server is missing …`, never let everyone in.
- Admin actions are an allowlist (`approve | deny | trash` → status), not free text. Prefer a soft "trashed" status
  over deleting a record, with a toggle to view the trash.
- Path matching for an admin route is case-insensitive and accepts its obvious variants (`/admin-page`,
  `/adminpage`), but don't count on an obscure URL for security.
- An admin **preview** (show the page as it will look on a chosen future date, or with a hidden feature on) beats
  editing live data to see the effect.

## 5. Front end
- **Data hooks** (`useThing()`) return `{ data, loading, error }`, check `res.ok`, ignore the result after unmount
  (a `cancelled` flag or `AbortController`), and may keep a module-level cache so moving between pages doesn't
  refetch. Every list has a loading state, an error state and an **empty state** that says what's going on
  ("no ranked data yet — check back after …").
- **Rules that change over time live in one table in `utils/`**, e.g. prize periods with `effectiveFrom` dates:
  the entry with the latest `effectiveFrom` on or before the date in question applies. The page and the admin
  preview both read that table, so a change is made once. Dates shown to users name their time zone when it matters.
- **Feature flags** for temporarily hidden features go in one `featureFlags.js` with a comment saying how to turn
  them back on. Don't delete a feature you only want hidden.
- Seasonal or fun modes (holiday themes, animations, an easter egg) are toggled in one theme runtime, respect
  `prefers-reduced-motion`, and never cover content or controls.
- **Mobile first:** test at phone width; header buttons stay side by side or stack on purpose; no sideways scroll.
- Never use `dangerouslySetInnerHTML` with data from a feed, a sheet or a user.
- README screenshots per screen and per flow (visitor, admin); retake them when the UI changes.

## 6. Git hygiene for sites (read before the first push)
- **`.gitignore` from day one:**
  ```
  node_modules/  dist/  .vite/  .netlify/  .netlify-local-data/
  .env  .env.*  !.env.example
  *.zip  *.docx  data exports (*.csv / *.json pulled from live data)
  ```
  Third-party documents (an API spec someone sent you) and live data (queues, leaderboards, user names) never go
  in the repo, even a private one.
- **Before the first push and before every `git add .`, run `git status` and `git ls-files | cut -d/ -f1 | sort | uniq -c`**
  and look for `node_modules`, `dist`, local data folders, `.env` files and files holding tokens.
- **If something got committed:** `git rm -r --cached <path>`, fix `.gitignore`, commit. The history still has it
  (rule 40 §5): **change any secret that was in it**, and ask the user before rewriting a pushed history.
- Netlify builds from the repo, so `dist/` never needs committing.

## 7. Local tool GUIs (Python)
A tool that serves its own page: `tool.py serve` or `./run.sh`, one HTML page plus a JSON API.
- **Stack:** stdlib `http.server.ThreadingHTTPServer` with a route table (`{"/api/state": fn, …}`) for
  single-file tools; Flask or FastAPI when the tool already has a venv. Serve one `ui.html`/`index.html`
  (vanilla JS, no build step) and JSON under `/api/*`. Open the browser on start for desktop tools.
- **Bind `127.0.0.1` by default.** Bind the LAN (`0.0.0.0`) only when the user wants it from other devices, and
  then say in the README that anyone on the network can use it (no auth).
- **A localhost API is reachable from any website the user visits** (the browser will send the request). For a tool
  that changes files, generate a **per-run token** (`secrets.token_urlsafe`), inject it into the page it serves,
  and require it as a header (`X-<Tool>-Token`) on every API call. Requests without it get `403`.
- **Map errors to statuses in one place:** bad input (`KeyError`/`ValueError`) → `400`, workflow order not met → `409`,
  anything else → `500` with the type and message, and the traceback printed to the server log.
- **Every path from a request is checked:** resolve it and require it to stay under the root
  (`root in full.parents`), on every route that touches files, including image and thumbnail routes.
- **An image or file proxy only fetches from an allowlist** (`url.startswith("https://<expected host>/")`), or it
  becomes a way to make the server fetch anything.
- **Run commands with a list of arguments and a timeout** (`subprocess.run([...], timeout=…)`), never `shell=True`
  with anything from a request.
- **Front end:** one `api(path, body)` fetch wrapper that shows errors; **escape every value** put into
  `innerHTML` (one `esc()` helper, used everywhere); `confirm()` before destructive actions, saying how many items
  and how much space; hash routes for deep links; a dark mode from `prefers-color-scheme`.
- **Long jobs:** start them with a POST that returns a job id; the page polls `/api/job?id=…&since=<n>` and gets
  only the new log lines. A Stop button sets a cancel flag. Read-only and write jobs are in separate lanes (rule 30 §7).
- **Caching:** API responses `Cache-Control: no-store`; generated images cached, keyed on `path|size|mtime|params`,
  so they refresh when the file changes. A slow listing is cached to a file with a TTL and refreshed in a
  background thread under a lock; the page gets the cached copy at once.
- **Keep old versions in git, not as `app.py.bak-before-<change>` files** beside the code. If the folder isn't a
  repo yet, `git init` it before the second big change.

## 8. Device panels behind a reverse proxy
For a box with several web services (a control panel, a file browser) and one login.
- **Caddy on port 80 is the only thing listening on the network;** every app listens on `127.0.0.1`.
- **One login for everything with `forward_auth`:** Caddy asks the panel's `/auth/check` before proxying to the
  other apps, and passes on the user in a header (`copy_headers X-Remote-User`). **Strip that header from client
  requests** (`request_header -X-Remote-User`) on every route, or anyone can claim to be logged in.
- **Log in against the box's own Linux account** with PAM. A service running as that user can verify only its own
  password, so allow just that user.
- **Session cookie:** HMAC-signed `user|expiry` with a secret kept in a root-readable file outside the repo, checked
  with `hmac.compare_digest`, `HttpOnly`, `SameSite=Lax`, a `max_age`. Logout deletes it.
- **Redirect after login only to a local path** (starts with `/`, not `//`), so the `next=` parameter can't send the
  user to another site.
- Turn off framework extras you don't use (FastAPI `docs_url=None, redoc_url=None, openapi_url=None`).
- **While a backend is still starting** (right after boot), have the proxy answer `502`/`503` with a small page that
  refreshes itself every 2 s ("starting…"), instead of a browser error.
- Run each app as a systemd unit (`User=`, `Restart=on-failure`, `RestartSec=3`), installed by the project's
  `install.sh`.

## 9. Testing
- **Back-end logic gets unit tests** that run with no network: `python3 -m unittest discover -s tests` for tools,
  a small test runner for functions (paths, params, validation, auth). Live smoke tests run only when the env
  provides the real URL and key (rule 30 §8).
- **Run it the way it will run:** `netlify dev` for sites, the real `serve` command for tools. Click through every
  flow (visitor, admin, error, empty), at desktop and phone width, and look at the browser console.
- After a change to a function, call it once with good input and once with each kind of bad input, and check the
  status codes.
- Screenshot every screen you changed before calling it done.
