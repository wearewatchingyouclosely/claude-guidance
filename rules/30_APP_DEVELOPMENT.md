# 30 — General app development

Tools and apps: converters, exporters, viewers, testers, utilities. The common rules (00) apply.
Branching and releases are in section 50.

§1–§6 are the defaults for **Windows tools handed to other people** (the portable .exe). For **personal tools on Linux**
(home server, media, game mods, device sync) and **small web sites**, §7 and §8 replace §1 and §2; §3–§6 still apply.

## 1. The default: one portable .exe
**Most users want to test a complete .exe, not source code.** They download or copy one file, double-click it and try it. Design for that from the first commit.

- **One self-contained executable** in the repo root (gitignored), rebuilt by a single build command or script (`tools\build.ps1`).
  - No installer.
  - No runtime to install.
  - No side files it needs in order to start.
  - Embed resources: images, icons, HTML templates, palettes.
- **Default stack for Windows desktop tools:** C# **WPF on .NET Framework 4.8**.
  - .NET Framework 4.8 is already on every Windows 10/11 machine, so nothing needs installing.
  - Merge dependencies into the exe, e.g. Fody/Costura, or avoid NuGet packages altogether.
  - Use something else only when the job demands it (e.g. a vendor API that needs another runtime). Ask first.
- **Output that people share is self-contained too.** A viewer or report is one HTML file with everything inline. It opens in Edge or Chrome with no server, and can be mailed.
- **Hand over the exe, not instructions to build it.**
  - "Done" means the user can run the exe you built.
  - Say where it is, and which version and commit it came from.
