# 🔋 PiSugar Battery Support

PiSugar is a battery pack for the Raspberry Pi that enables weeks of battery-powered operation, perfect for true wireless InkyCal deployments.

## Overview

PiSugar boards provide:
- **Battery-powered operation** without USB cable
- **Deep-sleep scheduling** to extend battery life
- **Auto-shutdown** after each render
- **Auto-wake timer** for scheduled updates
- **Battery status monitoring** via web UI

**⚠️ Beta note:** PiSugar support is working but still considered beta. These instructions should be carefully followed. Support is not officially affiliated with PiSugar.

---

## Prerequisites

- A compatible **Raspberry Pi Zero** (strongly recommended for low power draw)
- **PiSugar 3** or any compatible PiSugar model
- Working Inkycal installation
- SSH access to the device

---

## Step 1: Install PiSugar Driver

Run the PiSugar installer **without sudo**:

```bash
wget https://cdn.pisugar.com/release/pisugar-power-manager.sh
bash pisugar-power-manager.sh -c release
sudo systemctl enable pisugar-server
```

This installs the PiSugar web-UI and enables the daemon to start automatically.

### Verify Installation

Open `http://<your-pi-ip>:8421` in a browser to confirm the PiSugar web UI is running. You should see:
- Current battery voltage
- Battery percentage
- Connected status

---

## Step 2: Test Basic Inkycal

Before integrating PiSugar, verify Inkycal works normally:

```bash
cd ~/Inkycal
source venv/bin/activate
python inky_run.py
```

You should see your dashboard rendered on the display. If this fails, troubleshoot basic Inkycal setup first (display model, SPI, settings.json).

---

## Step 3: Enable PiSugar Mode in Settings

In your `settings.json`, add or set:

```json
{
  "use_pi_sugar": true
}
```

Then run Inkycal again:

```bash
cd ~/Inkycal
source venv/bin/activate
python inky_run.py
```

You should see additional output mentioning:
- Battery status (voltage, percentage)
- PiSugar wakeup timer
- Current system time

If you see errors about PiSugar connection, verify:
1. PiSugar server is running: `systemctl status pisugar-server`
2. `/tmp/pisugar-server` socket exists
3. Check PiSugar web UI for hardware connection

---

## Step 4: Enable Auto-Shutdown (Optional but Recommended)

To maximize battery life, enable auto-shutdown. This causes Inkycal to power off the Pi immediately after rendering, waking automatically at the next scheduled update.

**Via settings.json:**

```json
{
  "use_pi_sugar": true,
  "shutdown_after_run": true
}
```

Then test:

```bash
python inky_run.py
```

The system should:
1. Render to the display
2. Set a wakeup timer on PiSugar
3. Power down

If successful, the Pi will remain off until the timer fires.

---

## Battery Life Estimation

### Example Calculation (Pi Zero W + PiSugar 3)

**Assumptions:**
- PiSugar 3: 1200 mAh battery
- Efficiency loss: 20% (practical: ~960 mAh usable)
- Pi Zero W + display: ~230 mA during 3.5 minute boot/render
- Idle current during sleep: ~80 µA

**Per update:**
- Energy drawn: 3.83 mA/min × 3.5 min = ~13.5 mA
- Updates possible: 960 mAh ÷ 13.5 mA = **~71 updates**

**At different refresh intervals:**
- 1 update/day: ~71 days ✓
- 2 updates/day: ~35 days ✓
- 3 updates/day: ~24 days ✓

**Real-world note:** Calibration cycles and cold weather can reduce this by 20–30%.

---

## Important Notes

### ⚠️ Raspbian Sudo Configuration

Auto-shutdown requires passwordless sudo access to `systemctl` and `shutdown` commands. This is the **default** on Raspberry Pi OS but is a security consideration:

```bash
sudo visudo
```

Ensure these lines exist (usually present by default):

```
%sudo ALL=(ALL) NOPASSWD: /bin/systemctl
%sudo ALL=(ALL) NOPASSWD: /sbin/shutdown
```

### 🔋 Minimum Pi Zero Recommendation

- **Pi Zero W** (200 mA idle) ← **recommended**
- Pi Zero 2 W (higher idle, faster boot)
- Pi 3 (not recommended; higher power draw)

