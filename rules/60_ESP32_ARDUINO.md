# 60 — ESP32 / Arduino firmware

Hobby firmware for ESP32-class boards: CYD (Cheap Yellow Display) variants, ESP32-S3 devkits, M5Stack Cardputer /
Cardputer ADV / CoreS3, RP2040 boards. Arduino (`arduino-cli`), PlatformIO and ESP-IDF projects. The common rules (00)
apply. Agents for this work are in [../agents/](../agents/). Which cores and tools a given machine has installed
is a fact about that machine: check it, and keep it in the machine's own notes, not here.

## 1. Before touching a project
- **Read the project's README first.** It usually names the framework, core version, FQBN or env, partition scheme
  and the libraries that are vendored. Don't guess what's written down.
- **Work out the framework from the files**, not the folder name:
  - `.ino` in a folder of the same name → Arduino (`arduino-cli`).
  - `platformio.ini` at the root → PlatformIO (`pio run -e <env>`).
  - Top-level `CMakeLists.txt` + `main/` + `sdkconfig.defaults` → ESP-IDF (`idf.py`). A `platformio.ini` inside
    `main/` of an ESP-IDF project is only a component marker; ignore it. The entry point is `app_main()`.
- **Upstream clones** (Bruce, Marauder, Launcher, OEM demos) have their own `CLAUDE.md`/`AGENTS.md`/contributing
  rules. Those win inside that repo. Keep local patches small and marked (e.g. `// --- <fixName> ---` around each
  changed block) so they can be found and re-applied after an upstream update.
- **Check the core version the project targets.** ESP32 Arduino core 2.x and 3.x differ in real APIs (below). Never
  assume; if it's undocumented, try 2.x first and say so.

## 2. The local-library pattern
A project may vendor a **modified or pinned** library in its own `libraries/` folder so that the global
`<sketchbook>/libraries/` copy is *not* used: a `TFT_eSPI` with this board's `User_Setup.h` pins, or the real LVGL 8.3.11.
- **If the project has `libraries/`, always compile with `--libraries <project>/libraries`.** A build that silently
  fell back to the global copy is a failure even if it compiles: it built the wrong thing. Check with `compile -v`
  which path each library resolved to.
- **Vendor a library only when it needs board-specific config, the Library Manager's version is broken or
  mislabelled, or the user asks.** Stock libraries (`XPT2046_Touchscreen`, `ArduinoJson`, `Preferences`) stay global.
  Every local copy can drift and needs a reason to exist; write the reason in the README.
- **Copy a correctly configured library from a project with the same board** rather than downloading and
  reconfiguring it.
- **Flag stale or decoy copies** (a second `TFT_eSPI*` folder beside the real one) instead of using them.
- **Never install or upgrade a library globally** to fix a project that is meant to use a vendored copy.
- Keep a `LIBRARY_STATUS.md` in the global `libraries/` folder that marks each global library STOCK or CUSTOM, with what was
  changed. Back up the custom files before updating a CUSTOM one.

## 3. Build and flash: commands
Classic ESP32 (CYD, most devkits): FQBN `esp32:esp32:esp32`, port usually `/dev/ttyUSB0` (CH340/CP210x bridge).
ESP32-S3 (Cardputer, S3 devkits): `esp32:esp32:esp32s3`, port usually `/dev/ttyACM0` (native USB). Cardputer via the
M5 core: `m5stack:esp32:m5stack_cardputer`.

```bash
arduino-cli board list                                             # find the port
arduino-cli compile --fqbn esp32:esp32:esp32 [--libraries libraries] --upload -p /dev/ttyUSB0 SKETCH_FOLDER
arduino-cli monitor -p /dev/ttyUSB0 --config 115200                # match Serial.begin()
```

- **Compile only, by default.** Flash only when the user asked for it in this task: it needs a specific board on a
  specific port.
- **Sketch too big** (`text section exceeds available space`): add `:PartitionScheme=min_spiffs` to the FQBN.

  | `PartitionScheme` | App space | Trade-off |
  |---|---|---|
  | `min_spiffs` (usual choice) | 1.9 MB | keeps OTA, 190 KB SPIFFS |
  | `huge_app` | 3.0 MB | no OTA, 1 MB SPIFFS |
  | `no_ota` | 2.0 MB | no OTA, 2 MB SPIFFS |
  | default | 1.3 MB | OTA + 1.5 MB SPIFFS |

  Stack options with commas: `esp32:esp32:esp32:PartitionScheme=min_spiffs,FlashFreq=80`.
- **`arduino-cli compile` doesn't write to the sketch's `build/` folder** unless you pass `--export-binaries` (or
  `--output-dir`). A `.bin` already there can be from an older session. Check the `.elf` time (or `strings` it for a
  just-changed string) before treating a flash as a test of the code you just edited.
