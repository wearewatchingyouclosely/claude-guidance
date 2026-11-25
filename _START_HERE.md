# START HERE: setting up Claude Code and starting a project

Script Kiddie: A script kiddie (sometimes called a skiddie or skid) is a pejorative term in cybersecurity for an unskilled, inexperienced individual who uses pre-made scripts, software, or tools. The author of this document fits this description.

Two parts:
- **Part A, once per PC:** VS Code, Git, Claude Code and the viewers.
- **Part B, once per project:** point the project at this folder (or copy it in), then paste the kickoff prompt.

---

# Part A: set up the PC

You need a Claude account that includes Claude Code (Pro, Max, Team, Enterprise, or a Console/API account).

## A1. Linux (Debian / Ubuntu / Mint)
Run the setup script from this folder **as yourself** (not with sudo). It shows what it would do first and changes
nothing until you add `--apply`:

```bash
bash setup/linux-setup.sh                  # dry run: see what's missing
bash setup/linux-setup.sh --apply          # git, python, ssh, PuTTY, VS Code + Claude Code and the viewer extensions
```

Add the parts you need (they combine; `--all` is everything):

| Option | Adds | Rules |
|---|---|---|
| `--esp32` | arduino-cli, PlatformIO, pyserial, the `dialout` group, removes `brltty` | 60 |
| `--web` | nvm and Node LTS | 35 |
| `--kicad` | KiCad from the official PPA | 60 §7 |

It also records where this folder is in `~/.claude/CLAUDE.md` (see B1). It asks for your sudo password once, skips
anything already set up, and is safe to run again. No esp32 core is
installed: each project names its own (rule 60 §1). After `--esp32`, log out and back in before flashing a board.

