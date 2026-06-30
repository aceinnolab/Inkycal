# 📦 Installation Guide

Welcome to the Inkycal installation guide.  
Whether you're installing Inkycal on a **Raspberry Pi**, setting it up on a **desktop system**, or using the preconfigured **InkycalOS Lite** image, this guide will walk you through each step.

---

# 🚀 1. Choose Your Installation Method

Inkycal can be installed in **three different ways**:

| Method | Recommended For | Difficulty | Notes |
|-------|------------------|-----------|-------|
| **InkycalOS Lite (preconfigured)** | Raspberry Pi Zero / Zero W | ⭐ Very Easy | Fastest and most reliable method |
| **Install on Raspberry Pi OS** | Full control, custom setups | ⭐⭐ Medium | Requires manual configuration |
| **Install on non-GPIO devices** | Development, preview, debugging | ⭐ Easy | No display output |

---

# 🎯 2. Using InkycalOS Lite (Recommended)

If you want the **fastest, most reliable installation**, use the prebuilt InkycalOS Lite image.

### ✅ What you get:
- Fully configured Raspberry Pi OS Lite  
- SPI enabled  
- Dependencies preinstalled  
- Inkycal installed & autostart configured  
- Best possible performance on Pi Zero  

### 📥 How to get it
InkycalOS Lite is available to supporters of the project.  

