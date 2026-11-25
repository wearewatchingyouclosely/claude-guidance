# Agents

Claude Code subagent definitions for ESP32/Arduino work (rule 60), written so they don't name a machine or project.
Copy them into `<sketchbook>/.claude/agents/` (or any firmware folder's `.claude/agents/`) to use them. `<projects>`
means the folder holding your firmware projects, and "the reference project" means the most mature one in it, which
already follows the local-library pattern.

| Agent | Use for |
|---|---|
| `esp-firmware-developer` | Feature work, fixes, refactors and framework ports (copy, don't edit in place, for major ports) |
| `esp-build-verifier` | Compiling every sketch and checking that vendored `libraries/` are really used; flashes only when asked |
| `esp-project-scaffolder` | Setting up a new project folder with the local-library pattern |
| `esp-readme-writer` | Build/flash README: board, core, library table, commands, the gotchas actually met |
| `esp-user-guide-writer` | USER_GUIDE.md for the person holding the device |
| `esp-wiring-diagram-writer` | WIRING.md: a pin table and an SVG diagram; KiCad only when asked |

The agents assume two side-by-side cores, `arduino-cli` (2.x) and an `arduino-cli3` alias (3.x). Check what the machine
really has before relying on that.
