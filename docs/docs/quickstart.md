# 🚀 Quickstart

This guide walks you through setting up **Inkycal** from start to finish in just a few minutes.  
If you want a deeper explanation of each step, see the **Installation** and **User Guide** sections.

---

## 1. What You Need

- **Raspberry Pi Zero W / Zero 2 / 3 / 4**
- **Supported e-paper display** (Waveshare / Pimoroni / similar)
- **MicroSD card** (min. 4GB)
- **Wi-Fi connection**
- **A computer with Raspberry Pi Imager**

Optional but recommended:

- **InkycalOS Lite** – a preconfigured plug-and-play OS image  
  *(available for GitHub Sponsors)*

---

## 2. Flash Raspberry Pi OS

1. Download **Raspberry Pi Imager**  
2. Select:

   | Setting    | Value                                                       |
   |------------|-------------------------------------------------------------|
   | OS         | Raspberry Pi OS Lite (recommended version—see Installation) |
   | Hostname   | `inkycal`                                                   |
   | Enable SSH | Yes                                                         |
   | Username   | choose any                                                  |
   | Password   | set one                                                     |
   | Wi-Fi      | configure SSID + password                                   |
   | Timezone   | set your local zone                                         |

3. Write the image to the microSD card.

---

## 3. Create Your `settings.json`

Go to:

👉 **https://inkycal.aceinnolab.com/ui**

There you can:

- Choose your display model  
- Add modules (Calendar, Weather, RSS, etc.)  
- Configure layout & language  
- Download your `settings.json`

Place the file in: /boot/settings.json on the SD card.

---

## 4. First Boot

Insert the microSD card → power the Pi.

Wait ~3 minutes for first boot.

Then connect via SSH:

```bash
ssh <username>@inkycal.local
```
## 5. Install Inkycal

Inside the Pi, run:
```shell
sudo apt update -y
sudo raspi-config --expand-rootfs
sudo sed -i s/#dtparam=spi=on/dtparam=spi=on/ /boot/firmware/config.txt
sudo dpkg-reconfigure tzdata
```

Then install Inkycal:
```shell
cd $HOME
git clone https://github.com/aceinnolab/Inkycal
cd Inkycal
python -m venv venv
source venv/bin/activate
pip install --upgrade pip wheel setuptools --index-url https://www.piwheels.org/simple --extra-index-url https://pypi.org/simple
pip install -e . --index-url https://www.piwheels.org/simple --extra-index-url https://pypi.org/simple
pip install -r raspberry_os_requirements.txt --index-url https://www.piwheels.org/simple --extra-index-url https://pypi.org/simple
```

## 6. Finish with the installer

Run the interactive installer to finish setup, create services and run the display test flow:

```shell
python3 installer.py
```

The installer can:

- install or repair dependencies
- create `inkycal.service`
- create `inkycal-webui.service`
- guide you through a timed display test
- repair common permission mistakes

## 7. Start Inkycal
```shell
venv/bin/python inky_run.py
```
If everything is set up correctly:
* Inkycal loads your modules
* Renders a full e-paper image
* Displays it on your hardware

You can also validate the config without touching the display:

```shell
venv/bin/python inky_run.py --mode dry-run
```

## 8. Open the Local Web UI

If you used the installer-managed service setup, the local web UI is available separately from the main display service.

See the dedicated page:

- [Local Web UI](webui.md)

## 9. Updating Inkycal
```shell
cd ~/Inkycal
git pull
source venv/bin/activate
pip install -e .
```

Then re-run the installer if you want services and dependencies reconciled after an update:

```shell
python3 installer.py
```

## 10. Want the Easy Way? (Recommended)

If you’re using a Pi Zero (slow installation), consider InkycalOS Lite.

✔ Preinstalled dependencies
✔ SPI enabled
✔ Inkycal auto-start
✔ Faster boot / render
✔ Saves hours of installation time

Available via the GitHub Sponsor page.


