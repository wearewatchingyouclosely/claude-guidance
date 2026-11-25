# Logix comment kit

Two scripts for adding plain-language comments to an existing Studio 5000 / RSLogix 5000 project **without touching its logic**. The rules behind them are in [rules/20_OTHER_PLC_PROJECTS.md](../../rules/20_OTHER_PLC_PROJECTS.md) §7.

| File | What |
|---|---|
| `extract.py` | Dumps programs from `.L5X` exports to readable text: rungs with numbers, and SFC steps, actions and transitions sorted top-down. Read these dumps to write the comments. Diff two lines' dumps after normalising their prefixes |
| `build.py` | Builds the **Tools → Import → Tags and Logic Comments** CSV from comment tables. Checks every rung and SFC step against the export first, and refuses to build if anything has shifted |
| `example/` | A synthetic two-line example (made-up programs and tags) to try the kit on. Its `config.json` and `comments/` are the templates for a job |

**Status**
- 2026-11-13, started (*seen once*): the format was proven on a v20.05 project. Pilot import with Match by Rung Number = Yes gave 0 errors on every rung type and on SFC step descriptions.
- Not tested on other Studio 5000 versions, ST or FBD routines (rung comments are RLL only), or tag/member descriptions beyond SFC steps.

## Use
Copy the kit into the job's deliverable folder (e.g. `deliverables\YYYY-MM-DD_RUNG_COMMENTS\_tools\`). The job keeps the version it was built with.

1. Get exports from the **same** project you'll import into: one `.L5X` per program (right-click → Export Program) and **Tools → Export Tags and Logic Comments** (CSV). Put them in one folder.
2. Dump the programs:
   `python -I extract.py <exports> <deliverable>\data\dump <Program1> <Program2> ...`
3. Write the comments in `<deliverable>\comments\<SET>_rungs.tsv` (and `<SET>_steps.tsv` for SFC steps). Copy `example\comments\` as a start.
4. Write `<deliverable>\config.json`: the tag CSV name, and per set, the output file name and the programs with their placeholder values.
5. Build:
   `python -I build.py <exports> <deliverable>\config.json`
   Output: `<deliverable>\import\<output>` and `<deliverable>\data\changelog.tsv`.
6. Import into a **scratch copy** first. Use **Tools → Import → Tags and Logic Comments** with:
   - Overwrite/Discard Tags = **Discard**;
   - Import New Comments = Yes, Overwrite/Discard Comments = Overwrite;
   - Match by Rung Number = **Yes**.

   Expect 0 errors. Then import into the real target and save.

Try it on the example: `cd example` then `python -I ..\build.py exports config.json`.

## Comment tables (tab-separated, UTF-8 but ASCII text only)
`<SET>_rungs.tsv`

| Column | What |
|---|---|
| `routine`, `rung` | RLL routine name and rung number |
| `expect` | The start of the rung text, with placeholders. The build fails if the rung doesn't start with it. Keep it short: just enough to recognise the rung |
| `comment` | The comment, with placeholders |
| `note`, `note_for` | Optional. Text appended only for the programs listed in `note_for` (comma separated), e.g. a defect found on one line only |

`<SET>_steps.tsv`: `tag` (the SFC step array, e.g. `StepRunning`), `index`, `expect_stepnr` (the number the step action sets with `NewStepNr:=` or `StepIndex:=`), `comment`. Start each step comment with the step number.

Placeholders: `{KEY}` is replaced with the program's value for `KEY` in `config.json` (e.g. `{L}` → `L1`). Unknown keys are left as they are.

## Limits and cautions
- **Rung numbers must match the target project.** If anyone edits a routine after the export, re-export and rebuild. The `expect` check is what catches this.
- The build writes ASCII only. Non-ASCII text in a comment stops the build (`UnicodeEncodeError`) rather than writing something Studio 5000 may mangle.
- The step array's TAG row is copied unchanged from the tag export so its COMMENT rows have a parent. With Tags = Discard, the import doesn't overwrite it.
- OWNING_ELEMENT is filled with the rung's first instruction. It's only informative: with Match by Rung Number = No, most rows fail.