- Never overwrite the exe the user is running or testing. If a build fails because the app is open, close it first (only the instance you're allowed to close).
- Keep the release exe separate from the dev build. Section 50 §3 covers the release folder.

## 2. Default GUI style
Make every new tool look and behave like the existing ones, so users already know how to use it. The full style guides, with ready-to-use files in `starter-kits\`, are [31_STYLEGUIDE_EXE.md](31_STYLEGUIDE_EXE.md) and [32_STYLEGUIDE_HTML.md](32_STYLEGUIDE_HTML.md).
- **Two styles:** Modern and Windows 95.
  - The desktop exe's Modern style is dark only.
  - Generated HTML pages add System/Light/Dark to Modern.
  - Swap the palette and shape resource dictionaries per style.
  - Switch them in a Style option and in the window's right-click menu (Appearance).
- **Start-up screen:** a launcher with one card per tool. Every tool window has a **"← Main menu"** button, disabled while busy.
- **Inputs:**
  - Path fields have Browse, recent paths and drag-drop.
  - Files or folders can be dropped anywhere on the window, or onto the exe in Explorer, and go to the right field.
- **"Before you go" checklist** of what was found, with one mark per item:
  - ✔ found;
  - ! optional but missing;
  - ✖ blocks the run;
  - – not used.

  Each row's right-click menu offers the fix.
- **Right-click menus everywhere:**
  - Path fields: browse, open, show in Explorer, recent paths.
  - The run button: run, or copy the equivalent command line.
  - The log: copy, save, clear.
  - Each menu ends with the appearance options.
- **Output/log pane**, colour-coded by severity. While the tool is waiting for the user (a firewall prompt, a dialog), the pane pulses. Long steps report once a minute that they're still running, so a slow step can be told from a hung one.
- **Settings and recent paths are remembered** in `%APPDATA%\<AppName>\settings.json`. Never store them next to the exe.
- **Every window fits the work area**, at any DPI. Never assume 1920×1080.
- **Icons:** made with the repo's `make-icon` script from the image the user supplies. Don't reinterpret or crop a supplied image.

## 3. Headless mode
- **Every GUI action has a command-line equivalent**, for scripts, tests and other sessions: `App.exe <command> <args> [--flags]`.
  - Document it in the README.
  - The GUI's "copy command line" gives the exact command.
- **Exit codes mean something:** 0 = success. Other codes are documented, for example "saved with errors".
  - Never print SUCCESS when nothing was done. "0 imported, N unchanged" is a warning.
- When a host program approves callers by file hash (e.g. an API firewall), run headless commands through a **stable runner exe** that loads the current build. Then the approval survives rebuilds.

## 4. Behaviour rules
- **Test the user's real sequence**, not one clean run. Typical sequence: run → the report opens in Calc and locks the file → run again. A locked output file must never fail a run: write beside it and say so.
- **Fail loudly and usefully.** Report the first real error, which file and which line, and what to do about it. Don't print a stack trace in place of a message.
- **Never change user data silently.** For imports into another application:
  - show what will change;
  - detect conflicts (changed on both sides since the export);
  - ask per item;
  - refuse operations known to lose data, e.g. replacing objects the import format can't carry fully.
- **Write the tool's own logs beside the data it worked on**, in a folder the tool itself skips on the next run.
- Reports open in the user's spreadsheet program: assume Calc, not Excel (00 §7).

## 5. Testing
- Keep test scripts in the repo (`tools\tests\`), with output in a gitignored `tools\tests\out\`. Run them after every change. Typical set:
  - **Fast functional check** (seconds, no external application): convert or process the reference inputs, and compare counts with the last known good run. A drop is a regression.
  - **GUI check:** open every window, press every Main menu button, take a screenshot of each window, and check it fits the screen. Look at the screenshots.
  - **Full integration run** against the external application. It's slow, so run it in the background.
- **Verify a GUI change by launching the app and taking a screenshot.** Don't rely only on reading the XAML.
- Test data is synthetic or neutral (section 40). Real job files are used from their job folder and never copied into the repo.
- When a test needs the user (a firewall or UAC prompt), say so and skip it. Don't wait.

## 6. Documentation
- **README:**
  - what the tool does;
  - how to run the exe (portable, what it needs);
  - every input and where to get it from the source application ("File → Save As → *.SLC");
  - the command line;
  - screenshots.
- Write the README for the user of the exe, not for the developer. Developer notes go in `docs\`.
- Keep a `docs\BACKLOG.md` of requests and ideas, one line each, with the date and the source.
- When a tool is abandoned, mark it deprecated in the code, window banner, launcher card, README and a `DEPRECATED.md`. Don't delete it. Don't resume it without the user asking.

## 7. Personal Linux tools (home server, media, mods, device sync)
All *seen once* unless marked.
- **Default stack: one Python 3 file, stdlib only** (plus Pillow or similar only when needed), started by `./run.sh`
  or a small wrapper in `~/.local/bin`. Nothing to `pip install` when it can be avoided. If a venv is needed, keep it
  in the project folder and point the launcher at the venv's `python3`.
- **The GUI is a local web page served by the tool itself** (`tool.py serve`, vanilla JS, a JSON API under `/api/*`;
  how to build it safely is rule 35 §7).
  The browser is the GUI toolkit; it works from the phone on the LAN too. LAN-only and no auth is acceptable for a
  home tool; say so in the README. Give each view a **deep link** (`#open=…`, `#compare?a=…&b=…`) so a session can
  hand the user a URL to exactly what it means.
- **Every mutating command is a dry run unless `--apply`.** Show the user the dry run (counts, GB, a few examples,
  anything surprising) before applying anything non-trivial. The GUI's Apply button is the same switch.
- **Never `rm` user data.** Move it to a trash folder on the **same filesystem** (instant moves), journal every move
  under a run id, and give an `undo <run-id> --apply`. Only an explicit `trash --purge --apply` deletes, and only when
  the user asks.
- **Enforce the order of steps when order matters** (e.g. scan → health → dedupe → convert → compress: dedupe before
  re-encoding, so no work is wasted and size comparisons use originals). Refuse a later step's apply until earlier
  ones are done or skipped; `--force` overrides; reopening a step reopens the later ones.
- **Crash and power-loss safety for long jobs.** Persist progress as you go (per file, per group), stage a replaced
  file as `<name>.new` beside the original and swap only at the end, clean up stale temp on start, and keep a resume
  registry so a restarted server relaunches the interrupted job. A deploy then resumes the running job by itself.
- **Long jobs run in the background** (`tool bg <cmd> --apply`, a `screen`/systemd unit) with a log the session can
  tail. Jobs can be stopped gracefully (a cancel flag checked between items). Read-only jobs may run alongside one
  write job; never two writers.
- **Measure before you decide.** Use real on-disk size (`du`, `st_blocks`), not apparent size: sparse files exist,
  and can look thousands of times bigger than they are. Estimate a lossy step on a sample before running it on
  everything. A "lossless conversion" can make files bigger (seen: repacking archives).
- **Heuristic matches are never pre-ticked.** Duplicates by name/number can be different things. Confirm by content
  (hashes, perceptual hashes of images or frames) and leave unconfirmed groups for the user. Never pre-select a
  removal that would leave another tool (a library manager, a tracker) pointing at a missing file.
- **Prefer the CLI over SSH to the SMB mount** for bulk file work on the server: it is far faster. Deploy = copy the
  file over and restart the service; check it imports (`python3 -c "import tool"`) before deploying.
- **Test risky changes on a sandbox copy** selected by environment variables (`TOOL_LIBRARY=~/test …`), never on
  the real library first.
- **Respect third-party rate limits.** Pace calls, cache responses for days, track quota per API path, wait instead
  of failing, and make the work resumable. If you patch another app locally to slow it down, keep the `.orig`, and
  write down that an update will overwrite the patch.
- **On btrfs, use copy-on-write clones** (`cp --reflink=auto`) for build trees: a full build then takes about a
  second and no extra space.
- **Keep the original script** a tool replaces (`og script/`) until the new tool reproduces its output, and say in
  the README which outputs are identical and which differ on purpose.

## 8. Web sites and API clients
Web sites, local web GUIs and device panels are covered in full by [35_WEB_APPS.md](35_WEB_APPS.md). API clients:
- **API clients start as a harness:** a tiny client, unit tests for paths, params and auth headers, and live smoke
  tests that run only when the env file provides a base URL and key. Then a live failure is clearly the remote side.
- **When a live API returns HTML instead of JSON** (e.g. a 403 with "Just a moment…"), it's a bot-protection page,
  not the API. Don't try to get around it. Write a short note for the provider: what you send, what works, the exact
  status, content type and first line of the body, and the questions to answer (base URL, allow-listing, required
  headers, sandbox host).
