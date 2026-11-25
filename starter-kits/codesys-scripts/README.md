# CODESYS script kit

Headless scripts for reading a CODESYS V3.5 project as text, and for setting up its I/O from a table: the modules, the channel mappings and comments, one global tag list, and LD scan routines. The rules behind them are in [rules/21_CODESYS_PROJECTS.md](../../rules/21_CODESYS_PROJECTS.md).

**Status**
- 2026-11-12, started (*seen once*). Tested on CODESYS V3.5 SP22 Patch 3 with Scripting 4.2, on a scratch copy of a project with a Turck BL20 local I/O station, using `example/io_table.csv`. Results:
  - build: 0 errors, 0 warnings;
  - the export check passed;
  - a re-export with `export.ps1` checked again;
  - `apply.ps1` refused to overwrite without `-Force`;
  - a tampered table was caught by the check.
- Not tested: other vendors' I/O modules, `--keep-modules`, AO channels, or opening the result in the IDE by hand.

## Files
| File | Runs in | What |
|---|---|---|
| `run_codesys.ps1` | PowerShell (dot-sourced) | Starts `CODESYS.exe --noUI --runscript` correctly: paths in environment variables, no spaces, ProcessStartInfo, time-out |
| `export.ps1` + `cds_export.py` | PowerShell → CODESYS | Copies a project and exports the copy: `project_plcopen.xml` (everything, including LD, devices, mappings and tasks), `_tree.txt`, `src\*.st` |
| `make_io.py` | Python 3 | Reads the I/O table CSV and writes a build folder: `build_config.json`, the GVL `.st`, the LD POU XML (`ScanInputs`, plus `ScanOutputs` if any output has a global tag), `IO_List.md`. Its `--check` mode compares an export with the table |
| `apply.ps1` + `cds_apply.py` | PowerShell → CODESYS | Copies a template project and applies the build folder: deletes old objects, recreates the modules in table order, maps the channels, creates the GVL, imports the POUs, adds the task calls, builds, saves. Then exports and checks. Writes the output only if both pass |
| `example/io_table.csv` | | A three-module example (BL20 8DI, 8DO, 4AI-TC) with made-up tags |

Requirements:
- CODESYS V3.5 with the **CODESYS Scripting** add-on;
- Python 3 on PATH;
- a temp folder whose path has no spaces (the default 8.3 `%TEMP%` works).

The CODESYS path and profile default to V3.5 SP22 Patch 3 at the standard install path. Pass `-CodesysExe` / `-Profile` to change them.

## Use
```powershell
# 1. Read any project (works on a copy; the original is never opened)
powershell -ExecutionPolicy Bypass -File export.ps1 -Project "<x.project>" -Out "<folder>"

# 2. Set up I/O from a table
python -I make_io.py io_table.csv --out build --io-parent <I/O parent device name> --remove "<old GVL>,<old POU>"
powershell -ExecutionPolicy Bypass -File apply.ps1 -Template "<template.project>" -Build build -Output "<repo>\x.project" [-Force]
```
`make_io.py` options:

| Option | Default | Sets |
|---|---|---|
| `--gvl` | `Global_Tags` | GVL name |
| `--in-pou` | `ScanInputs` | Input POU name |
| `--out-pou` | `ScanOutputs` | Output POU name |
| `--task` | `MAIN_TASK` | Task that calls the POUs |
| `--keep-modules` | off | Map channels on modules already in the template, instead of recreating them |

Copy the kit into the job's repo (e.g. `tools\`) so the job keeps the version it was built with.

## The I/O table
One row per channel. The module columns repeat on each row, and modules are created in order of first appearance.

| Column | What |
|---|---|
| `slot`, `module_name` | Slot number (for comments) and the name the module gets in the device tree |
| `dev_type`, `dev_id`, `dev_version`, `module_id` | The module's identity. Find it in an export of a project that already has the module (`_tree.txt` shows `type=`, `id=`, `ver=` and `module=`), or in `C:\ProgramData\CODESYS\Devices\...\device.xml` |
| `kind`, `channel`, `param` | `DI`, `DO`, `AI` or `AO`; the channel number; the parameter name. If `param` is blank, `Input value Ch<n>` or `Output value Ch<n>` is used (the Turck naming; other vendors differ, so check an export) |
| `card_tag` | Variable created on the channel, e.g. `inp_PB_START` |
| `global_tag`, `data_type` | Tag in the GVL; leave it blank for spares. Inputs go card → global, outputs global → card. BOOL for DI/DO; `data_type` for AI/AO (default WORD) |
| `device`, `description`, `drawing` | Comment text: device tag, description, drawing sheet/line |

Generated LD:
- DI/DO channels get one network each: a contact driving a coil.
- AI/AO channels get a MOVE box.
- Each network title is the channel's comment.

## Limits and cautions
- **`apply.ps1` starts from the template every time.** Edits made in the IDE to the output are lost on a rebuild, which is why it needs `-Force` to overwrite. Once people edit the project by hand, stop rebuilding.
- With `rebuild_modules` (the default), **every module under the I/O parent is deleted and recreated**, which clears parameter changes made on those modules in the template. Use `--keep-modules` to keep them.
- Module parameters (e.g. TC type, AI range) are not set by the kit. Set them in the IDE, or extend `cds_apply.py`.
- The check reads module order from the PLCopen export, not from the device tree (rules/21 §4). Confirm the order by eye in the IDE once.
- Never point `apply.ps1` or `export.ps1` at the live project path for `-Output`. Both work on copies, but `-Output` is overwritten.
