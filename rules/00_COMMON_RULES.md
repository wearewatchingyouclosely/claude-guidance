# 00 — Common rules (every project)

## 1. Sources of truth
- **Before reviewing any document, ask the user whether it is a Source of Truth or WIP/ad hoc.**
  - Record the answer in `docs/SOURCE_REGISTER.md`.
  - Don't open, summarise or take facts from a document that hasn't been classified.
  - Subagents can't ask the user. If a document they need isn't in the register, they stop and report back.
- Split the truth by what it is truth *for*. Typical splits:
  - **Behaviour:** the original program.
  - **Intent:** the functional and design specs.
  - **Interface:** the register map, at the version the user names.
  - **I/O:** the schematics, not a list someone typed from them.
  - **Layout and text:** the original screens.
- **When sources disagree, don't pick a winner silently.** Log it in `docs/OPEN_ISSUES.md` and tell the user.
- When the user corrects a source (for example "v3 is the truth, not v2"), update the register straight away.
- **Cite sources** in anything you write, e.g. `[FRS §4.2]` or `[LAD7 R12]`. Mark a fact *verified* only if you checked it against the source of truth in this session.
- **Check timestamps** on exports and generated folders. Exporters often leave old files behind, so a deleted item's file can still be there. Ignore files much older than the newest one in the folder.

## 2. Hands off the live thing
- **Never open or change the live project, controller program or production data.**
  - Work on a folder copy, made while the owning application has the project closed.
  - Name the exact copy any finding comes from. Copies often keep the original file name, so name them by folder ("the copy in `TestCopies\Copy3`").
- **Deliver changes as files for the user to apply.** Never apply them yourself.
- **A one-time exception covers that occasion only.** For example, "apply it tonight, I'm going to bed". In that case:
  - Back up first.
  - Test on a copy first.
  - The rule stands again afterwards.
- Never edit an original backup or export in place.
- **Before deleting or overwriting anything, look at it first.** Rename or copy it aside rather than destroy it when you're unsure. For example, a destination folder may hold uncommitted work from months ago.

## 3. Deliverables (the deliverable style)
The deliverables folder is the only place where work lands. Scratch work goes in the session scratchpad.

