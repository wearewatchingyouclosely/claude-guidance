# <Topic in plain words> YYYY-MM-DD

**Status**
- YYYY-MM-DD HH:MM built from `<base export / input, with its date>`.
- YYYY-MM-DD tested on `<exact copy path>`: <n> errors, <n> warnings (<what each warning is>).
- <not applied> / YYYY-MM-DD applied by the user / superseded by `<YYYY-MM-DD_OTHER>`.

<One paragraph: what this fixes or adds and why, in the reader's terms. Name the base it was built from,
and how to rebuild it: `python _tools\build.py "<base>"`. Say what it does NOT touch (no new blocks, no
other files changed).>

## What's in `import\`
| File | Change | Source |
|---|---|---|
| `<group>\<file>` | <what changed, in one or two sentences> | <original rung / spec section> |

<Anything deliberately left as it is, and whose decision that was.>

## Checked offline
- <truth-table / diff / well-formed checks, with results>

## Install
1. <What not to change before importing.>
2. Close the project. In <tool vX.Y.Z>, run **<button>** on `import\`.
3. Expect: `<exact result line>`. <Compile errors/warnings to expect, if any.>
4. <Download / reinitialise needed or not.>

## Check afterwards
- **<behaviour 1>:** <how to trigger it>. Expect `<signal>` = <value>, then <…>.
- **<behaviour 2>:** …

## Watch out
- <Interaction with other packages, the order they must be applied in, rebuild instructions.>

## Still manual
- <Anything the package can't do, as exact steps.>

## Rollback
- <Restore the archive taken before importing, or reimport `orig\`.>
