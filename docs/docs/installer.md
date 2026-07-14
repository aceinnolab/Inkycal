# Installer Guide

The Python installer is the recommended way to finish setting up Inkycal on Raspberry Pi OS and to maintain an existing installation.

It is designed to reduce manual systemd, permission and dependency mistakes while keeping the installation portable to your real username and path.

## When to use the installer

Use the installer when you want to:

- perform a first-time setup after cloning the repo
- create or repair the virtual environment
- install or refresh `systemd` services
- set up swap on Raspberry Pi Zero devices
- set system timezone via `raspi-config`
- repair file-permission mistakes caused by accidental `sudo`
- run the built-in display test flow
- update an existing installation safely
- remove installer-managed changes with the full wipe option

## Run it

```bash
cd $HOME/Inkycal
python3 installer.py
```

> Do not run the installer directly as root. Run it as your normal user and let it elevate only when required.

## What the installer currently manages

### Dependency setup

The installer can:

- create the `venv`
- install or refresh Python dependencies
- install or repair apt-side prerequisites when needed
- install WiringPi from source (unconditionally on Linux, for 12.48" display compatibility)
- use the PiWheels-friendly package flow already documented in the main installation guide

### Raspberry Pi Zero swap setup

On Raspberry Pi Zero devices, the installer can configure the recommended swap file automatically after asking for confirmation.

It writes:

- `/etc/rpi/swap.conf.d/80-use-swapfile.conf`

and restarts `systemd-swap` if needed.

### Timezone setup

The installer menu includes:

- `Set timezone (raspi-config)`

This runs `raspi-config nonint do_change_timezone <TZ>` and applies the selected timezone without leaving the installer.

### Portable `systemd` services

The installer creates services using your real username and repo path.

Managed services:

- `inkycal.service`
- `inkycal-webui.service`

The main service runs:

```text
inky_run.py --mode run
```

The web UI service runs:

```text
inky_webui.py
```

### Locking and logs

The installer-managed service setup uses:

- `/tmp/inkycal.lock` to prevent concurrent runtime instances
- `logs/inkycal.log` for rotating file logs inside the project folder

## Display test support

The installer includes a timed display-test flow with display-model selection.

This is useful for validating:

- SPI access
- display driver selection
- basic render success before relying on your full `settings.json`

For additional display checks after installation, the local web UI also provides:

- calibration
- clear
- demo image display

See also:

- [Local Web UI](webui.md)

## Update workflow

You can re-run the installer after pulling new changes:

```bash
cd $HOME/Inkycal
git pull
source venv/bin/activate
pip install -e .
python3 installer.py
```

This helps reconcile services, dependencies and common environment drift after updates.

## Permission repair

If you previously used `sudo` in the repo and now hit ownership or write errors, the installer can repair those common permission problems.

## Full wipe

The installer also includes a full wipe option that can:

- remove installer-managed `systemd` units
- remove swap setup created by the installer
- optionally purge installer-managed apt packages
- optionally delete the cloned `Inkycal` folder

Use this if you want a cleaner uninstall path than deleting files manually.

## Troubleshooting

### Installer says not to run as root

That is intentional. Run:

```bash
python3 installer.py
```

as your normal user instead of `sudo python3 installer.py`.

### Service starts but nothing appears on display

- verify the display model in `settings.json`
- run the installer display test
- check `logs/inkycal.log`
- confirm SPI is enabled

### Need help?

The community is happy to help:

- Discord: [https://discord.gg/sHYKeSM](https://discord.gg/sHYKeSM)
- GitHub Issues: [https://github.com/aceinnolab/Inkycal/issues](https://github.com/aceinnolab/Inkycal/issues)