### 📅 Update Scheduling

PiSugar can wake the device at only **one scheduled time**. Inkycal resets this timer on each run, so:

- **Single daily update:** Runs reliably at same time each day
- **Multiple updates per day:** Set cron/systemd timer to wake at desired intervals, Inkycal will update and reschedule

Recommended: 1–3 updates per day for best battery life.

### 🔧 Calibration in PiSugar Mode

E-paper display calibration is **disabled** in PiSugar mode to save power and time. If ghosting appears:

1. Temporarily disable auto-shutdown:
   ```json
   "shutdown_after_run": false
   ```

2. Run Inkycal manually (will include calibration)

3. Re-enable auto-shutdown after verifying display looks good

---

## Troubleshooting

### ❌ PiSugar Server Not Responding

```bash
sudo systemctl restart pisugar-server
```

Check socket:

```bash
ls -la /tmp/pisugar-server
```

### ❌ Wakeup Timer Not Setting

- Verify system time is correct: `date`
- Check PiSugar web UI for timer field
- Ensure `shutdown_after_run: true` is in `settings.json`

### ❌ High Idle Current Despite Auto-Shutdown

- Check background processes: `ps aux`
- Ensure services are actually stopping: `systemctl status inkycal.service`
- Verify HDMI is disabled if not in use (saves ~50 mA):
  ```bash
  tvservice -o
  ```

### ❌ Device Won't Wake Up

- Check PiSugar battery level (may be too low to wake)
- Verify wakeup time is in the future
- Try manually waking via PiSugar web UI button
- Check dmesg logs: `dmesg | tail -20`

---

## Tips & Tricks

### 💡 Disable HDMI to Save Power

If you're not using HDMI output:

```bash
echo "hdmi_blanking=2" | sudo tee -a /boot/firmware/config.txt
sudo reboot
```

Saves ~50 mA during sleep.

### 💡 Monitor Battery Health

Periodically check PiSugar web UI or SSH in and run:

```bash
cat /tmp/pisugar_state
```

### 💡 Scheduled vs. Manual Wake

- **Scheduled:** Set interval in `settings.json`, PiSugar wakes automatically
- **Manual:** Press button on PiSugar to wake manually, run `inky_run.py` immediately

### 💡 Testing Before Going Wireless

Before deploying:

1. Run 5 complete cycles with auto-shutdown enabled
2. Monitor battery in PiSugar web UI after each cycle
3. Verify display renders correctly each time
4. Check Pi logs for errors: `journalctl -u inkycal.service -n 50`

---

## Advanced: Custom Wake Schedules

If you need multiple updates per day, use `systemd` timers in addition to PiSugar:

1. Create a custom timer:
   ```bash
   sudo systemctl edit --force inkycal-wakeup.timer
   ```

2. Add:
   ```ini
   [Unit]
   Description=Inkycal PiSugar Wakeup
   
   [Timer]
   OnCalendar=*-*-* 08:00:00
   OnCalendar=*-*-* 12:00:00
   OnCalendar=*-*-* 20:00:00
   Persistent=true
   
   [Install]
   WantedBy=timers.target
   ```

3. Enable:
   ```bash
   sudo systemctl enable --now inkycal-wakeup.timer
   ```

Each trigger will wake the device, Inkycal will render, then PiSugar will reschedule the next wake cycle.

---

## Safety & Best Practices

✔ **Do:**
- Test thoroughly in plugged-in mode first
- Monitor battery level regularly
- Keep firmware updated (check PiSugar site)
- Document your update schedule

❌ **Don't:**
- Assume 1200 mAh devices can run for months (typically 2–8 weeks)
- Modify PiSugar driver code unless you understand power management
- Deploy without testing calibration and ghosting first
- Leave device in PiSugar mode if display shows artifacts

---

## Support

If you encounter issues:

1. **Check PiSugar documentation:** https://pisugar.com/
2. **Verify Inkycal works without PiSugar** first
3. **Share logs on Discord:** https://discord.gg/sHYKeSM
4. **Open a GitHub issue** if it's Inkycal-specific

---

## Further Reading

- [PiSugar Official Docs](https://pisugar.com/)
- [Inkycal Discord Support](https://discord.gg/sHYKeSM)
- [Raspberry Pi Power Management](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply)
