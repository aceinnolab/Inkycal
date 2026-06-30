# Troubleshooting

## Common install issues

### Installation is very slow on Pi Zero

- Use PiWheels indexes during `pip install`.
- Enable swap before dependency installation.

### `settings.json` not found

Inkycal searches typical boot locations (`/boot/settings.json`, `/boot/firmware/settings.json`) unless a custom path is supplied.

### SPI / display init failures

- Ensure SPI is enabled (`raspi-config`).
- Confirm the selected display model matches your hardware.
- Re-run the installer display test.

## Runtime issues

### Inkycal service does not start

- Check status: `systemctl status inkycal.service`
- Check logs in `logs/inkycal.log`

### Modules fail due to network errors

- Verify internet connectivity and DNS.
- Validate API keys for Weather/Todoist/Tindie.

### Webshot capture fails

- Install Chromium/Chrome and chromedriver.
- Optionally set `INKYCAL_BROWSER_BIN` and `INKYCAL_CHROMEDRIVER_BIN`.

## Local Web UI notes

The local web UI supports:

- service start/stop/restart and dry run
- hardware status with periodic refresh
- timezone update
- settings editing (full JSON and key/value)
- display actions (calibration, clear, demo image)

If a display action is running, Inkycal service is temporarily paused and then restored.

## Need help from the community?

If you are unsure whether the problem is wiring, configuration or a software bug, the quickest support path is often Discord:

- Join the Inkycal Discord server: [https://discord.gg/sHYKeSM](https://discord.gg/sHYKeSM)
- Share the display model, your `settings.json` snippet, and the exact error/log output
- If the issue is clearly reproducible, also open a GitHub issue so it can be tracked

