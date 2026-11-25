# 20 — Other PLC projects

Any controller or HMI platform other than TIA Portal, for example Rockwell (RSLogix 500/5000, FactoryTalk View), Codesys-based platforms or Schneider. This also covers the platform-neutral half of any PLC-to-PLC port. The common rules (00) apply. For a port *into* TIA Portal, read section 10 as well.

## 1. What the job is
- A migration is a **platform port, not a re-spec.**
  - The original program is the behaviour truth. The specs are the intent truth.
  - If the two disagree, log it in OPEN_ISSUES and ask. Don't "fix" the original quietly.
- Before designing anything, write two short documents in the job workspace:
  - **Machine overview:** modes, sequences, safety chain, key signals.
  - **Pain-points list:** platform constructs that don't map one to one, counted from the original program.

  Agents and later sessions read these first.
- **Cross-check the drawings against the program before treating either as the I/O truth** *(seen once)*. List the I/O
  addresses the program uses and the ones the drawings show. Log every address that appears in only one of them in
  OPEN_ISSUES. Drawings can be years older than the program: whole slots in use but not drawn, and drawn points no
  longer used. Where a device's title on the drawing disagrees with what its circuit drives, describe what the
  circuit does and log the conflict.

## 2. Constructs that break in a port
Check every one of these in the original. They are the usual sources of silent behaviour change:
- **Word-packed bits:** a bit file used both as words and as bits, and a MOV into a word that sets bits elsewhere.
- **Indirect addressing:** `N[N7:x]:y`, `B3:40/[N7:10]`, and file-wide copies or fills (COP, FLL).
- **Timers:** time base, retentive (RTO) vs non-retentive, reset behaviour, preset taken from a setpoint vs a literal, and the accumulator read by other logic.
- **Edges and one-shots:** the edge memory must persist between scans; Temp memory doesn't.
- **Compares and maths:** operand order in subtractions, signed vs unsigned, integer division and overflow, scaling with clamping.
- **Scan model:** immediate I/O, interrupt routines, subroutine call order, and same-scan dependencies.
- **Latches and double coils:** one writer per output. Find every OTL/OTU and every duplicate OTE.
- **PID:** the instruction's form and units, setpoint and CV ownership, and manual/auto tracking.
- **Comms:** the register map, word and byte order, the scaling of each register, and who is client and who is server.

## 3. Reading the original
- Export the program as text: RSLogix 500 `.SLC` with its symbol file, Logix `.L5X`, PLCopen XML, or whatever the platform offers. Work from the text, never from screenshots.
- **FTView Decompiler**, for FactoryTalk View ME plus RSLogix 500: it turns the HMI export and the `.SLC` into one self-contained HTML page. You can click screens, read the ladder with cross-references and power flow, and jump between HMI tag and rung. Use it to answer "what drives this screen object" and "where is this bit used" without the original software.
- Keep a rung lookup script (`file + rung → text`) in the job's `tools\`, so citations are quick to check.
- PDFs: `pdftotext -layout`. State diagrams, interlock matrices and I/O pages extract badly, so read them as images.
- **CAD-plotted PDFs often have no text layer at all** *(seen once)*: `pdftotext` and PyMuPDF `get_text()` return
  nothing. Use PyMuPDF (`pip install pymupdf`): render each page at about 110 dpi to find the I/O sheets, then crop the
  I/O columns at 260–300 dpi (`page.get_pixmap(dpi=…, clip=rect)`) and read the crops as images. Record sheet, line and
  wire number for every point, so each row can be checked against the PDF.
  - Skip hatched or "not used" areas, but check whether their addresses are reused by active points drawn elsewhere.
    Keep the active use and note the hatched one.
- RSLogix 500 `.RSS` files can be triaged without RSLogix 500 (§9).