## A1 (Windows)
1. Run **`setup\Ninite Git Notepad PuTTY Python Python 3 Installer.exe`** and click **Yes** at the admin prompt. It
   installs Git, Notepad++, PuTTY and Python 3 with default settings, asks no questions, and says **Done** when
   finished. Running it again later updates them.
   - **Check it first:** right-click → **Properties** → **Digital Signatures**. The signer must be
     **Secure By Design Inc.** (the company behind [Ninite](https://ninite.com)). If it isn't, don't run it.
   - The .exe holds no apps: it downloads each one from its official source.
2. Install **VS Code** from code.visualstudio.com (the installer above doesn't include it).
3. Optional: **LibreOffice** (opens Office files without Office) and a PDF reader.

Git matters even if you don't use version control: on Windows, Claude Code runs its commands in the **Git Bash** that
Git installs. If it can't find it, see Troubleshooting.

## A2. Claude Code and the viewers
In VS Code, install **Claude Code** (publisher **Anthropic**, `anthropic.claude-code`) and sign in. Then, from a
terminal:

```bash
code --install-extension anthropic.claude-code
code --install-extension shd101wyy.markdown-preview-enhanced
code --install-extension yzhang.markdown-all-in-one
code --install-extension bierner.markdown-mermaid
code --install-extension tomoki1207.pdf
code --install-extension cweijan.vscode-office
code --install-extension mechatroner.rainbow-csv
```

| Extension | What for |
|---|---|
| Markdown Preview Enhanced, Markdown All in One, Mermaid | Rendered `.md` with tables and diagrams (`Ctrl+Shift+V`) |
| vscode-pdf | PDFs in a tab |
| Office Viewer | `.docx`/`.xlsx` read-only in a tab. It takes over `.md` files: right-click the tab → **Reopen Editor With…** → **Text Editor** → make that the default |
| Rainbow CSV | Lines CSV columns up |

Optional for firmware: **PlatformIO IDE** (`platformio.platformio-ide`) if you'd rather not use the CLI.

---

# Part B: start a project

## B1. Decide how the project gets the rules
Below, **`<guidance>`** means this folder, wherever you cloned or copied it. Its name and location don't matter: each
PC records it once, in `~/.claude/CLAUDE.md` (Windows: `%USERPROFILE%\.claude\CLAUDE.md`), which Claude Code reads in
every session. On Linux, `setup/linux-setup.sh` writes it (`--register-only --apply` does just that step); anywhere
else, kickoff step 0 has Claude add it. **Moved or re-cloned the folder? Register it again.** Nothing else needs editing.

- **Your own projects on this PC:** **don't copy this folder in.** Projects use the registered `<guidance>`, so
  lessons land in one place.
- **Work jobs, other PCs, or anything shared:** copy the whole folder into the project, keeping its name. Delete
  `starter-kits/` from the copy if there's no app work.

## B2. Open the project folder in VS Code
Open the **project** folder (not this one), trust it, and open Claude Code.

## B3. Paste the kickoff prompt
Change the two lines at the top first.

```text
Kick off this project.

Project: <short name, e.g. "CYD 2.4R weather display" or "Job 1234 – packaging line">
What it is: <one or two lines: "port this sketch to LVGL", "home-server script for X", "port an old PLC program">

0. Find the guidance folder: a copy inside this project if there is one, otherwise the path in
   ~/.claude/CLAUDE.md. If neither exists, ask me where it is, then add this block to ~/.claude/CLAUDE.md
   (create the file if needed; keep anything already in it):
     <!-- claude-guidance:start -->
     Claude guidance folder: <the absolute path>
     <!-- claude-guidance:end -->
1. In the guidance folder, read _START_HERE.md, _INDEX.md and rules/00_COMMON_RULES.md. Then read the other rules that fit this
   project and tell me which ones you picked and why. For a personal project, also read
   ~/.claude/MACHINES.md if it exists (machine facts, kept outside this folder).
2. If there's no CLAUDE.md in this project, copy templates/CLAUDE.template.md here as CLAUDE.md. If there
   is one, don't overwrite it: add the template's sections under a "Project" heading. Fill in the project
   block from what I wrote above, delete the pointers that don't apply, and leave anything you don't know
   as <TBD>. Don't guess.
3. Work job only: copy templates/SOURCE_REGISTER.md and templates/OPEN_ISSUES.md into docs/ and create an
   empty deliverables/ folder. Don't create anything until I say OK.
4. List the files and folders already here (outside the guidance folder) by name only. Don't open them
   yet. Ask me which are source of truth, which are WIP and which you must not open. For firmware, also
   ask which board, core/FQBN or env, and port. For server work, which host.
5. Don't start real work yet. Show me the filled-in CLAUDE.md and a short list of what's still <TBD>.
```

## B4. Then work normally
Claude reads `CLAUDE.md` at the start of every session in that folder, so the kickoff is one-time. Start each task
with a plain request. When a project teaches something worth keeping, ask Claude to **leave a note in
`_FEEDBACK/`** (rule 00 §8). A maintainer session folds it in (`_INDEX.md` "Keeping it up to date").

## Working with Claude Code: the basics
- **Permission prompts:** read what it wants to run before you click Yes.
- **Keep live things closed to Claude:** the live PLC project, the real library, a device's boot partition. Point
  it at copies or dry runs (rule 00 §2, rule 30 §7).
- **`@file`** attaches a file; selected text in the editor is visible to Claude.
- **New conversation per topic** (the **+** button).
- **Memory is per folder.** Lessons carry over only through this guidance folder.

## Troubleshooting
| Problem | Fix |
|---|---|
| Claude doesn't follow the rules | `CLAUDE.md` must be in the folder you opened, and must point at this guidance folder |
| No serial port for a board | Rule 60 §5 (cable, `dialout`, `brltty`, BOOT button) |
| `.md` opens in a rich editor | Office Viewer took it over; see A2 |
| Claude Code can't find Git Bash (Windows) | Set `CLAUDE_CODE_GIT_BASH_PATH` to `bash.exe` and restart VS Code |
