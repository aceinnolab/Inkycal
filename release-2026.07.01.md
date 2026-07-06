# Inkycal v2026.07.01

Release date: 2026-07-01  
Version source: `_version.txt` (`2026.07.01`)  
Release tag: `v2026.07.01`

This release covers all work since commit `6896df3`.

## Added

- Local web UI improvements:
  - mobile-first responsive layout and improved styling
  - settings editor with both raw JSON and key/value editing
  - timezone updates from UI
  - hardware info auto-refresh endpoint
  - display test actions from UI (calibration, clear, demo image)
  - git maintenance tools in UI (branch switch + `git pull --ff-only`)
  - sudo password modal for privileged actions (service/timezone/display operations)
  - support links for settings generator, InkycalOS-Lite, and Discord
- New optional webshot setting `dither` (default `true`) for module-level dithering control.
- Weather module now displays combined current/max temperature format.
- Agenda module improvements:
  - two-column layout support
  - better wrapping and date-header continuation handling
  - all-day icon centering updates
  - docs updates for agenda module
- Added support for `image_file_12_in_48` display model.
- Docs pages added:
  - InkycalOS-Lite setup guide
  - installer guide
  - local web UI guide
  - troubleshooting
  - modules: weather, image, custom
- Added InkycalOS-Lite setup GIF embed to docs.
- Optional startup splash behavior in core startup path:
  - renders monochrome `Inkycal` + version text
  - shown once per boot by default
  - can be disabled with `show_startup_splash: false` in `settings.json`

## Changed

- Network fetch handling moved from `urlopen` to `requests` + `certifi` in textfile and iCal parsing paths.
- General code-quality pass across service scripts, logging setup, and installer paths.
- Requirements/dependency updates in `requirements.txt`, `dev_requirements.txt`, and Raspberry Pi requirements.
- Docs navigation (`docs/mkdocs.yml`) and content structure improved for discoverability.
- CI workflow maintenance and hardening:
  - updated workflow actions/tooling versions
  - added timeout and concurrency controls
  - improved release upload and compression behavior
  - branch-aware workflow dispatch behavior for `test-on-rpi` and `update-os`
  - `update-os` now uses service-based startup provisioning instead of crontab
  - `update-os` now honors selected target branch during clone/switch
  - workflow renamed to `Build OS image`

## Fixed

- Todoist due-date handling.
- Import registration issue in module importer.
- Agenda rendering bugs:
  - overlapping columns
  - bottom-of-column date header edge cases
  - older events clamped to today for multi-day rendering
- Calendar visual fixes:
  - red "today" circle clipping corrected by reducing radius factor
  - date-width measurement robustness improvements
- Canvas autofit sizing stability improved by using a static start size for each autofit pass.
- Webshot module now respects per-module dither setting during palette conversion.
- `update-os` no longer fails on missing `systemd-swap` package.

## Documentation

- Sync and expansion of docs to match current `dev` branch behavior.
- Updated install/quickstart/hardware/dev-reference content.
- Added dedicated installer and web UI pages with placeholder assets.
- Added community support links (Discord) and InkycalOS-Lite guidance.
- Added dedicated InkycalOS-Lite page and linked it in nav/installation guide.

## Notes for maintainers

- Suggested compare range for release PR notes: `6896df3...HEAD`
- Suggested GitHub release title: `Inkycal v2026.07.01`
- Suggested release tag: `v2026.07.01`