- Sponsor the repo through the [GitHub Sponsors button](https://github.com/sponsors/aceisace). Use the one-time option for InkycalOS-Lite.
- Forward the sponsor confirmation email to the address shown after sponsoring.
- Once your email is registered, visit the [InkycalOS-Lite download page](https://inkycal.aceinnolab.com/inkycal-os-lite) to retrieve your download link.
- New releases are distributed to registered supporters by email.

### ▶️ Flashing InkycalOS-Lite

1. Install [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
2. Insert your microSD card.
3. Flash the downloaded InkycalOS-Lite image.
4. Reinsert the card so the boot partition (`bootfs`) becomes visible on your computer.

### 🌐 Setting up user-data and network

Raspberry Pi Imager does not pre-fill the custom InkycalOS-Lite user-data/network setup, so prepare those files separately:

1. Open the [Inkycal Raspberry Pi config page](https://inkycal.aceinnolab.com/rpi-config).
2. Fill in your network and login details.
3. Generate and download the configuration files.
4. Copy both files into the visible `bootfs` partition on the SD card and allow overwrite if prompted.

### 🧩 Add `settings.json`

1. Generate your config from the [settings.json generator](https://inkycal.aceinnolab.com/ui).
2. Make sure you add at least one module.
3. Copy `settings.json` into the `bootfs` partition as well.

### ▶️ First boot

1. Insert the microSD card into the Raspberry Pi.
2. Power on the device.
3. Inkycal will look for `settings.json` in the boot partition and render automatically if the file is valid.

If you want to adjust the layout later, simply generate a new `settings.json` and replace the existing file.

### 🔐 SSH access (if something goes wrong)

If the display does not show the expected dashboard, connect over SSH:

```sh
ssh inky@inkycal.local
```

Use the password you configured in the Raspberry Pi config step.

Then run:

```sh
cd $HOME/Inkycal
source venv/bin/activate
python inky_run.py
```

This prints the real error instead of leaving you with a blank screen.

### 🆘 InkycalOS-Lite troubleshooting

- Some flicker during refresh is normal for e-paper displays.
- If the screen stays blank, double-check wiring/orientation on the display connector.
- If rendering fails, regenerate `settings.json` or debug over SSH.
- If you need help, join the community Discord: [https://discord.gg/sHYKeSM](https://discord.gg/sHYKeSM)

You're done. 🎉

---

# 🐍 3. Install on Raspberry Pi OS

This path gives you full control while still using the current Python installer for the final setup steps.
It is recommended for advanced users, developers, and custom hardware setups.

---

## Step 1 — Flash Raspberry Pi OS

Use **Raspberry Pi Imager** and write:

> ✅ Recommended version used in the automated Raspberry Pi test workflow:  
> [Raspberry Pi OS Lite (Trixie, armhf, 2025-11-24)](https://downloads.raspberrypi.com/raspios_lite_armhf/images/raspios_lite_armhf-2025-11-24/2025-11-24-raspios-trixie-armhf-lite.img.xz)

This is the exact base image referenced in `.github/workflows/test-on-rpi.yml`.

Configure in Imager:

| Setting  | Value               |
|----------|---------------------|
| Hostname | `inkycal`           |
| SSH      | Enable              |
| Username | choose one          |
| Password | choose one          |
| Wi-Fi    | Configure if needed |
| Timezone | Your local timezone |

---

## Step 2 — Prepare the SD Card

1. Generate your `settings.json` in the **Inkycal Web UI**  
   <https://inkycal.aceinnolab.com/ui>

2. Copy `settings.json` to the root of the SD card.

Insert the SD card into the Pi and boot.

---

## Step 3 — Connect via SSH

After ~2–3 minutes, connect:

```sh
ssh username@inkycal.local
```
(on Windows/macOS you can also use Termius)

## Step 4 — Raspberry Pi Setup

Expand filesystem:
```sh
sudo raspi-config --expand-rootfs
```

Enable SPI:
```sh
sudo raspi-config nonint do_spi 0
```

Set timezone (optional):
```sh
sudo dpkg-reconfigure tzdata
```

Or set it later from the installer menu with:

- `Set timezone (raspi-config)`

Required for 12.48" only:
```shell
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.71.tar.gz
tar zxvf bcm2835-1.71.tar.gz
cd bcm2835-1.71/
sudo ./configure && sudo make && sudo make check && sudo make install
```

## Step 5 — Install Dependencies

- Update system:
```shell
sudo apt-get update -y
```

- Enable swap (strongly recommended on the Raspberry Pi Zero)
```sh
sudo sh -c 'mkdir -p /etc/rpi/swap.conf.d &&
cat <<EOF | cmp -s - /etc/rpi/swap.conf.d/80-use-swapfile.conf || cat <<EOF >/etc/rpi/swap.conf.d/80-use-swapfile.conf
[Main]
Mechanism=swapfile

[File]
FixedSizeMiB=1024
EOF
EOF'
```

- Prevent memory overflow while installing:
```shell
export TMPDIR=/var/tmp
```

- Install apt dependencies:
```sh
sudo apt-get install git python3-dev python3-setuptools zlib1g-dev \
libjpeg-dev libffi-dev libopenblas-dev libopenjp2-7 chromium chromium-driver \
rustc build-essential libssl-dev liblgpio-dev -y
```

## Step 6 — Clone & Install Inkycal

- Clone the repo
```shell
cd $HOME
git clone https://github.com/aceinnolab/Inkycal
cd Inkycal
```
Create virtual environment:
```sh
python -m venv venv
source venv/bin/activate
```

Install dependencies using piwheels to avoid multi-hour builds:
```shell
pip install --upgrade pip wheel setuptools --index-url https://www.piwheels.org/simple --extra-index-url https://pypi.org/simple
pip install -e . --index-url https://www.piwheels.org/simple --extra-index-url https://pypi.org/simple
pip install -r raspberry_os_requirements.txt --index-url https://www.piwheels.org/simple --extra-index-url https://pypi.org/simple
```

### The installer on Raspberry Pi OS

The installer is Python-only and provides an arrow-key menu on Raspberry Pi OS:

```sh
cd $HOME/Inkycal
python3 installer.py
```

It covers:
- install/repair
- update flow
- service generation for your real username and path
- swap setup on Raspberry Pi Zero, with confirmation and duplicate detection
- timezone updates via `raspi-config`
- permission repair (common sudo mishaps)
- timed display test with model selection
- local web UI service setup
- a full wipe option that removes installer-managed system changes and can delete the cloned folder

By default, first startup after boot also shows a monochrome splash with `Inkycal` and the current version before modules render. You can disable this via `"show_startup_splash": false` in `settings.json`.

For a dedicated walkthrough, see:

- [Installer Guide](installer.md)

## Step 7 — Finish with the installer

Run the installer to complete service installation, swap setup, and the display test:

```sh
python3 installer.py
```

If you are on a Raspberry Pi Zero, the installer will ask whether to set up swap and will skip it if it already exists.

Inkycal creates `Inkycal/logs/inkycal.log` and rotates logs daily (max 14 rotations). The installer-managed service uses `/tmp/inkycal.lock`, ensuring only one instance runs at a time.

The installer can also set up the lightweight local web UI service:

- `inkycal.service` → main dashboard runtime
- `inkycal-webui.service` → local control panel

For the web UI workflow, see:

- [Local Web UI](webui.md)


### Install on Non-GPIO Devices (Development Mode)

You can run Inkycal on macOS, Linux, Windows — useful for:

* Debugging
* Developing new modules
* Rendering previews

You won’t be able to show images on real hardware.


```shell
git clone https://github.com/aceinnolab/Inkycal
cd Inkycal
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

Run:
```sh
python inky_run.py
```

## PiSugar Support
If you’re using a PiSugar battery board, see:

https://github.com/aceinnolab/Inkycal/wiki/PiSugar-support

This covers:

* Driver installation
* Configuration
* Auto-shutdown
* Power monitoring

## 🤝 Community support

If you get stuck during installation, the community is happy to help.

- Join the Discord support server: [https://discord.gg/sHYKeSM](https://discord.gg/sHYKeSM)
- Open GitHub issues for reproducible bugs
- Include logs or the exact terminal error when asking for help

## 🆘 Troubleshooting Summary
> Display stays white

Likely missing BCM2835 driver for 12.48”.

Slow installation on Pi Zero W

Use piwheels + swap (already covered above).

settings.json missing

Ensure it is placed at:
* /boot/settings.json
* Same directory as inky_run.py