**One folder per piece of work: `deliverables\YYYY-MM-DD_TOPIC\`**
- The date is the day the work started.
- TOPIC is in capitals with underscores, e.g. `2026-01-15_ALARM_ACK`.

Typical layout:

| Path | What |
|---|---|
| `README.md` | Status block, what and why, how to apply (step by step), what to check afterwards, what's still manual, rollback |
| `build.py` (or `_tools\build.py`) | Regenerates every output from the base. Rerun it; never hand-patch outputs |
| `base_*\` | The input the build started from. The README names its date and source |
| `orig\` | Unedited copies of modified files, for diff and rollback |
| `work_*\` | Edited copies the build produces |
| `import\` | Exactly what the user runs or imports, and nothing else: no README, script or log inside it |
| `data\*.csv`, `changelog.tsv` | Evidence and the per-edit change list |
| `logs\` | Test-import and compile logs from the test copy |

**README rules** (template: [templates/DELIVERABLE_README.md](../templates/DELIVERABLE_README.md)):
- **A status block at the top**, with one dated line per event:
  - built from which base;
  - tested on which copy, with error and warning counts;
  - applied by the user, or not;
  - superseded by what.
- **A table of what changed**: file, change, and the source it comes from (e.g. original rung).
- **Install steps** that say exactly which button to press and which folder to pick, the result line to expect, and the errors and warnings to expect.
- **"Check afterwards"**: concrete test steps on the real system, with the expected value of each signal.
- **"Watch out"**: interactions with other packages, e.g. "importing package X after this one removes the network this one adds".
- Write it for the person applying it: short sentences, imperative steps, no internal reasoning.

**Revisions don't overwrite:**
- A changed approach becomes `build_v2.py` / `import_v2\` beside the original. The README says which one is current.
- Follow-up work after a package was applied gets a **new dated folder** that links back to the earlier one.
- Exception: a living plan or tracking document that the user asks you to keep current is updated in place, with a status table at its top.

**Before handing anything over:**
- Test it on a copy. Read every generated file you deliver, including all generated code.
- State its status plainly: *built*, *tested on a copy*, *compiled*, *applied by the user*. Never round "built" up to "done".
- If the test run modified the package (a manifest, a log folder), rebuild it before handing it over.

**Before starting**, check `deliverables\` for earlier work on the same topic, and build on it rather than re-deriving it.

**Quoting a fix** *(seen once)*: when the user wants to quote work rather than do it, deliver two question lists in one dated folder:
- **client questions:** plain, numbered for easy reply, each with a one-line "why we ask", and no internal speculation, so the list can be sent as is;
- **internal questions:** tools and licences, approach per item, risks and quote structure, each saying what it affects in the price, with citations to the evidence.

Add a README that summarises what is already known per item and the order to do things in (e.g. remove the biggest unknowns before sending).
Building the quote itself (costing, the letter) is outside this guidance: stop at the question lists and tell the user.

## 4. Structure and style of the work itself
- **Preserve behaviour.** A port is a port, not a redesign. A difference is allowed only when the user has approved it.
- **Don't create new top-level units without asking.** That covers blocks, modules, services and DB tables. Put new logic in the existing place that mirrors the original. If something new seems necessary, ask; the user will say how they want it.
- **Keep code simple.** Use plain conversions, one line per signal, and no defensive wrappers. Add a clamp or guard only where a value can realistically go out of range or become NaN, and say why in one line.
- **Keep original names** where other systems, documents or people refer to them.
- **The user prefers tool-driven updates** (import files, generated sources, scripts) over hand edits in an editor.

## 5. Communication
- Give concise status summaries. Confirm the direction in small steps before a big build.
- Ask only when the decision is the user's to make. Otherwise pick the conventional option, say so, and go on.
- When something goes wrong, say what, show the output, and say what you did about it.
- **Print mappings and key tables in chat** so the user can check them before importing.
- Give file references as links the editor can open.

## 6. Memory and hand-offs
- Before ending a session, leave notes in memory: what was done, what's applied or not, and what's next.
- **Memory points at the deliverable path** rather than repeating its contents.
- Write user rules down the moment they're given, with the reason. A rule without its reason gets misapplied.
- A hand-off to another session (e.g. a tool problem found during a job) is a deliverable folder with a README, not a chat message. See section 50 §6.

## 7. Office files without Office
Assume no Microsoft Excel is installed: spreadsheets open in OpenOffice/LibreOffice Calc. Generated `.xlsx` must look right there:
- no Excel-only features;
- check column widths and frozen panes;
- render a preview before handing it over.

Some users don't want workbooks as deliverables at all. Ask once and record the answer.

**Printer-friendly copies (2-up and similar)** *(seen once)*. Don't use Word's or the printer driver's "pages per
sheet" for a 2-up print: Word lays the document out again, shrinks the text and leaves a blank band under each page
(measured: about 45% of each half-page used). Build the 2-up PDF instead:
1. Export the document to PDF without changing it: Word COM opened read-only (`Documents.Open(path, $false, $true)`,
   `ExportAsFixedFormat(out, 17)`), or `soffice --headless --convert-to pdf` where Word isn't installed. Check the page
   count matches the document.
2. With PyMuPDF, take the union of the content extents of all pages (text blocks, images, drawings) plus a few points
   of padding, and use that one clip on every page, so every page gets the same scale.
3. Place two clipped pages side by side on each Letter landscape sheet (`show_pdf_page`; about 18 pt outer margin and
   18 pt gap, and a 14 pt footer strip). Add "Page N of M" under each half and a thin grey divider at the middle.
4. Render one sheet to PNG and look at it before handing it over. Tell the user to print at Actual size / 100%, one
   page per sheet, with the driver's 2-up off.

Never change the source document. Write the output next to the user's file or in the deliverables folder, under a
new name.

## 8. Feedback for the guidance
When a session finds something this folder gets wrong or misses (a rule that didn't work, a tool or kit that changed, a
lesson worth keeping), **don't edit the guidance**: not the workspace copy and not the master. Leave a note instead:
- **Where:** the feedback inbox named in the workspace's `CLAUDE.md`. Default: the master copy's `_FEEDBACK/`,
  `~/Documents/scriptKiddy/claude guidance/_FEEDBACK/`.
  If it isn't reachable, write the note to `docs/GUIDANCE_FEEDBACK.md` in the workspace and tell the user.
- **One file per item**, named `YYYY-MM-DD_<area>_<topic>.md` (`<area>` is `project`, `esp`, `linux` or `app`), in the format the inbox's `README.md` gives.
- **Generic only** (section 40): no job numbers, customer, site or machine names, tags or paths. The inbox is read by
  sessions for every other job.
- Tell the user you left it, with its path.

Only a maintainer session, working on the master copy, turns notes into rules (`_INDEX.md` "Keeping it up to date").
