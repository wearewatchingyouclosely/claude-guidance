#!/usr/bin/env bash
# linux-setup.sh — set up a Debian/Ubuntu/Mint PC for Claude Code work (the Linux twin of the Ninite installer).
#
# Dry run by default: it prints what it would do and changes nothing. Add --apply to do it.
# Run it as yourself, not with sudo: it asks for your sudo password only for the system steps.
# Safe to run again: anything already installed or configured is skipped.
#
#   bash setup/linux-setup.sh                    # base, dry run
#   bash setup/linux-setup.sh --apply            # base: git, python, ssh, editors, VS Code + extensions
#   bash setup/linux-setup.sh --esp32 --apply    # + arduino-cli, PlatformIO, serial access   (rule 60)
#   bash setup/linux-setup.sh --web --apply      # + Node LTS via nvm                         (rule 35)
#   bash setup/linux-setup.sh --kicad --apply    # + KiCad from the official PPA              (rule 60 §7)
#   bash setup/linux-setup.sh --all --apply      # everything
#   bash setup/linux-setup.sh --register-only --apply   # only record this folder's path (no sudo); rerun after moving it
#
# Exit codes: 0 done (or dry run finished), 1 a step failed, 2 bad arguments or unsupported system.

set -uo pipefail

APPLY=0; ESP32=0; WEB=0; KICAD=0; REGISTER_ONLY=0
NVM_VERSION="v0.40.1"
KICAD_PPA="ppa:kicad/kicad-10.0-releases"
EXTENSIONS=(
  anthropic.claude-code
  shd101wyy.markdown-preview-enhanced
  yzhang.markdown-all-in-one
  bierner.markdown-mermaid
  tomoki1207.pdf
  cweijan.vscode-office
  mechatroner.rainbow-csv
)

usage() { sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'; }

for arg in "$@"; do
  case "$arg" in
    --apply) APPLY=1 ;;
    --esp32) ESP32=1 ;;
    --web)   WEB=1 ;;
    --kicad) KICAD=1 ;;
    --all)   ESP32=1; WEB=1; KICAD=1 ;;
    --register-only) REGISTER_ONLY=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $arg"; echo; usage; exit 2 ;;
  esac
done

# ---------------------------------------------------------------- helpers
FAILED=()
CHANGES=0
say()  { printf '\n== %s\n' "$*"; }
skip() { printf '   ok    %s\n' "$*"; }
todo() { printf '   %s  %s\n' "$([ $APPLY = 1 ] && echo 'doing' || echo 'would')" "$*"; CHANGES=$((CHANGES+1)); }
# run "description" cmd args...   (no shell: arguments are passed as they are)
run() {
  local what="$1"; shift
  todo "$what"
  [ $APPLY = 1 ] || return 0
  if ! "$@"; then echo "   FAILED: $what"; FAILED+=("$what"); return 1; fi
}
have()    { command -v "$1" >/dev/null 2>&1; }
pkg_ok()  { dpkg-query -W -f='${Status}' "$1" 2>/dev/null | grep -q "install ok installed"; }

# ---------------------------------------------------------------- checks
if [ "$(id -u)" = 0 ]; then
  echo "Run this as yourself, not with sudo or as root. It asks for sudo only when it needs it."; exit 2
fi
if ! have apt-get || ! have dpkg-query; then
  echo "This script supports Debian, Ubuntu and Linux Mint (apt). Install the same tools by hand on other systems."; exit 2
fi
. /etc/os-release 2>/dev/null || true
echo "System: ${PRETTY_NAME:-unknown}   Mode: $([ $APPLY = 1 ] && echo APPLY || echo 'DRY RUN (add --apply to do it)')"
echo "Parts:  base$([ $ESP32 = 1 ] && echo ' + esp32')$([ $WEB = 1 ] && echo ' + web')$([ $KICAD = 1 ] && echo ' + kicad')"

