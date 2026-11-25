# 70 — Linux, the home server, and devices

Work on the Linux desktop, the home media server, single-board computers (Orange Pi / Raspberry Pi) and Android
tablets over adb. The common rules (00) apply: hands off the live thing (§2) here means the running server, a
user's library and a device's boot partition. Specific hosts, addresses and installed tools belong in each project's own notes, not here. Most lessons here are *seen once*.

## 1. Reaching machines
- **Use SSH aliases** from `~/.ssh/config` (key auth) rather than typing user@IP. Check reachability with one quick
  `ssh -o BatchMode=yes -o ConnectTimeout=5 <host> true` before planning remote work.
- **Bulk file work on a server: run it on the server over SSH**, not through the SMB/GVFS mount on the desktop.
  The mount is far slower and hides permissions and sparse files.
- **Hosts on DHCP move.** Find them by mDNS name (`avahi-resolve -4 -n <host>.local`) or by MAC in `ip neigh`, not by
  last week's IP. Write down the stable identifiers (hostname, MAC), not only the IP.
- **Non-login SSH shells may lack `/usr/sbin`** on PATH: prefix `export PATH=$PATH:/usr/sbin:/sbin`.
- **Don't cut off your own session.** Switching a single Wi-Fi radio between client and hotspot, changing routes or
  restarting networking over an SSH session on that link drops it. Use a timed change (`--for 10m`), a console, or
  tell the user they'll need a power cycle.
- **Remote access from outside the LAN goes through Tailscale**, not a VPN provider's mesh feature. Prove it from a
  phone on cellular data; it can't be proven from the server itself.

## 2. Ask for a physical check when the user is at the device
When a question can be settled by the user doing something simple by hand (unplug and replug, look at the phone's
Wi-Fi list, read the HDMI screen, press a button) and reporting back, ask for that instead of scripting a remote
experiment with sweeps, retries and long waits. Give a short numbered list of what to do and what to report. Keep
remote work to short targeted commands once the device is known to be reachable. (A long self-recovering remote test costs far more than a 30-second manual check.)

## 3. Root, sudo and system changes
- **Assume `sudo` needs a password** that the session doesn't have and must not ask for. Check with `sudo -n true`.
- **For root work on the desktop:** write one script to the scratchpad, check it with `bash -n`, and run it once
  with `pkexec /bin/bash <absolute path>` (one graphical prompt per call, so bundle all the steps). Removable drives
  can be mounted, unmounted and powered off without root via `udisksctl`.
- **For root work on a server:** copy the script there and ask the user to run `sudo bash ~/script.sh` themselves.
  Say what it prints and what to send back.
- **The script verifies its own result** and prints PASS/FAIL (e.g. compare exit IPs), so the user's report is one
  line.
- **Change services with systemd drop-ins** (`/etc/systemd/system/<unit>.d/override.conf`; for a templated unit put
  it on `<name>@.service.d/` so every instance gets it), never by editing the vendor unit.
- **Edit config files whose keys contain backslashes** (e.g. `Session\Interface`) with a small Python edit, not
  `sed`. Back the file up first.
- **Things the session was blocked from doing** (crontab `@reboot` lines, `chgrp` on a library, `UMask` in a unit)
  go to the user as exact commands, and are recorded as *handed to the user, not confirmed*.

## 4. Disks and images
- **Identify a disk by label, serial and size**, never by `sdb`/`sdc` (letters change between plugs):
  `lsblk -o NAME,SIZE,LABEL,SERIAL,MODEL`. A `dd`/`mkfs` script checks all three before writing and refuses
  otherwise.
- **Verify downloaded OS images** (checksum) and keep the verified copy in an ignored `downloads/` in the project.
- **Before formatting, confirm the old contents are backed up elsewhere** and record that the user said so.

## 5. Networking and VPN on the server
- **"Connected" is not "used."** Check where traffic really goes: `ip route`, `ip rule`, and
  `curl --interface <if> ifconfig.me` vs plain `curl ifconfig.me`.
- **Per-app VPN routing** (one app through the tunnel, the rest of the machine normal) needs all of these together:
  1. turn off the VPN client's catch-all policy routing (`nordvpn set routing disabled`; mesh features that depend on
     it have to go off first);
  2. bind the app to the tunnel interface (e.g. qBittorrent `Session\Interface` and `Session\InterfaceName`);
  3. give the service `AmbientCapabilities=CAP_NET_RAW` in a drop-in, since `SO_BINDTODEVICE` needs it for non-root.

  Binding is fail-closed: if the tunnel drops, the app can't connect, with no fallback to the real IP. Check whether
  the routing setting survives reconnects and reboots.
- **An `apt-get update` that fails on one stale source** (a duplicate or dead line in `/etc/apt/sources.list.d/`)
  breaks every installer that runs it. Back up that file and remove just the dead line.
- **Check which unit is really running** (`systemctl status`, the unit file path) before changing a service. The
  live box can differ from what the repo's installer would have created.

## 6. Media server and *arr apps
- **Division of labour:** the library manager (the *arr apps) owns naming, folder layout and downloads;
  a custom tool owns health, dedupe and compression. Don't run two tools that both rename the same files.
- **Read other apps' databases read-only** (`sqlite3 -readonly`) and never print key or password columns.
- **Shared libraries use a group** (e.g. `media`), `g+rwX`, setgid directories, and `UMask=0002` on the services.
  Don't turn on an app's own chmod/chown features if it has no error handling for folders it doesn't own.
- **Metadata sources share rate limits** between every tool using the same key; one tool's import can starve
  another's. Leave headroom and make imports retryable.

## 7. Android devices over adb
- **Prefer no-root.** Root and bootloader unlocks on consumer tablets often need low-level vendor tools with real
  brick reports; most goals (debloat, file manager, readers, media player) don't need root.
- **Debloat with `pm uninstall --user 0`** loops that have a dry-run mode, a protected-package guard and a
  `restore.sh` (`cmd package install-existing --user 0 <pkg>`). Read any debloat script in full before running it.
- **Know the landmines:** some vendor packages look removable but a system service depends on them, and removing
  them boot-loops the device. `adbd` usually still works during the hang, so the restore command can be retried in a
  loop until it lands.
- **Sideload only from the app's official source** (project's own releases page or official mirror), staged in a
  local `apks/` folder. Apps that need the user's login install from the store, by the user.
- **Check health after changes:** `getprop sys.boot_completed`, `adb logcat -b crash` empty.
- Things with no reliable adb command across vendor skins (e.g. setting the wallpaper) are left to one manual tap.
