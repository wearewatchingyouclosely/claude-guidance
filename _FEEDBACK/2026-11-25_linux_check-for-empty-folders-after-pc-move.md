# After moving to a new PC, check for project folders that came over empty

**Area:** linux
**Kind:** rule missing
**Where:** rules/70_LINUX_HOME_SERVER_AND_DEVICES.md (new section), or _START_HERE.md Part A
**Seen:** once

## What happened
A projects folder was copied to a new PC. Seven of about twenty project folders arrived as empty directories, all
with the same timestamp (the copy time); their files existed only in the old PC's backup on a second drive. A later
session searched the home directory and the home server for one project's code, found nothing, and only found it
after the user named the backup drive. The backup drive (a 777-mode filesystem) also made every file show as a
mode change in `git status`.

## Suggested change
- When a project folder is unexpectedly empty, list its siblings with `find <dir> -maxdepth 1 -type d -empty` and
  compare timestamps: several empty folders with one shared timestamp means a failed copy, not deleted work. Ask the
  user where the backup is before searching further.
- Restore with `rsync -a --no-perms --chmod=D755,F644` (excluding venvs, `node_modules`, caches), then set the
  execute bit only on the scripts that need it. In a repo read straight from such a drive, use
  `git -c core.fileMode=false status`.
- Uncommitted work found in a backup goes on its own branch (`restore/<date>-wip`) before anything else (rule 50 §1).
