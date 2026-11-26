# skills/: Anthropic's official Agent Skills (vendored)

Copied from [github.com/anthropics/skills](https://github.com/anthropics/skills), commit
`e4bb5d960d87126ff3b3a8af1a104b7db67560ba` (2026-11-16). Each folder keeps its own `LICENSE.txt` (Apache 2.0, or
the license text that folder ships with). Upstream's disclaimer applies: these are examples, so test them before you
rely on them.

A skill is a folder with a `SKILL.md`. Claude Code loads one on its own when your request matches the skill's
`description`, or when you name it ("use the xlsx skill to...").

## What's here
| Skill | Use it for | Rules |
|---|---|---|
| `docx` | Reading, writing and editing Word files, including tracked changes and templates | 00 (Office files) |
| `xlsx` | Spreadsheets: IO lists, tag exports, formulas, cleaning messy CSVs | 00, 10, 20 |
| `pptx` | Reading or building PowerPoint decks | 00 |
| `pdf` | Extracting text and tables, merging, splitting, filling forms, OCR | 00 (2-up PDFs) |
| `webapp-testing` | Driving a local web app with Playwright: screenshots, console logs, clicks | 35 |
| `frontend-design` | Giving a new page or UI a deliberate look instead of the default one | 32, 35 |
| `mcp-builder` | Writing an MCP server, so Claude can talk to a tool or service of yours | 30 §8 |
| `skill-creator` | Writing, testing and tuning your own skills | |

Not copied: the Anthropic-branded and marketing skills (brand-guidelines, internal-comms, slack-gif-creator,
algorithmic-art, canvas-design, theme-factory, web-artifacts-builder, doc-coauthoring, academy-guide,
discernment-nudge) and `claude-api`, which Claude Code already ships and which goes out of date quickly.

## Install
Claude Code reads skills from `~/.claude/skills/` (every project) and `<project>/.claude/skills/` (one project).

**Linux:** link them, so a `git pull` here updates them too:
```bash
mkdir -p ~/.claude/skills
for s in "<guidance>"/skills/*/; do ln -sfn "$s" ~/.claude/skills/"$(basename "$s")"; done
```

**Windows:** copy them (links need admin or Developer Mode):
```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills" | Out-Null
Get-ChildItem "<guidance>\skills" -Directory | Copy-Item -Destination "$env:USERPROFILE\.claude\skills" -Recurse -Force
```

Restart Claude Code, then ask it "which skills do you have?" to check they're listed.

**Instead of copying:** in Claude Code, `/plugin marketplace add anthropics/skills`, then
`/plugin install document-skills@anthropic-agent-skills` (docx, xlsx, pptx, pdf) or `example-skills@...` (the rest).
That route tracks upstream but installs everything in each set, the skills you don't want included.

The skills use these tools; Claude installs them when a task needs them, and each `SKILL.md` lists its own:
- Python: `openpyxl`, `pandas`, `pypdf`, `pdfplumber`, `python-pptx`, `markitdown`, `playwright`;
- Node: `docx` (docx-js) for writing Word files;
- **LibreOffice** (`soffice`), which docx, xlsx and pptx use to convert files and recalculate formulas. Install it
  (`sudo apt install libreoffice`, or the optional Windows step in `_START_HERE.md` A1).

## Changes from upstream
- `mcp-builder/reference/node_mcp_server_v2.md`: the sample address is now `john@example.com`, so the commit hook
  doesn't block it (rule 40 §5).

## Updating
Clone upstream to a temporary folder, copy the skills listed above over these folders, apply the changes above
again, update the commit hash at the top of this file, and add a line to the `_INDEX.md` change log.