## 4. Delivering changes
- Use the target platform's own import format:
  - Logix: `.L5X` routines and rungs.
  - Codesys: PLCopen XML or `.export` files.
  - FactoryTalk: XML displays and tag CSVs.

  The deliverable rules in 00 §3 apply unchanged: dated folder, `build.py`, `import\`, a README with a status block.
- **Never build an import file from a guessed layout**, for any vendor format (tag CSVs, description databases,
  comment files). First ask the user to make one or two entries by hand on a copy, export them, and give you the file.
  Copy that layout exactly, keep the sample in the deliverable as evidence, and have the build check every generated row
  against it. Then pilot a few rows on a scratch copy, re-export and diff, before the full file. A layout built from
  memory got thrown away on two jobs (§7 Logix tag CSV, §9 RSLogix 500 database).
- Never make **online edits** or **downloads to a running controller**. Those are the user's to do. Deliver the file and the steps.
- Keep the original symbol and tag names where the HMI, DCS or documents use them. Tag names follow the P&ID: device type + number.

## 5. Testing without the machine
- Build a simulation layer that forces **raw inputs only**:
  - feedback follows the real command outputs;
  - analog values ramp;
  - drive feedback follows the run command.

  Never force outputs or derived status bits.
- Watch tables / trend lists follow the same format as section 10 §6: names only, organised by sequence step.
- Write test cases per mode, covering:
  - every sequence step;
  - skip-step, pause and resume;
  - restart after a fault;
  - retentive timer hold;
  - interlocks;
  - alarm and acknowledge behaviour, compared with the original's (e.g. "acknowledge = unlatch" vs a reset button).

## 6. Commissioning notes
- **Record every online finding in a dated deliverable** (`YYYY-MM-DD_EOD_ANALYSIS` or similar), with:
  - the evidence: trace, screenshot, watch values;
  - the suspected cause, with a citation;
  - the fix package, if any.
- **Drives:** check the motor data against the nameplate *and* the connection (star/delta, voltage) before tuning anything. A wrong rating looks like a control problem.
- **I/O faults:** check the hardware first (power to the card, wiring) before changing logic.

## 7. Rockwell Logix (RSLogix 5000 / Studio 5000) notes
All *seen once* (v20.05, one job, 2026-11), unless marked otherwise.

**Exports to ask for**
- One `.L5X` per program (right-click the program → Export Program). Include references and context; the export does that by default. Also ask for **Tools → Export Tags and Logic Comments** (CSV), plus a screenshot of the controller organizer for the task/program tree.
- **A program L5X also holds the AOIs and UDTs it uses** (`Use="Context"`). Count rungs only inside `<Program Use="Target" …>`. Counting the whole file can overstate rung counts by 3–15×.
- **Diff programs from the dump, not the raw XML.** Two programs that are copies of each other (e.g. one per line) show thousands of raw diff lines from SFC IDs and X/Y positions alone. Dump to text first (rung text; SFC steps, actions and transitions sorted by position), normalise the line prefixes, then diff.

**Bulk comments: the tag CSV (Tools → Import Tags and Logic Comments)**
Starter: [starter-kits/logix-comments/](../starter-kits/logix-comments/) dumps programs to text and builds the import CSV from comment tables, checking every rung first.
- Start the file with the export's own header lines (`remark,…` lines and the version line, e.g. `0.3`), copied as they are.
- The CSV carries tag descriptions, member/bit comments and **rung comments**. It never touches logic, which makes it the safe way to add comments to an existing project.
- Tag and member rows use the header `TYPE,SCOPE,NAME,DESCRIPTION,DATATYPE,SPECIFIER,ATTRIBUTES`:
  - top-level tag description: in the `TAG` row's DESCRIPTION. SCOPE is empty for controller tags and the program name for program tags;
  - member or bit comment: `COMMENT,<scope>,<base tag>,"text",,"<base tag>.<member path>"`.
- Rung comments sit at the end of the file, under **their own header**: `TYPE,SCOPE,ROUTINE,COMMENT,OWNING_ELEMENT,LOCATION`.
  - Row: `RCOMMENT,"<program>","<routine>","text","<owning element>","<rung number>"`.
  - OWNING_ELEMENT is the first instruction on the rung, without its `;`. In one export, an AOI call `Lib_Instr(a,b,c)` appeared as `Instr(a,b,c)` (the part after the last underscore), so don't assume it's a plain copy of the rung text.
  - **Import with "Match by Rung Number = Yes".** With No, the import matches each row on OWNING_ELEMENT. A guessed "first instruction" only matched rungs holding a single built-in instruction (`NOP()`, `JSR(...)`, a lone `MOV`); every multi-instruction rung and every AOI-call rung failed with "Rung or Element could not be found" (pilot, v20.05). Re-imported with Match by Rung Number = Yes, the same file gave 0 errors on every rung type, so OWNING_ELEMENT doesn't need to be exact in that mode. Matching by rung number needs the file built from an export that matches the target project, so the build should check each rung's text before it writes the row.
  - Import options also cover tags: set **Overwrite/Discard Tags = Discard** when the file carries TAG rows only as parents for COMMENT rows. Otherwise each one logs "Name collision: Tag … overwritten with imported definition".
  - **Before generating hundreds of rows**, get a sample export with one rung comment and one member comment added by hand, and copy its layout exactly. Then import a small pilot into a scratch copy, re-export, and diff it, before delivering the full file.
- SFC steps aren't rungs. Step descriptions come from the step tag's description: a `COMMENT,<program>,<array tag>,"text",,"<array tag>[n]"` row after the array's TAG row. This imported cleanly (pilot, v20.05). SFC text boxes can't be set from the CSV.
- Rung numbers shift if anyone edits the routine. Build the comment file from the export that matches the target project, and say which export in the README.

**PhaseManager programs**
- An equipment phase program has a fixed set of state routines (Running, Holding, Restarting, Aborting, often as SFC) plus RLL helpers (PrestateRoutine, Parameters, Alarms).
- **Hold behaviour usually lives outside the phase.** Besides the Holding routine, grep **every** program for `<phase>.Held` and `<phase>.Holding`. Device interlocks in the equipment programs that drop on those states are what stop pumps and valves. The phase's own step timer may already pause correctly (a retentive timer that isn't reset while the state isn't Running).
- Also check the unit procedure's Holding routine. It may hold some operations and **abort** the unit when none of them is running.
- Step numbers are set in the SFC step actions (`NewStepNr:=…` or `StepIndex:=…`). Write SFC step descriptions as `<step number> <what it does>`, so the SFC, the HMI and the comments line up.

**Auditing a Logix program**
- **Trace an HMI status value to the PLC formula before blaming the HMI.** For example, a unit procedure may build the HMI step number as `operation base + phase step - 1000`. Then read the HMI's mapping script for that value. Fix the side where the mismatch is.
- **Grep for disabled or forced logic and report it; don't remove it:** `XIC(AlwaysFalse)`-style disable bits, SFC transitions such as `x and 0` or `x or 1`, and mode bits latched every scan (e.g. an auto-step latch that makes manual stepping impossible).
- **Machines with one program set per line:** grep each line's programs for the *other* line's tag prefix. A copied program that still reads the other line's tags is a real defect, and easy to miss in review.
- **"A should behave like B" comparisons** *(seen once)*:
  - Confirm with the user whether "clone" means the same program or the same behaviour. If the programs aren't a port
    of each other (different platform or layout), compare behaviour (e.g. release and hold rules), not rungs, and log that.
  - If one program is still a PLC-5/SLC conversion (`B3[n].b`, `N7[n]`, routines named after data words) and the other
    uses named tags, derive an address → tag map from routines with matching structure, translate, then diff rung by
    rung. Keep the map and the diff in the deliverable. A raw diff is useless here.
  - **Compare tag values as well as logic:** timer presets (shown as `?` in rung text, visible only in the L5K/L5X tag
    data), setpoint and dimension tables, preset arrays. An uploaded program holds the running values. A 0 ms preset
    where the reference has 1 s was the main lead in one case.
  - Grep both for test and disable bits: `Toggle*`, `TEST*`, `AFI()`, conditioned rungs with only `NOP()`, and empty
    branch legs (`[X ,]`).

## 8. AVEVA / Wonderware System Platform HMI notes
*Seen once* (one job, 2026-11).
- An `.aaPKG` is a zip. Inside it is one `File1.cab`, which is itself a **zip** (not a Microsoft cab). That zip holds `Manifest.xml` (template and instance names, and `iasversion`, which is the System Platform version), one `.txt` per graphic symbol, and the base templates as `.aaPDF` (real MS cabs).
- A managed InTouch application (`$InTouchViewApp` instance) is in the package as `<id>.InTouch.txt`, another zip holding the whole InTouch app folder:
  - `win*.win` windows, with their QuickScripts as plain text;
  - `DB.CSV` (the DBDump tag database), `tagname.x`, recipe files and help files.

  Window scripts and tag definitions can be read without the IDE. Unzip to the scratchpad, never run anything from it.
- Strings in window scripts may be in the original integrator's language. Decode with the matching code page (e.g. GBK for Simplified Chinese, language ID 2052), not latin-1.
- A package may hold only one node's application (e.g. one line of two). Check which prefixes its scripts use before concluding anything about the other node. Ask for the **Galaxy backup** (`.cab` from the System Management Console) as the source of truth for the HMI.
- Identify installer media before relying on it: list the ISO with 7-Zip and check its date and `ReadMe`. A file name like "2014" doesn't say whether it is the R2 release.
- When printing decoded non-ASCII text from Python on Windows, set `PYTHONIOENCODING=utf-8`, or write to a UTF-8 file instead. The console code page raises `UnicodeEncodeError`.
- **Version rule:** an IDE can import packages from its own or an older version, never from a newer one. A package imported into a newer IDE is migrated and can't be taken back to the older site. Find out the site's System Platform version (`iasversion` in the manifest) and edit with that version, or deliver step-by-step edit instructions for whoever has it.

## 9. Rockwell RSLogix 500 (SLC 500 / MicroLogix) notes
*Seen once* (one job, 2026-11), unless marked otherwise.

**Reading an `.RSS` without RSLogix 500**
When only binary `.RSS` files are supplied, they can be triaged with Python `olefile` (`pip install olefile`):
- The `.RSS` is an OLE compound file. Each `<SECTION>/ObjectData` stream is a 16-byte header, then **zlib** data
  (`78 9C` at offset 16): decompress from offset 16.
- `MEM DATABASE` holds the address, symbol and description records: a length-prefixed address string (`I0001:000`,
  `T0004:039`, `PFILE:00019`, `DFILE:00007` style), a length-prefixed symbol, then length-prefixed description lines
  ending in a 0 byte.
- `PROGRAM FILES` holds the ladder as MFC-serialised objects (`CLadFile`, `CRung`, `CIns`). The operand strings
  (`I:1.0/5`, `T4:52`, `N7:12`) are readable; the instruction opcodes aren't decoded.
- `REVISION NOTES` holds dated revision lines.

Use it to triage: which revision has descriptions, which I/O each revision uses (for the drawings cross-check in §1),
and program-file names that show what template it was built from. It doesn't give readable rungs; for rung-level work,
ask for **File → Save As `.SLC`**.

**An uploaded program has no descriptions.** Before planning to re-describe a program, check older revisions and backups
for descriptions that can be carried over.

**Descriptions and symbols: Tools → Database → ASCII Export / Import**
The layout was confirmed against a real export (RSLogix 500, 155 rows). Still follow §4: get a hand-made sample from the
user's own version first.
- **No header line.** Plain ASCII, CRLF line ends, including the last line.
- **13 fields per row**, ending with a trailing comma:

  ```
  ADDRESS,0,SYMBOL,"DESC1","DESC2","DESC3","DESC4","DESC5",0,,,0,
  I:1/0,0,PB_START,"Start","Push","Button","","",0,,,0,
  S:1,0,,"Processor","Mode","Status/","Control","",0,,,0,
  DFILE:00007,0,,"Setpoints","","","","",0,,,0,
  ```

  (Example values, not from a job.) Fields 2, 9 and 12 were always `0`, and 10, 11 and 13 always empty.
- Address and symbol unquoted. All five description lines are always quoted, empty ones as `""`.
- Address forms: bits without the word number for I/O (`I:1/0`, `O:4/12`); status words and bits `S:3`, `S:1/15`;
  data-file titles `DFILE:00007`.
- Description lines up to **20 characters**, 5 lines. The longest line seen was 20; treat 20 as the limit.
- The export also writes every built-in `S:` (status file) description and the `DFILE:` titles, not only user entries
  (142 `S:` and 9 `DFILE:` rows against 4 user rows in the sample).
- The export run also wrote two files with the same name plus `1` and `3`, both empty (probably other sections, such as
  rung comments).
- **Not yet confirmed; get a sample before relying on it:**
  - data-table addresses (`N7:12`, `B3:0/5`, `T4:1`, `T4:1/DN`);
  - escaping of a comma or `"` inside a description;
  - the maximum symbol length.

**Building the import file**
- The build checks every row against the sample's pattern, plus line width, duplicate addresses and symbols, and the
  I/O card type per slot.
- Pilot three rows on a scratch copy first. Check that the built-in `S:` descriptions survive an import that doesn't
  list them.
