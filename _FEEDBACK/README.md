# Guidance feedback inbox

Notes from Claude sessions (and people) about this guidance folder. Work sessions leave a note here instead of editing the
rules, so only one maintainer session changes the master at a time.

## Leaving a note (work session)
- **One file per item**, named `YYYY-MM-DD_<area>_<topic>.md`. `<area>` is `project` (PLC/work), `app`, `esp` or `linux`;
  `<topic>` is a few words in kebab case, e.g. `2026-12-01_esp_core3-ledc-on-s3.md`.
- **Never edit or delete another session's note.** If you have more on the same topic, write a new note that names it.
- **Generic only.** No job numbers or customer, site or machine names from work (rule 40). No secrets. Home device names
  are fine in `esp`/`linux` notes, but write the lesson as a rule.
- Format:

```markdown
# <one-line summary>

**Area:** project | app | esp | linux
**Kind:** rule wrong | rule missing | template or kit changed | tool bug | idea
**Where:** <file and section, e.g. rules/60_ESP32_ARDUINO.md §5>
**Seen:** once | <n> times

## What happened
<Generic description of the case, with numbers.>

## Suggested change
<The rule or fix, worded as it would go into the guidance.>
```

## Maintainer session
1. Read the root `_INDEX.md`, this file, and `rules/40`.
2. For each note, say what you'd change (file and section) or why you'd leave it, and wait for the user's OK.
3. Make the change, mark single-case lessons *seen once*, and add a dated change-log line to the root `_INDEX.md`.
4. Move the note to `_DONE/` with a last line: `**Done YYYY-MM-DD:** <what changed, or why not>`.
