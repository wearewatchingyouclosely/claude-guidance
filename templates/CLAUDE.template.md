# <PROJECT NUMBER> — <short name> — <one line: what this workspace is>

<!-- PROJECT BLOCK: fill this in. Delete the section pointers that don't apply. -->

**What:** <machine / app / tool, and what the job is: port, new build, fix, commissioning support>.
**From → to:** <e.g. "AB SLC 5/05 (RSLogix 500) → S7-1516 / TIA Portal V20, WinCC RT Advanced", "WPF .NET 4.8 desktop tool", or "CYD 2.4R, arduino-cli, esp32 core 2.0.10">.
**The user:** <role>. <Port, not re-spec / new design / ...>.

## Rules that apply here
Read these from `rules/` in the guidance folder: a copy inside this workspace if there is one, otherwise the folder
registered in `~/.claude/CLAUDE.md`. Don't write its absolute path here, so this file still works if it moves:
- `00_COMMON_RULES.md`: always.
- `10_TIA_PORTAL_PLC_PROJECTS.md`: TIA Portal work. The tools (TIA Portal Tool, FTView Decompiler) are in `plc tools/` in the guidance folder.
- `20_OTHER_PLC_PROJECTS.md`: other PLC/HMI platforms (incl. Rockwell Logix and AVEVA System Platform), and ports in general.
- `21_CODESYS_PROJECTS.md`: CODESYS V3.5 projects (read 20 first).
- `30_APP_DEVELOPMENT.md`: tool and app repos.
- `35_WEB_APPS.md`: web sites, local web GUIs, device panels.
- `31_STYLEGUIDE_EXE.md`: desktop exe (WPF) look and layout.
- `32_STYLEGUIDE_HTML.md`: generated HTML pages.
- `40_DATA_SANITIZATION.md`: anything shared beyond this job.
- `50_BRANCHES_AND_VERSION_CONTROL.md`: any git repo.
- `60_ESP32_ARDUINO.md`: ESP32/Arduino/PlatformIO/ESP-IDF firmware. Agents: `agents/` in the guidance folder.
- `70_LINUX_HOME_SERVER_AND_DEVICES.md`: Linux desktop, home server, SBCs, Android over adb.
- `~/.claude/MACHINES.md`: this PC's machines and toolchains, if it exists (personal projects only; never copied into a workspace).

The rules in this file override the guidance where they differ.

## Read first
1. `docs/SOURCE_REGISTER.md`: every source, its classification, and what has been verified.
2. `docs/OPEN_ISSUES.md`: conflicts between sources and open questions.
3. <overview / pain points / interface docs, once written>

## Where things are
| What | Path |
|---|---|
| This workspace | `<path>` |
| Shared project folder | `<path>` |
| Live project (**do not open or edit**) | `<path>` |
| Test copies | `<path>` |
| Latest export | `<path>` |
| Deliverables | `deliverables\YYYY-MM-DD_TOPIC\` |
| Tools used (release folders, not dev folders) | `<path>` |
| Board / FQBN / core or env (firmware) | `<…>` |
| Host and SSH alias (server work) | `<…>` |
| Guidance feedback inbox (rule 00 §8) | `_FEEDBACK/` in the guidance folder |

## Sources of truth (confirm with the user, then keep in the register)
- Behaviour: <…>
- Intent: <…>
- Interface: <… at version …>
- I/O: <…>
- WIP, verify before use: <…>
- Do not open: <…>

## Job-specific rules
<!-- Rules the user gives for this job only, dated, each with its reason. -->
- 
