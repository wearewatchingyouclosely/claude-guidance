# Claude guidance: index

> **For Claude and the maintainer.** People start with [README.md](README.md).

Working rules for Claude Code sessions. They combine three sources:
- **controls engineering:** PLC jobs, Windows tools, style guides, starter kits;
- **personal Linux and web projects:** home server, media tools, mod builders, Netlify sites;
- **ESP32 / Arduino firmware.**

Sessions read the rules so they don't have to learn them again. A session starts with [_START_HERE.md](_START_HERE.md).

The rules in `rules/` are generic. Machine and household facts are kept outside this folder
(`~/.claude/MACHINES.md` and each project's own notes), and job facts stay in the job's own workspace (rule 40).

## Folder layout
| Path | What |
|---|---|
| [_START_HERE.md](_START_HERE.md) | PC setup and the kickoff prompt for a new project |
| [README.md](README.md) | For people: what this folder is and how to use it |
| `_INDEX.md` | This file: index, sources, upkeep, change log |
| [rules/](rules/) | The rule sections, numbered. A project's `CLAUDE.md` points to the ones that apply |
| [templates/](templates/) | Files Claude copies into a workspace and fills in |
| [starter-kits/](starter-kits/) | WPF app, HTML page, CODESYS scripts and Logix comments kits (rules 21, 31, 32, 20 §7) |
| [agents/](agents/) | ESP32/Arduino subagent definitions (rule 60) |
| `setup/` | Windows installer (Ninite: Git, Notepad++, PuTTY, Python 3); see `_START_HERE.md` A1 |
| [tools/githooks/](tools/githooks/) | Commit hooks that block deny-listed words and e-mail addresses (rule 40 §5) |
| [_FEEDBACK/](_FEEDBACK/) | Inbox where work sessions leave lessons; `_DONE/` for handled ones |

## Rules
| File | Read it when |
|---|---|
| [00_COMMON_RULES.md](rules/00_COMMON_RULES.md) | Always. Sources of truth, hands off the live thing, the deliverable style, communication, memory, Office files and 2-up PDFs, feedback (§8) |
| [10_TIA_PORTAL_PLC_PROJECTS.md](rules/10_TIA_PORTAL_PLC_PROJECTS.md) | Siemens TIA Portal PLC/HMI work |
| [20_OTHER_PLC_PROJECTS.md](rules/20_OTHER_PLC_PROJECTS.md) | Other PLC/HMI platforms and ports in general: Rockwell Logix (§7), AVEVA System Platform (§8), RSLogix 500 (§9) |
| [21_CODESYS_PROJECTS.md](rules/21_CODESYS_PROJECTS.md) | CODESYS V3.5 (read 20 first) |
| [30_APP_DEVELOPMENT.md](rules/30_APP_DEVELOPMENT.md) | Any tool or app. §1–6 Windows portable .exe; **§7 personal Linux tools** (dry run / `--apply`, trash + undo, crash-safe jobs); **§8 API clients** |
| [35_WEB_APPS.md](rules/35_WEB_APPS.md) | **Any web app:** Netlify sites (layout, functions, Blobs, scheduled sync, secrets, admin pages, git hygiene), local tool GUIs (127.0.0.1, per-run token, path guards, job polling), device panels behind Caddy (forward_auth, PAM, signed cookies) |
| [31_STYLEGUIDE_EXE.md](rules/31_STYLEGUIDE_EXE.md) | WPF desktop look and layout |
| [32_STYLEGUIDE_HTML.md](rules/32_STYLEGUIDE_HTML.md) | Generated HTML viewers and reports |
| [40_DATA_SANITIZATION.md](rules/40_DATA_SANITIZATION.md) | Anything that leaves a workspace. **§7 secrets and personal projects** |
| [50_BRANCHES_AND_VERSION_CONTROL.md](rules/50_BRANCHES_AND_VERSION_CONTROL.md) | Any git repo |
| [60_ESP32_ARDUINO.md](rules/60_ESP32_ARDUINO.md) | ESP32/Arduino/PlatformIO/ESP-IDF firmware: local-library pattern, build and flash, `.bin` types, gotcha table, ports, wiring |
| [70_LINUX_HOME_SERVER_AND_DEVICES.md](rules/70_LINUX_HOME_SERVER_AND_DEVICES.md) | Linux desktop, home server, SBCs, Android over adb: SSH, root without sudo, disks, per-app VPN, *arr apps |

## Templates
| File | Use it when |
|---|---|
| [CLAUDE.template.md](templates/CLAUDE.template.md) | Starting a workspace: Claude copies it to the project root **as `CLAUDE.md`** and fills it in |
| [DELIVERABLE_README.md](templates/DELIVERABLE_README.md) | Starting a deliverable folder (rule 00 §3) |
| [SOURCE_REGISTER.md](templates/SOURCE_REGISTER.md), [OPEN_ISSUES.md](templates/OPEN_ISSUES.md) | Work job workspaces with several source documents |

The template is named `CLAUDE.template.md`, not `CLAUDE.md`, on purpose. Claude reads any `CLAUDE.md` it finds in a
folder it works in, and would take an unfilled template as instructions.

## Where this came from
Built on 2026-11-25 from three sets of notes:
- the work engineering guidance set (rules 00–50, templates, kits, hooks);
- notes from personal Linux, home-server and web projects;
- notes from ESP32/Arduino firmware projects.

Only generic lessons were carried over. Project names, paths, hosts, device details, measurements and secrets were
left in the projects they came from.

## Keeping it up to date
**Work sessions don't edit this folder.** They leave a note in [_FEEDBACK/](_FEEDBACK/) (rule 00 §8). A
**maintainer session** (opened on this folder) works through the inbox as its README says. When it adds a lesson:
- rules go in the matching file in `rules/`; machine facts never go in this folder;
- a lesson seen once is marked *seen once*;
- every change gets a dated line in the change log below;
- job text is never pasted in as is. Rewrite it first (rule 40).

Lessons for the **work** set (PLC, Windows tools) should also reach the SMB master's `_FEEDBACK\` as a `*_project_*`
note, so the Windows work copies get them. This folder doesn't sync back automatically.

## Change log
- 2026-11-25: removed company-specific setup before publishing.
- 2026-11-25: this index moved from `README.md` to `_INDEX.md`; `README.md` is now a page for people.
- 2026-11-25: new rule 35 web apps, from three hosted sites, four local tool GUIs and one device panel. Rule 30 §8 now
  covers API clients only and points to 35.
- 2026-11-25: sanitised. Removed project names, paths, hosts and measurements from rules 30/60/70, the agents and this
  README. Machine facts no longer live in this folder (rule 40 §7).
- 2026-11-25: first version. Merged the work engineering set (rules 00–50, templates, kits, hooks) with personal Linux/web
  and ESP32 knowledge. New: rule 30 §7 personal Linux
  tools and §8 web sites and API clients; rule 40 §7 secrets; rule 60 ESP32/Arduino; rule 70 Linux, home server and
  devices; `agents/` (six ESP agents); `_START_HERE.md` rewritten Linux-first; single
  feedback inbox with `project`/`app`/`esp`/`linux` areas. All new lessons from personal projects are *seen once*
  unless the rule says otherwise.
