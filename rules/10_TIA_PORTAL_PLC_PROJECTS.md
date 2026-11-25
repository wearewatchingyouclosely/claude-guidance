# 10 — TIA Portal PLC projects

Siemens S7-1200/1500 programs and WinCC HMIs built or changed in TIA Portal, including migrations from
other platforms. The common rules (00) apply. This file adds the TIA specifics.

**Go deeper:** the TIA Portal Tool's `project-kit` on its **`public` branch** holds:
- a CLAUDE.md template;
- six agents: process expert, converter, TIA developer, HMI developer, sim/test engineer, migration reviewer;
- `docs/LESSONS_LEARNED.md`, with the technical gotchas: hand-port defects, scaling, DCS interfaces, scan model, alarms, WinCC import rules, texts, Openness, drives, commissioning;
- device-type hardware notes.

Copy it into every new TIA workspace:
`git -C <TIA_Portal_Tool> archive public project-kit | tar -x -C <workspace>`.

## 1. The TIA project itself
- **Never open (GUI or Openness) or change the live TIA project.**
  - Copy the project folder while TIA has it closed, and work on the copy.
  - Copies keep the same `.apNN` name, so name them by folder.
- A headless TIA instance can run on a copy while the user has the live project open in their own TIA. Watch the RAM: two instances plus a large project can run out of memory.
- **Export immediately before building a package.** Always start from an export of the target project, never from memory. Override imports put the *exported* XML back, so a package built on an old export reverts every TIA edit made since then.

## 2. How changes reach TIA (the import package)
A package is the `import\` (and `import_hmi\`) folder of a deliverable. A good one imports, compiles and saves in one run, with no hand steps in TIA.

- **Formats**, in order of preference:
  - SimaticML block XML, through the tool's **Import Folder**. This works for LAD and FBD, which can't come from SCL sources.
  - `*.scl` external sources, for SCL blocks.
  - `<Table>.tags.tsv`, for tags.
  - `SW.Types.*` XML, for UDTs.
  - The HMI export folder with its `hmi_manifest.json`.
  - Project-text `.xlsx`, for translations.
- **Ask whether ported ladder should stay LAD.** Usually it should, so deliver XML, not SCL.
- **No PLC tag import workbooks.** Use `.tags.tsv` instead. **Never use untagged absolute addresses**: TIA auto-creates junk `Tag_n` names for them.
- **Edit the export's own XML with `build.py`.** Keep the SimaticML structure TIA wrote. XML written by hand from scratch is the most common cause of import failures.
- **One package is one consistent change.** Ship together:
  - every block that changes;
  - every caller of a changed interface;
  - FBs with their instance DBs;
  - for a replacement, the old call taken out.

  Don't ship blocks that didn't change: each import overwrites the block.
- **Keep numbers and names stable.** Set `<AutoNumber>false` where the number matters, and keep file name = block name. Group folders match the TIA group names.
- **Match the target project:**
  - CPU family: S7-1200 has no `DBAccessibleFromWebserver`.
  - Languages: remove cultures the project doesn't have.
  - Library FB versions.
- **Never put an existing OB in a package.** Replacing an OB loses its process image and event links. Ship the new logic as an FC called from the OB, or as by-hand steps.
- **Nothing else in `import\`.** Clear the tool's `TIA_Portal_Tool_Logs\` before handing the package over.
- **Test on a copy before handing it over:**
  - Run headless `import-folder <copy> <folder> --no-save`, or a GUI import on the copy.
  - Expect 0 errors, and explain every warning.
  - When an import fails, read the **first** error only. The rest usually follow from it.
- **After any test import of an HMI package, rebuild it or restore its `hmi_manifest.json`.** The tool writes the test target's hashes into the package, so the next run reports "0 imported, N unchanged" and still says SUCCESS. Treat that line as a failure.
- If the target project already has compile errors, list them in the README and say whether the package fixes them.

## 3. The TIA Portal Tool
- Projects use the **release folder**: a detached worktree of the `public` branch with the release exe in its root. Never use the dev folder: its checked-out branch is tool development work.
- Headless commands always go through the Openness-approved runner:
  `<tool>\tools\runner\OpennessRunner.exe <tool>\TiaPortalTool.exe <command> ...`.
  Running `TiaPortalTool.exe` with arguments directly opens only the GUI.
- Useful commands (check the README of the version you run):
  - `export-blocks`, `hmi-export`, `hmi-import`;
  - `import-folder [--no-save] [--save-with-errors] [--force]`;
  - `export-projecttexts`;
  - `verify-folder`, `verify-export` (rung check of a hand port against the original);
  - `lint-export` (Temp edge memory, literal timer presets, double coils).
- A new exe build needs the Openness firewall approval again. The prompt comes about 2.5 minutes after TIA starts, then a UAC prompt. If the user isn't there to approve it, skip that step and say so.
- **A job session never edits the tool, its repo or the kit**, not even to fix a one-line bug. It writes a report folder `deliverables\YYYY-MM-DD_TOOL_<TOPIC>\README.md` (layout in section 50 §6). Until the fix is released, it works around the problem in its own deliverable and links to the report.

## 4. PLC code rules
- **No new blocks without asking.** Ported logic goes as networks in the existing blocks that mirror the original program files (INPUT, SCALING, OUTPUT and so on).
- **Preserve the original scan and call order**, and the command-word layering (mode commands → output transfer → OUTPUT). Hardware addresses live only in the INPUT/OUTPUT blocks.
- Comment every network with where it came from (`// LADn Rm`). Keep the original symbol names that the HMI, documents or DCS use.
- **Match units and behaviour exactly:**
  - timer bases, and minutes vs seconds;
  - retentive timers;
  - counter resets;
  - compare directions;
  - edge memory: never in Temp;
  - timer presets: never a literal where the original had a setpoint.
- Keep code simple (00 §4): `reg[0] := REAL_TO_INT(x);`, not a wrapper chain.

## 5. HMI (WinCC classic / RT Advanced)
- Openness leaves **alarm views and trend views** out of an HMI export, and doesn't report it. Importing the screen or template they're on deletes them. Check the export's runtime-only object list before importing a screen.
- Never re-import a template that holds an alarm view unless you've checked that list.
- HMI tag limits may not be enforced by the panel. Where a limit matters, clamp in the PLC too.
- HMI-driven bits (pushbuttons, login bits) can latch. Check that every bit the HMI sets is also reset (momentary Set/Reset), and that login/logout actually reaches the PLC.
- Translations: the original HMI's language export is the source of truth for text. Deliver translations through TIA's project-text xlsx importer.

## 6. Watch tables and simulation
- **A watch table deliverable is only the TIA Name column.**
  - One tag per line, with CRLF line ends.
  - `//` lines are section headers.
  - No address, type, format, comment column or tabs.
- **Sequence watch tables are organised by step**: a `// ==== STEP n - <description> ====` header, then every tag that step uses. Tags repeat across steps.
- **Simulation forces raw field inputs only.**
  - Never force outputs, or bits derived every scan: the force fights the recompute.
  - Make feedback follow the real command (`IF OP_x THEN fbk := TRUE ELSE fbk := FALSE`), always with the ELSE.
- A stateful sim FB is called once per scan. Gate it by mode instead of adding a second call.

## 7. Reviewing a hand port
- Use `verify-export` against the original program and read the Expected/Actual columns before calling anything a bug. Literal presets, setpoint FB calls and `.PT`/`.ET` temps explain many mismatches.
- `verify-export` matches networks by RUNG titles. Keep them; restore them if an edit dropped them.
- Run `lint-export` on the original's conversion too. Findings that appear in both came from the original program.
