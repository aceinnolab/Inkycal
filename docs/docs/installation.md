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
Check the **GitHub Sponsors page** or use the PayPal link provided in the repository README.

### ▶️ Installation steps
1. Flash the downloaded `.img` file using **Raspberry Pi Imager**.
2. Copy your `settings.json` to the boot partition.
3. Insert the SD card and power the Pi.
4. Inkycal boots automatically.

You're done. 🎉

---

# 🐍 3. Install on Raspberry Pi OS (Manual Installation)

This method gives you full control.  
Recommended for advanced users, developers, or custom hardware setups.

---

## Step 1 — Flash Raspberry Pi OS

Use **Raspberry Pi Imager** and write:

> ⚠️ Recommended version:  
> **Raspberry Pi OS Lite (bookworm)** — the newest release may have kernel issues.

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
# TODO: update ot use raspi-config, non-interactive
sudo sed -i s/#dtparam=spi=on/dtparam=spi=on/ /boot/firmware/config.txt
``

Set timezone (optional):
```sh
sudo dpkg-reconfigure tzdata
```

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
libjpeg-dev libffi-dev libopenblas-dev libopenjp2-7 wkhtmltopdf \
rustc build-essential libssl-dev -y
```

## Step 6 - Clone & Install Inkycal

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

## Step 7 — Enable Autostart

- Add Inkycal to crontab (no sudo):
```shell
CRON_LINE='@reboot sleep 60 && cd $HOME/Inkycal && venv/bin/python inky_run.py &'
( crontab -l 2>/dev/null | grep -qxF "$CRON_LINE" ) || \
( crontab -l 2>/dev/null; echo "$CRON_LINE" ) | crontab -
```


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

## 🆘 Troubleshooting Summary
> Display stays white

Likely missing BCM2835 driver for 12.48”.

Slow installation on Pi Zero W

Use piwheels + swap (already covered above).

settings.json missing

Ensure it is placed at:
* /boot/settings.json
* Same directory as inky_run.py