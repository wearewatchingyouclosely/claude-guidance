# PLC tools

Two portable Windows tools that go with the PLC rules. Each is a single `.exe` (.NET Framework 4.8, already on Windows
10/11): copy it anywhere and double-click it. Both also run headless for scripts and Claude sessions.

| Tool | What it does | Rules |
|---|---|---|
| `TiaPortalTool.exe` | Drives Siemens TIA Portal through Openness: export and import blocks and HMI screens, SLC 500 → TIA conversion, project texts | [10](../rules/10_TIA_PORTAL_PLC_PROJECTS.md) |
| `FTViewDecompiler.exe` | Turns a FactoryTalk View ME export and an RSLogix 500 program into one self-contained HTML viewer | [20 §3](../rules/20_OTHER_PLC_PROJECTS.md) |

The usage below is the tools' own help text from these builds. If a command here and the tool disagree, the tool is
right (FTView Decompiler has `--help`).

## TIA Portal Tool

**Needs:** TIA Portal with the matching **Openness** package installed, and your Windows account in the local group
**Siemens TIA Openness** (sign out and back in after adding it). The tool's start-up checklist says which of these is
missing. The first time a new build talks to TIA Portal, Openness asks you to approve it (a firewall prompt, then UAC);
approve it once per build. The SLC converter is tested with TIA Portal V20.

**GUI:** double-click it.

**Headless:**
```
TiaPortalTool.exe slc-import --slc <export.SLC> --out <folder> (--new <folder> <name> [--replace] | --existing <project.apNN>) [--1200] [--verify]
TiaPortalTool.exe new-project <dir> <name> [--1200]
TiaPortalTool.exe export-blocks <project.apNN> <export folder>
TiaPortalTool.exe import-folder <project.apNN> <folder> [--force] [--force-lost-objects] [--accept-layout-changes] [--save-with-errors] [--no-save]
TiaPortalTool.exe scl-export <project.apNN> <source.scl> <export folder>
TiaPortalTool.exe hmi-export <project.apNN> <export folder>
TiaPortalTool.exe hmi-import <project.apNN> <HMI export folder> [--force] [--force-lost-objects] [--accept-layout-changes] [--no-compile] [--no-save]
TiaPortalTool.exe hmi-runtime-names <pdata.fwc | RtData.plf | project.apNN> [--compile]
TiaPortalTool.exe hmi-probe <project.apNN> <out folder>        (lists device items and software; dumps a WinCC Unified HMI)
TiaPortalTool.exe hmi-item-diff <imported file.xml> <same object exported from TIA.xml>
TiaPortalTool.exe export-projecttexts <project.apNN> <out.projecttexts.xlsx> [source en-US] [target de-DE]
```

- **SLC converter (`slc-import`):** converts an RSLogix 500 ASCII export (`.SLC`, with its `.SY6` symbol file next to
  it for names and descriptions) into TIA blocks, imports them into a new or existing project and, with `--verify`,
  reads every converted rung back out of TIA and checks it against the original. Open `SLC_Verification.xlsx` after
  the run. The converted logic never touches real I/O: SLC inputs and outputs become tags in DBs `I1`/`O0`, and the
  HAL maps them to the hardware. Rungs it can't convert keep the original rung in the network comment.
- **Imports are guarded:** an import that would delete objects Openness can't export (alarm views, trend views) or
  change a screen's layout stops before saving. Override only on purpose: `--force-lost-objects`,
  `--accept-layout-changes`.
- **Always on a copy of the project** with TIA Portal closed on it (rule 10 §1), and export right before you build an
  import package.

## FTView Decompiler

**Needs:** nothing but the exports. No FactoryTalk or RSLogix install.

**Inputs:**
- **HMI:** the FTView ME displays exported as XML. In FTView Studio: *Graphics → Displays → select all → right-click →
  Export*, or *Tools → Graphics Import/Export Wizard*. Optionally the tag export (`.CSV`).
- **PLC:** the RSLogix 500 ASCII export (`.SLC`), with the symbol file (`.SY6`/`.SY5`/`.EAS`) of the same name next
  to it. Without the symbol file, the ladder shows bare addresses.

**GUI:** double-click it, then drop the export folder, `.SLC`, tag `.CSV` or symbol file anywhere on the window,
check the list on the right, and press **Generate**. It can copy the equivalent command line.

**Headless:**
```
FTViewDecompiler.exe --hmi <export folder> [--tags <tags.csv>] [--slc <program.slc>] [--sym <symbols .sy6/.eas>]
                     [--out <viewer.html>] [--title <text>] [--shortcut <name>]... [--no-images] [--no-languages] [--no-values]
```
Give `--hmi` and/or `--slc`. The result is one HTML file: every screen with its behaviour, and the ladder with
symbols, comments and cross-references, linked both ways. It opens in any browser and can be mailed.

## Updating
Replace the `.exe` with the new build, keep the file name, and update this page if the usage changed. A new TIA
Portal Tool build needs the Openness approval again.
