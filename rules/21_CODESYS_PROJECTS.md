# 21 — CODESYS projects

CODESYS V3.5-based controllers (vendor PLCs that use the CODESYS runtime and IDE). Read section 20 first; this file adds the CODESYS specifics. The common rules (00) apply.

**Scripts:** [starter-kits/codesys-scripts/](../starter-kits/codesys-scripts/) does §2, §3, §5, §6 and §7: headless runner, export, table-driven I/O setup with LD scan routines, and the export check.

Everything here was *seen once* (one job, CODESYS V3.5 SP22 Patch 3, Scripting add-on 4.2, a Turck BL20 programmable gateway with local I/O). Check it on your version before relying on it, and remove the *seen once* mark when a second job confirms it.

## 1. The project file
- `.project` is a binary file. You can't read or diff it as text. Read it through an **export** (§3), never from screenshots.
- **Never open or save the live project from a script.** Copy it and work on the copy. The rules in 00 and 20 §4 apply.
- A headless CODESYS instance can run on a copy while the user has the original open in the IDE. *Seen once.*
- Files next to the project that aren't the project (ignore them in git and when copying): `*.opt` (per-user settings), `*.precompilecache`, `*.compileinfo`, `*.bootinfo`, `*.bootinfo_guids`. A `.projectarchive` is a zip of the project plus libraries and devices.

