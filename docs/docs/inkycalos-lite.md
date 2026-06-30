# InkycalOS-Lite Setup Guide

Use this guide when you already have access to the prebuilt InkycalOS-Lite image.

> If any step does not work as expected, please open a GitHub issue or ask for help on Discord: <https://discord.gg/sHYKeSM>

## Getting access to InkycalOS-Lite

- Sponsor Inkycal via [GitHub Sponsors](https://github.com/sponsors/aceisace) and select the one-time InkycalOS-Lite option. If you purchased Inkycal on tindie, this is included.
- Forward your sponsor confirmation email to the address shown after sponsoring.
- Once your email is registered, download from the [InkycalOS-Lite page](https://inkycal.aceinnolab.com/inkycal-os-lite).
- You can re-download later from the same page, and new releases are shared with registered supporters.

## Flashing InkycalOS-Lite

1. Install [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
2. Insert your microSD card.
3. Flash the downloaded InkycalOS-Lite image.
4. Reinsert the card so the `bootfs` partition is visible on your computer.

![Raspberry Pi Imager setup flow](https://github.com/user-attachments/assets/5cc7ff42-dff1-4fc7-b4d5-dadee44faa41)

This GIF shows the Raspberry Pi Imager flashing flow used for InkycalOS-Lite.

## Set up user-data and network

InkycalOS-Lite uses custom cloud-init files, so prepare them separately:

1. Open the [Inkycal Raspberry Pi config page](https://inkycal.aceinnolab.com/rpi-config).
2. Fill in your network and login details.
3. Generate and download both config files.
4. Copy both files to `bootfs` and allow overwrite.

## Add your settings.json

1. Generate a config with the [settings.json generator](https://inkycal.aceinnolab.com/ui).
2. Make sure at least one module is configured.
3. Copy `settings.json` to `bootfs`.

## First boot

1. Insert the microSD card into the Raspberry Pi.
2. Power on the device.
3. Inkycal reads `settings.json` from `bootfs` and starts automatically.

Current images are built with service-based startup (`inkycal.service` and `inkycal-webui.service`), not crontab startup.

If you want to change layout/settings later, regenerate `settings.json` and overwrite the file in `bootfs`.

## Troubleshooting

- Display flicker during refresh is normal for most e-paper displays.
- If the display stays blank:
  - re-check display connector orientation and wiring,
  - validate `settings.json` (or generate a fresh file),
  - debug over SSH.

## SSH access for debugging

Create an SSH host using:

- Hostname: `inkycal.local`
- Username: `inky`
- Password: `<your_password>`
- Method: `SSH`

After connecting, run:

```sh
cd $HOME/Inkycal
source venv/bin/activate
python inky_run.py
```

Copy the full error output and share it in Discord or in a GitHub issue.