- **PlatformIO:** `pio run -e <env>`; upload `pio run -e <env> -t upload --upload-port /dev/ttyACM0`. If a build fails
  on LittleFS/LFS dependencies, delete `.pio/core/penv` (or the project's `.pio`) and retry. Pin a dependency
  (`lib@3.10.3`, not `^3.10.3`) when a new upstream release breaks the build, and note when to revert.
- **ESP-IDF:** source the environment in every new shell (`. ~/esp/esp-idf/export.sh`), then `idf.py build`,
  `idf.py -p <port> flash monitor` (`Ctrl+]` exits the monitor). Use the exact IDF version the project names.

## 4. Flashing a precompiled `.bin`
Three cases; which one depends on where the file came from.

| What you have | How to flash |
|---|---|
| `arduino-cli`'s own output: `<sketch>.ino.bin` with sibling `.bootloader.bin` and `.partitions.bin` | `arduino-cli upload --fqbn <fqbn> -p <port> --input-dir BIN_FOLDER` |
| One **merged** image (bootloader + partitions + app), usually from PlatformIO or a release page | `esptool.py --chip <chip> --port <port> --baud 921600 write_flash 0x0 FILE.bin` |
| An **app-only** image | `write_flash 0x10000 app.bin` (check the project's `partitions.csv` / `flash_args`) |

- `arduino-cli upload --input-dir` can't read a merged image ("could not find a valid build artifact"). Use esptool.
- **Telling them apart:** a merged image is a single standalone file, usually a bit larger; an app image only exists
  next to its `.bootloader.bin`/`.partitions.bin`, or the project's `flash_args` says which address. When unsure,
  look at `flasher_args.json`/`flash_args` before guessing an offset.
- Flashing a merged image at `0x0` overwrites the bootloader and partition table; a later full flash of your own
  project restores them.
- **Use the esptool bundled with the esp32 core** (`~/.arduino15/packages/esp32/tools/esptool_py/<ver>/esptool.py`)
  rather than relying on a global `pip` esptool. It needs `pyserial`.
- **A script that runs `python3 -m esptool` internally:** set `PYTHONPATH` to that exact version folder. Spell out
  the version; a `*` wildcard can silently resolve to some other esptool on the machine.
- **Name exported binaries so a loose copy identifies itself:** `<project>_<version>_<branch>_<commit>.bin` (plus the
  matching `.bootloader.bin`/`.partitions.bin`). Archive known-good builds per version and don't delete old ones.
- For the post-build serial checks in some upstream repos, flash with esptool at the variant's bootloader address,
  partitions at `0x8000`, firmware at `0x10000`, as their own CLAUDE.md says.

## 5. Known gotchas (match the error here before treating it as new)
| Symptom | Cause | Fix |
|---|---|---|
| `'ledcAttach' was not declared` | core-3.x API built on core 2.x | 2.x: `ledcSetup(ch,f,res)` + `ledcAttachPin(pin,ch)` + `ledcWrite(ch,duty)`, or build on core 3.x |
| `'ledcSetup' was not declared` | core-2.x API built on core 3.x | 3.x: `ledcAttach(pin,f,res)` + `ledcWrite(pin,duty)`, or build on core 2.x |
| `arm_neon.h`, `atomic.h` not found; `unknown type name 'lv_result_t'`/`'lv_display_t'`; assembler `unknown opcode … 'typedef'` | The Library Manager's "LVGL 8.3.11" is really 9.x (ARM Helium assembly, 9.x types) | Use the real 8.3.11 (from the GitHub tag) vendored in `libraries/`, with `--libraries` |
| `rst:0x8 TG1WDT_SYS_RESET` boot loop on first `lv_timer_handler()` | `lv_disp_drv_t`/`lv_indev_drv_t` declared as locals in `setup()`; LVGL keeps a pointer | Make them `static` globals |
| Wrong colours with LVGL | `LV_COLOR_16_SWAP` and `pushColors(..., swap)` both swap, or neither does | Exactly one swaps: `LV_COLOR_16_SWAP 0` + `pushColors(..., true)` |
| `does not give a valid preprocessing token` in LVGL | Inline comment on a `#define` value line in `lv_conf.h` (GCC 8 token paste) | Put comments on the line above |
| White text vanishes on LVGL 8.3 | Default screen background is light grey | Set a dark background on every screen you create |
| Boot-loop resets at display init | Brownout detector trips on the inrush | `WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0)` before display init |
| `error: expected nested-name-specifier before numeric constant … macro 'FP'` | A library release declares `template <typename FP>`, colliding with a `-DFP=…` build flag | Pin the library to the last release before the change |
| No `/dev/ttyUSB*`/`ttyACM*` | Charge-only USB cable, or missing permission | Swap cable; `sudo usermod -aG dialout $USER` and log in again |
| Upload starts then times out / port grabbed | `brltty` claims CH340 ports on Debian/Ubuntu-based distros; or board not in download mode | `sudo apt remove brltty`; hold **BOOT** (Cardputer: **G0**) as the upload starts |
| "This chip is ESP32-S3, not ESP32" | Wrong FQBN | Use `esp32:esp32:esp32s3` |
| "Port busy" | A monitor session is open | Close it first |
| Web-based flasher (WebSerial) finds no port | Browser is a Flatpak/Snap and can't see udev devices | Use a native Chromium/Chrome package |
| Under a Launcher, an app's settings menu is empty or edits don't stick | The Launcher builds the app's data partitions itself and may give it no SPIFFS; code that writes the file before updating its RAM copy loses everything | Always update the in-RAM settings, skip only the disk write when the filesystem is missing |
| Under a Launcher, settings are lost on reinstall | Launcher workflow, not a bug | Use the Launcher's Backup Data / Restore before deleting or reinstalling |

## 6. Writing firmware
- **Major infrastructure ports are copies, not edits.** Moving to another UI framework (TFT_eSPI → LVGL), another core
  major version or another board family: copy the sketch to a sibling (`<Project>_lvgl/`) and port the copy. The user
  wants both buildable and flashable side by side. Git history is not a substitute for a copy on disk. Ordinary fixes
  and features stay in place.
- **Preserve behaviour.** A port reproduces the existing screens and flow before any visual change.
- **Never silently change** display rotation, colour order, touch calibration or `map()` constants carried over from
  working code. Touch axes are rotation-dependent and swapped relative to the display; carry the existing mapping over.
- **Keep pin maps and hardware constants in one place** (a config header or the top of the sketch).
- **Compile incrementally.** For a large port, get a blank screen building first (that's where most init gotchas
  bite), then one screen or feature at a time.
- **Don't drop features to make something compile.** Prefer an additive fix; if a feature can't carry over, ask.
- **Don't rewrite third-party library source** unless asked.
- **Multi-board firmware is flash-size first:** reuse existing helpers, keep shared logic in shared code, guard every
  board-specific `#include` and block behind its board macro (PlatformIO's dependency finder uses those guards), no
  speculative options. A change in shared code is a change for every board: consider them all.
- **A clean compile is not a working device.** Report what still needs real hardware: touch, colours, rotation,
  timing, radio range. Mark results *compiled* vs *tested on hardware*, and say which board.
- Keep `loop()` non-blocking where practical, redraw partially to avoid flicker, avoid large allocations in hot paths.

## 7. Hardware and wiring
- **ESP32 GPIOs are not 5 V tolerant.** Keep 5 V off every GPIO.
- **Never invent a pin number.** Take it from the vendor's pin docs, the board's silkscreen, or a project that's
  verified working. Carry "not yet checked on the physical board" caveats into the docs instead of dropping them.
  Avoid strapping pins and ADC-only pins for general I/O; note pull-ups.
- **Check what an add-on connector really exposes before buying adapters** (a board's expansion header may already
  carry the full SPI bus, so no SD sniffer is needed). Internal I²C buses that serve the keyboard, codec or IMU
  are reserved.
- **Radio modules brown out:** give each nRF24-PA/LNA its own bulk capacitor (≥100–220 µF plus a ceramic) and use a
  proper antenna for the band. High-current loads (LED drivers) get their own power path, switched by a logic-level
  MOSFET, not the board's battery circuit.
- **Wiring docs:** always a pin table (GPIO ↔ part ↔ terminal ↔ wire colour ↔ notes) and a diagram reviewable as text
  (SVG or ASCII), generated from the same table so they can't drift, in `WIRING.md`. A KiCad file only when asked.
- **KiCad schematics generated by hand:** use colon-free symbol ids (`CC1101`, not `RF:CC1101`): with a colon,
  `kicad-cli` looks for a library table that a stand-alone file doesn't have and fails with only "Failed to load
  schematic". Validate by exporting to PDF/SVG with `kicad-cli` and looking at it. Without KiCad on the machine, mark
  the file *not opened or validated in KiCad*.
- **Design docs explain why** a base board was chosen over the alternatives, with the BOM, bus allocation and power
  plan, so the next decision doesn't repeat the research.

## 8. Project layout and docs
```
<project>/
  README.md          board, FQBN/env, core, library table (local vs global and why), exact commands, gotchas met
  USER_GUIDE.md      how to use the finished device (controls, modes, feedback); no build content
  WIRING.md          pin table + diagram, for custom hardware only
  .gitignore         build output, secrets.h / wifi_credentials.h, editor folders
  libraries/         only libraries that need project-specific config
  <Sketch>/<Sketch>.ino
```
- New projects go in a new top-level folder under the projects folder, or an `unvalidated/` folder while
  experimental. Move to the main list once it builds and works on hardware.
- README command blocks copy one master quickstart's patterns (a `README.md` at the top of the projects folder) rather than
  re-deriving flag syntax per project. Project READMEs carry only what's specific: board identity, library table,
  gotchas actually met.
- Gotchas in a README are real ones from this project (from its history and commits), never generic filler.
- Upstream third-party READMEs in vendored libraries are not this project's docs; don't edit them.