## 2. Running CODESYS headless (Scripting add-on)
- The **CODESYS Scripting** add-on must be installed on the PC (CODESYS Installer → add-ons). Scripts are IronPython 2.7.
- Command:
  `CODESYS.exe --profile="<profile name>" --noUI --runscript="<script.py>"`
  - The profile name is the one shown in the IDE's title bar, e.g. `CODESYS V3.5 SP22 Patch 3`.
  - `CODESYS.exe` is under `<install>\CODESYS\Common\`.
- **Paths with spaces break `--runscript` and `--scriptargs`.** *Seen once.* To work around it:
  - copy the script and the project into a folder with no spaces (the user's temp folder in its 8.3 form works);
  - pass every path to the script in **environment variables**, not as arguments.
- From PowerShell, start it with `System.Diagnostics.ProcessStartInfo` (`UseShellExecute = false`, `EnvironmentVariables[...]`, `WaitForExit(timeout)`). Plain `&` / `Start-Process` mangled the quoting.
- The script writes its own log file. CODESYS's console output is not a reliable record. End the log with an explicit `RESULT: OK` line that the caller checks.
- Expect harmless noise: "Application Composer: no valid license", "No Offline Help installed".

## 3. Reading a project: the export
Write one export script per job, or take one from an earlier job, and run it on a copy. It should write:
- **PLCopen XML** of the whole project: `proj.export_xml(proj.get_children(False), path, True)`. This is the only place **graphical POUs** (LD, FBD, CFC) appear as text.

  The export also holds the **device configuration**:
  - every I/O channel with its mapped variable (`<Mapping>`);
  - module parameters;
  - Modbus/fieldbus channel setup;
  - the task configuration with its POU calls (`<pouInstance>`).

  It does **not** hold channel comments or IEC addresses.
- **Tree dump:** name, type GUID and device identification per object.
- **ST text:** for objects with a textual declaration or implementation.

Re-export after every user save before reasoning about the code. Commit the export next to the binary project, so that git diffs are readable.

## 4. Scripting API notes *(seen once)*
- **`dir()` returns nothing useful** on script objects. Find out what works by trying each candidate call inside `try/except` and logging which signature succeeded.
- **Hardware modules.** Look up module names, ModuleIds and the meaning of enum parameters in the installed device descriptions: `C:\ProgramData\CODESYS\Devices\<type>\<id>\<version>\device.xml`. For example, a TC module's "type 0" is type K. Read them there instead of guessing.
- **Adding modules:**
  - `parent.insert(name, index, type, id, version, module_id)` appends at `index`.
  - `parent.add(...)` put the module at the **top** of the tree.
  - After a reopen, `get_children()` did not return the insertion order. Check module order in the PLCopen export, or by eye in the IDE.
- **I/O channels:** loop over `device.connectors[n].host_parameters`.
  - `p.visible_name` is e.g. "Input value Ch1".
  - `p.io_mapping.variable = "name"` creates and maps a variable.
  - `p.user_comment = "..."` sets the Description column. `p.description` is read-only.
- **GVL:** `app.create_gvl(name)`, then `gvl.textual_declaration.replace(text)`.
- **Task call:** `task.pous.add("POU_NAME")` appends. `task.pous.insert(index, "POU_NAME")` puts it at a position; use that when a new POU has to run between existing ones. Removing a call from a script did not work: `remove(name)` did nothing, and `remove(index)` raised.
  - Iterating `task.pous` gives the called POU names. `task.pous[i]` gives a `(name, '')` tuple.
- **DUTs and POUs:** `app.create_dut(name, DutType.Structure)` and `app.create_pou(name, PouType.FunctionBlock)`, then `.textual_declaration.replace()` / `.textual_implementation.replace()`. For persistent variables use `app.create_persistentvars(name)`: a PERSISTENT section in a normal GVL gave warning C244.
- **Struct inheritance:** `TYPE B EXTENDS A : STRUCT … END_STRUCT END_TYPE` compiles. A variable of type B can be passed to an FB input of type A. That lets a generic FB take a richer settings struct.
- **Build and messages:**
  - `app.build()` runs the build.
  - Read the messages with `system.get_message_categories(True)` and `system.get_message_objects(cat)`; each has `.severity` and `.text`.
- **Import:** `app.import_xml(path)` imports a PLCopen XML file (POUs and GVLs) into the application.

## 5. Writing ladder (LD) as PLCopen XML *(seen once)*
CODESYS accepts LD through a PLCopen import, but **a wrong layout imports with no error and loses content**. Always do the round trip: import, export, then count networks, elements and variables.
- **One `leftPowerRail` (localId 0) for the whole POU.** Every network's first element connects to it. A `rightPowerRail` at the end.
- **Each network** is:
  - a `comment` (the network comment);
  - a `vendorElement` whose `ElementType` is `networktitle`;
  - its elements.

  localIds are unique across the whole POU. A left rail per network imported only the first network.
- **Contact and coil:** `<contact><connectionPointIn><connection refLocalId="0"/>…<variable>x</variable>`, then a `<coil>` connected to the contact.
- **Operator boxes (e.g. MOVE):**
  - `<block typeName="MOVE">` with inputs `EN` (from the rail) and `In2` (from an `inVariable`);
  - outputs `ENO`, and `Out1` with the destination as `<connectionPointOut><expression>dest</expression>`;
  - addData `CallType` = `operator`.

  Without `ENO`, the Out1 assignment was dropped. An `outVariable` wired to Out1 broke the POU.
- **Comparison boxes (GE, LE, …) with EN** are stored as `EN`, `In2`, `In3` → `ENO`, `Out2`, whatever input names you import. Generate them that way so the round trip compares cleanly.
- **Parallel branches** must share a non-rail element, e.g. a box's `ENO`. Two branches that share only the left rail become two networks.
  - **The IDE can draw a rung the import cannot rebuild.** In the LD editor you can put two boxes on parallel branches straight off the left rail (e.g. a compare box on top, an FB call below). CODESYS exports that with both boxes' `EN` wired to the rail, and nothing else joining them.
  - The only trace of the branch is in the `rightPowerRail`: one `<connection refLocalId="<box>" formalParameter="">` per branch-end box, each with addData `http://www.3s-software.com/plcopenxml/ldbranchid` → `<BranchId>n</BranchId>` (n just counts up through the POU). A normal rung lists only its last box there. CODESYS fills this list in on import, so a generator can leave it empty.
  - **Importing that exact structure, right-rail list included, still splits every such rung into one network per branch.** The build shows 0 errors; only the network-count check catches it. *(Seen once, CODESYS V3.5 SP22 Patch 3.)*
  - So if the user wants this layout in a generated POU, you can't generate it. Agree on one of these: a shared start element, a join into a shared element, one network per box, or hand-drawing in the IDE (then the POU is no longer generated).
- **BOOL pins on a box depend on whether the box has EN:**
  - On a box **with EN**, every input pin, BOOL ones too, is stored as an `inVariable`. **An OR-join of two contacts into such a pin imports with one contact silently dropped, and the build still shows 0 errors.** Only the element-count check caught it. Do the OR inside the block (two inputs), or in a separate rung.
  - On an FB called **without** EN (the rung enters on its first BOOL input), CODESYS draws the other BOOL pins as contacts on the left rail. Generate them as contacts.
- Copy the structure from an export of a real POU whenever you can. It beats any description. But an export is not proof that the import will accept the structure (see parallel branches above), so round-trip the copied structure before you build a generator on it.