# ---------------------------------------------------------------- register
# Every Claude Code session reads ~/.claude/CLAUDE.md. Record where this folder is, so projects and rules never need a
# fixed path (_START_HERE.md B1). The path comes from this script's own location, so a clone anywhere works.
GUIDE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
USER_MD="$HOME/.claude/CLAUDE.md"
register() {
  say "Register this guidance folder in ~/.claude/CLAUDE.md"
  if grep -qxF "Claude guidance folder: $GUIDE_DIR" "$USER_MD" 2>/dev/null; then
    skip "registered: $GUIDE_DIR"; return 0
  fi
  local verb="add"; grep -qF '<!-- claude-guidance:start -->' "$USER_MD" 2>/dev/null && verb="update"
  run "$verb the guidance path ($GUIDE_DIR)" python3 -c '
import pathlib, re, sys
md, path = pathlib.Path(sys.argv[1]), sys.argv[2]
block = ("<!-- claude-guidance:start -->\n"
         "Claude guidance folder: " + path + "\n"
         "Rules, templates and agents live there; its feedback inbox is _FEEDBACK/. Start with _START_HERE.md.\n"
         "<!-- claude-guidance:end -->\n")
old = md.read_text() if md.exists() else ""
pat = re.compile(r"<!-- claude-guidance:start -->.*?<!-- claude-guidance:end -->\n?", re.S)
new = pat.sub(lambda m: block, old) if pat.search(old) else (old.rstrip("\n") + "\n\n" if old.strip() else "") + block
md.parent.mkdir(parents=True, exist_ok=True)
md.write_text(new)
' "$USER_MD" "$GUIDE_DIR"
}

