# 40 — Data sanitization

Some folders are shared by every job: tool repos, project kits, this guidance folder, public releases.
They must be **project-agnostic**, and not only confidential. Nothing in them may even *allude* to a
specific job.

The reason is clarity as much as confidentiality. An example address or a "main drive" note copied from one job reads as if it applies to whatever job the next person is on.

## 1. What counts as job data
- Job, project or order numbers, customer and site names, machine names and serial numbers.
- Tag names, addresses, register numbers, setpoints, device ratings and counts taken from a real job.
- Paths to job folders, shares or projects. A path name alone can identify a job.
- Exports, backups, schematics, specs, workbooks, screenshots and logs from a job.
- Branch names, test-script names, fixture names and commit messages that mention a job.
- People's names, emails and credentials, except the git identity the repo already uses.

## 2. Where job data may live
- **Only in the job's own workspace** (e.g. `<jobs>\<job>\`), its shared project folder, and Claude's memory for that workspace.
- Never in:
  - a tool repo, including its ignored folders (`.claude\`, `tools\tests\out\`, local settings);
  - a kit or template;
  - this guidance folder;
  - a release or a public branch;
  - a report written for the tool developer.

## 3. Writing generic text
- **Examples use neutral values.** For example, for SLC addresses use `B3:40/[N7:10]`, `F20:[N7:5]`, `N50:[N7:6]`. Use "test project A/B" and "an RT Advanced IPC", not real ones.
- **Turn the lesson into a rule.** Instead of "UV0xx on job N stayed latched", write "an HMI pushbutton bit set with Set/InvertBit is never cleared: use momentary Set/Reset".
- Mark a lesson seen on one job only as *seen once*.
- Hardware notes are **device-type** references (setup, interface, gotchas, checklist). They never hold "the main drive", ratings or counts from a job.

## 4. Reports that cross from a job to a tool
When a job finds a tool problem, the report (`deliverables\YYYY-MM-DD_TOOL_<TOPIC>\README.md`) is split in two:
- **Everything from "Problem" down is generic**, so it can be pasted into the tool repo as it is. Use one observed case with numbers ("3 errors in 2 blocks refused an unrelated import") and no names.
- **A final section marked "stays with this job"** holds where it happened and which package is waiting for the fix.

## 5. Mechanical guards
- **`.gitignore` blocks job file types in every tool repo:**

  ```
  *.ap[0-9][0-9]  *.zap[0-9][0-9]  *.als[0-9][0-9]  *.apa  *.mer
  *.SLC *.slc *.SY5 *.SY6 *.EAS *.RSS *.ACD *.L5X *.L5K
  *.xlsx *.xls *.csv *.pdf *.doc *.docx *.eml *.msg
  *.aaPKG *.aaPDF *.cab *.project *.projectarchive
  /tools/tests/out/   /.claude/   (or track only the generic .claude/agents)
  ```

  Add a file type the moment a new job brings one.
- **Before every commit to a shared repo**, grep the staged diff and the commit message for job words:

  ```bash
  git diff --cached | grep -inE '<job no>|<customer>|<site>|<machine>|<tag prefix>' && echo "STOP: job data"
  ```

  Keep the job-word list in each job's own workspace, never in the repo.
- **The commit hooks in `tools/githooks/`** of this guidance folder (copy them into any shared tool repo as `.githooks/`) block a commit whose
  staged text or message contains a word from the deny-list, or any e-mail address (except `@example.com`). Set up once
  per master clone:
  1. Copy `tools/githooks/` into the repo as `.githooks/`, then `git config core.hooksPath .githooks`
  2. Create `~/.scriptkiddy-denylist.txt` (Windows: `%USERPROFILE%\.scriptkiddy-denylist.txt`), one job number, customer, site, machine or tag prefix per line.
     It lives **outside** every repo, so the list of jobs never reaches the guidance or a workspace copy.
     `SCRIPTKIDDY_DENYLIST` points elsewhere if needed.

  Without the deny-list the hook only warns. It doesn't read binary files (`.docx`, `.exe`, images). Claude adds the
  job's words to the deny-list before committing a lesson, and never bypasses the hook with `--no-verify` without the
  user's say-so.
- **Before every release**, grep the whole tree, not just the diff. Also check screenshots: window titles and paths in them count.
- **Git history keeps everything.** Once job data is in a commit, cleaning the files doesn't remove it. Publish only a **history-free branch** (section 50 §4). Never push the private history or its tags.

## 6. Shared folders and copies
- Copying a repo or tool folder to another machine or share copies its ignored folders too: `.claude\`, test output, local settings. Check them before sharing the copy.
- A cleanup pass on an existing repo goes on its own branch (e.g. `cleanup/project-agnostic`). It covers comments, example addresses, test names, docs, screenshots and branch names. Rename any job-named branch.

## 7. Secrets and personal projects
Personal and hobby repos (web sites, firmware, home-server scripts) don't carry job data, but they carry **secrets**,
and some of them are public on GitHub.
- **Secrets live in an ignored env file**, never in code or chat: `.env.local` (or `.env`) beside a committed
  `.env.example` that lists the keys with empty values. Firmware uses an ignored `secrets.h` / `wifi_credentials.h`
  with a committed `*.example.h`. Check `.gitignore` covers it **before** the first commit.
- **Never ask the user to paste a key, password or token into chat.** Tell them which file to put it in.
- **Never print secret values** when reading another program's config or database: filter out `*key*`, `*pass*`,
  `*token*`, `*secret*` columns and lines (e.g. `sqlite3 -readonly`, then select named columns only).
- **Root passwords stay with the user.** When a step needs `sudo` and `sudo -n` fails, write the script and have the
  user run it (rule 70 §3); don't try to collect or pipe a password.
- **Recovery codes, SSH keys and API keys found in a folder are not copied** into this guidance, a kit or a report,
  and are not quoted back. Mention that the file exists and where, if it matters.
- **Household and machine facts** (hostnames, LAN addresses, users, ports, device models, which tools are installed)
  never go in this folder. They live in `~/.claude/MACHINES.md` (outside this folder), each project's own
  `CLAUDE.md`, or Claude memory.
- **Captures and logs from security tools** (pcaps, captured portal credentials, wardrive logs on an SD card) are
  personal data of other people. Don't open, summarise or copy them unless the user asks for that specific file.