## 6. Building and checking
- **A POU that no task calls is not compiled.** A clean build says nothing about it. Add the call (§4) before trusting a build.
- Pass criterion for a scripted change:
  - the CODESYS build shows 0 errors (and the warnings are read);
  - a re-export matches what was meant: module order, mappings, network count and variables, task calls, GVL contents.

  Check it with a script, not by eye.
- Check the application name in the build output. `<device>.Sim.<app>` means **simulation mode is on**. That's fine offline; turn it off before a download.
- **Prove the checker.** To check that something compiles, also add a deliberate error on the task as a control. If the control doesn't show up, the code wasn't compiled.

## 6a. Simulation test (optional) *(seen once)*
A script can log in to the CODESYS simulation of a **copy** of the project, write values, let the task scan, and read results back. It's a scripted version of going online and forcing values in a watch list.
- **API:**
  - `oa = online.create_online_application(app)`, then `oa.login(OnlineChangeOption.Try, True)` and `oa.start()`;
  - write with `oa.set_prepared_value("Global_Tags.X", "TRUE")` + `oa.write_prepared_values()`;
  - read with `oa.read_value("Global_Tags.X")`. There is no `Application.` prefix, and the result may carry a type prefix (`BOOL#TRUE`); strip it.
  - Let several task cycles pass after each write before reading.
- **Drive raw inputs only** (20 §5): a global SIM switch plus a table of simulated raw values, read by the input scan routine. Commands and settings may be written directly. Never force outputs or derived status bits.
- **The simulator's I/O cards read 0.** With SIM off, that's a free "no feedback ever arrives" case for fail-to-open/close tests. Keep any test that isn't about faults in SIM mode, or valves will time out and drop their outputs mid-test.
- **It is optional, not a build gate** (user preference on the first job). The required checks are §6: 0 build errors and the export check. Run the simulation test when the user asks, and offer it when a change touches logic it covers. Say in the changelog whether it ran.
- It doesn't test real I/O, the HMI, the LD layout in the editor, or timing beyond "within a few scans". Say so when you report it.

## 7. Generated projects
For a new build from a spec, it works well to keep:
- a **template** project (hardware tree, task, network, copied once);
- a **table** in code (I/O from the drawings, with a sheet/line citation per channel);
- a **build script**: template copy → apply → build → export → check → copy in only if the check passes.

Rules:
- **A rebuild from the template discards IDE edits.** Use it only for the first build, and say so in the repo README and the changelog.
- **After that, build in update mode** *(seen once)*. The script changes the current project, but only what the generator **owns**:
  - the channel mappings;
  - a marked GENERATED block in the global list;
  - the generated routines and their task calls.

  **Seeds** (types, FBs, the persistent settings table) are created only if missing, then belong to the user. Everything else is kept.
- **Safeguards** for update mode, each one refusing and changing nothing:
  - git must be clean;
  - the project must not be open in the IDE;
  - a **guard** compares the owned objects with a snapshot written by the last build, so a hand edit can't be overwritten. Report what changed, and allow an explicit override flag once the user understands it;
  - replacing a seed is allowed only if the project's copy still matches a version the generator once produced (git history). That covers the persistent table too: regenerate it from each committed version of the generator;
  - 0 build errors and the export check must pass before the result is copied in.
- **Commit before changing anything.** If the user edited in the IDE, export and commit that as their own commit first. Commit tooling separately from the project build.
- Try every tooling change in a scratch `git clone` first, then in the real repo.
- Once people edit by hand, the project is the source for everything the generator doesn't own.
- Generate the human-readable I/O list from the same table, so it can't drift.
- Put the project in a git repo:
  - a `CHANGELOG.md` entry per change set, saying what changed, how it was checked and what wasn't checked;
  - ignore the per-user and compile files (§1);
  - commit the text export.

## 8. I/O from the drawings
- Read the I/O pages as images (20 §3). Give each channel a sheet/line citation.
- **Check every device label against what the PLC channel actually drives.**
  - On one job, four labels were wrong: a TC tag typo, a solenoid labelled with the wrong unit number, a position sensor labelled with the other valve, and solenoids labelled as a different valve type.
  - Log each one as an open issue. Don't silently pick a side.
- Check that the module order and module types in the project match the drawing's slot order. A project built by hand can have the right modules in the wrong order.
- Note channels the spec relies on that the drawings leave unwired, for example a start key switch or an E-stop. These go to the customer, not into the program as guesses.