if [ $REGISTER_ONLY = 1 ]; then
  register
  echo
  [ ${#FAILED[@]} -gt 0 ] && { echo "FAILED: ${FAILED[*]}"; exit 1; }
  [ $APPLY = 1 ] && echo "Done." || echo "Dry run: run again with --apply to do it."
  exit 0
fi

if [ $APPLY = 1 ]; then
  echo; echo "Asking for your sudo password once for the system steps..."
  sudo -v || { echo "sudo failed; nothing was changed."; exit 1; }
fi

APT_UPDATED=0
apt_update() { [ $APT_UPDATED = 1 ] && return 0; run "apt-get update" sudo apt-get update -q && APT_UPDATED=1; }
apt_install() {   # apt_install pkg...   installs only the missing ones
  local missing=()
  for p in "$@"; do pkg_ok "$p" && skip "$p" || missing+=("$p"); done
  [ ${#missing[@]} = 0 ] && return 0
  apt_update
  run "apt install ${missing[*]}" sudo apt-get install -y -q "${missing[@]}"
}

# ---------------------------------------------------------------- base
say "Base packages (git, python, ssh, editors)"
# Windows Ninite equivalents: Git → git, Notepad++ → the desktop's text editor (VS Code below), PuTTY → openssh-client
# (plus putty itself, for people who want the same tool), Python 3 → python3 with venv and pip.
apt_install git python3 python3-venv python3-pip pipx openssh-client putty curl wget gpg ca-certificates unzip

say "VS Code (Microsoft's apt repository, not the Flatpak/Snap: those can't see serial ports and local tools)"
if have code; then
  skip "code $(code --version 2>/dev/null | head -1)"
else
  if grep -rqs 'packages.microsoft.com/repos/code' /etc/apt/sources.list.d/ /etc/apt/sources.list; then
    skip "Microsoft VS Code repository already configured"   # don't add a duplicate: duplicates break apt update (rule 70 §5)
  else
    run "add Microsoft's signing key" bash -c \
      'curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | sudo install -D -o root -g root -m 644 /dev/stdin /etc/apt/keyrings/packages.microsoft.gpg'
    run "add the VS Code repository" bash -c \
      'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list >/dev/null'
    APT_UPDATED=0
  fi
  apt_install code
fi

say "VS Code extensions (Claude Code and the viewers)"
if have code || [ $APPLY = 0 ]; then
  installed="$(code --list-extensions 2>/dev/null || true)"
  for ext in "${EXTENSIONS[@]}"; do
    if grep -qix "$ext" <<<"$installed"; then skip "$ext"; else run "install extension $ext" code --install-extension "$ext" --force; fi
  done
else
  echo "   VS Code isn't installed, so the extensions were skipped."; FAILED+=("VS Code extensions")
fi

# ---------------------------------------------------------------- esp32
if [ $ESP32 = 1 ]; then
  say "ESP32 / Arduino (rule 60)"
  apt_install python3-serial
  mkdir -p "$HOME/.local/bin" 2>/dev/null || true
  if have arduino-cli || [ -x "$HOME/.local/bin/arduino-cli" ]; then
    skip "arduino-cli"
  else
    run "install arduino-cli to ~/.local/bin" bash -c \
      'curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR="$HOME/.local/bin" sh'
  fi
  if have pio || [ -x "$HOME/.local/bin/pio" ]; then
    skip "PlatformIO (pio)"
  else
    run "install PlatformIO with pipx" pipx install platformio
  fi
  if id -nG "$USER" | grep -qw dialout; then
    skip "$USER is in the dialout group (serial ports)"
  else
    run "add $USER to the dialout group (log out and in afterwards)" sudo usermod -aG dialout "$USER"
  fi
  if pkg_ok brltty; then
    run "remove brltty (it grabs CH340 USB-serial ports)" sudo apt-get remove -y -q brltty
  else
    skip "brltty not installed"
  fi
  echo "   note  No esp32 core is installed: each project names its own version (rule 60 §1), e.g."
  echo "         arduino-cli core update-index && arduino-cli core install esp32:esp32@2.0.10"
fi

# ---------------------------------------------------------------- web
if [ $WEB = 1 ]; then
  say "Web (rule 35): Node LTS via nvm (the distro's Node is too old for current Vite and netlify-cli)"
  export NVM_DIR="$HOME/.nvm"
  if [ -s "$NVM_DIR/nvm.sh" ]; then
    skip "nvm"
  else
    run "install nvm $NVM_VERSION" bash -c \
      "curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/$NVM_VERSION/install.sh | bash"
  fi
  if [ -s "$NVM_DIR/nvm.sh" ] && bash -c ". '$NVM_DIR/nvm.sh' && nvm ls --no-colors lts/* >/dev/null 2>&1"; then
    skip "Node LTS ($(bash -c ". '$NVM_DIR/nvm.sh' && nvm version lts/*" 2>/dev/null))"
  else
    run "install Node LTS and make it the default" bash -c \
      ". '$NVM_DIR/nvm.sh' && nvm install --lts && nvm alias default 'lts/*'"
  fi
  echo "   note  netlify-cli isn't installed globally: sites run it with npx (\"netlify:dev\": \"npx netlify dev\")."
fi

# ---------------------------------------------------------------- kicad
if [ $KICAD = 1 ]; then
  say "KiCad (official PPA; the distro's KiCad is several versions behind)"
  if pkg_ok kicad; then
    skip "kicad $(dpkg-query -W -f='${Version}' kicad 2>/dev/null)"
  else
    if grep -rqs 'kicad/kicad' /etc/apt/sources.list.d/; then
      skip "KiCad PPA already configured"
    else
      apt_install software-properties-common
      run "add $KICAD_PPA" sudo add-apt-repository -y "$KICAD_PPA"
      APT_UPDATED=0
    fi
    apt_install kicad
  fi
fi

register

# ---------------------------------------------------------------- summary
echo
if [ ${#FAILED[@]} -gt 0 ]; then
  echo "FAILED (${#FAILED[@]}):"; printf '  - %s\n' "${FAILED[@]}"
  echo "Fix the first failure and run the script again; finished steps are skipped."
  exit 1
fi
if [ $APPLY = 0 ]; then
  [ $CHANGES = 0 ] && echo "Nothing to do: everything is already set up." \
                   || echo "Dry run: $CHANGES step(s) above would run. Run again with --apply to do them."
else
  echo "Done: $CHANGES step(s) ran."
  [ $ESP32 = 1 ] && echo "If you were just added to dialout, log out and back in before flashing a board."
  [ $WEB = 1 ]   && echo "Open a new terminal so nvm and Node are on your PATH."
  echo "Next: open VS Code, sign in to Claude Code, then follow _START_HERE.md Part B."
fi
exit 0
