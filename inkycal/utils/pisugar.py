"""PiSugar helper class for Inkycal."""

import logging
import subprocess

from inkycal.settings import Settings

settings = Settings()

logger = logging.getLogger(__name__)


class PiSugar:

    def __init__(self):
        # replace "command" with actual command
        self.command_template = 'echo "command" | nc -q 0 127.0.0.1 8423'
        self.allowed_commands = ["get battery", "get model", "get rtc_time", "get rtc_alarm_enabled",
                                 "get rtc_alarm_time", "get alarm_repeat", "rtc_pi2rtc"]

    def _get_output(self, command):
        if command not in self.allowed_commands:
            logger.error(f"Command {command} not allowed")
            return None
        cmd = self.command_template.replace("command", command)
        try:
            result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
            if result.returncode != 0:
                print(f"Command failed with {result.stderr}")
                return None
            output = result.stdout.strip()
            return output
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return None

    def get_battery(self) -> int or None:
        """Get the battery level in percentage.

        Returns:
            int or None: The battery level in percentage or None if the command fails.
        """
        battery_output = self._get_output("get battery")
        if battery_output:
            for line in battery_output.splitlines():
                if 'battery:' in line:
                    return int(line.split(':')[1].strip())
        return None

    def get_model(self):
        """Get the PiSugar model."""
        model_output = self._get_output("get model")
        if model_output:
            for line in model_output.splitlines():
                if 'model:' in line:
                    return line.split(':')[1].strip()
        return None

    def get_rtc_time(self):
        """Get the RTC time."""
        return self._get_output("get rtc_time")

    def get_rtc_alarm_enabled(self):
        """Get the RTC alarm enabled status."""
        return self._get_output("get rtc_alarm_enabled")

    def get_rtc_alarm_time(self):
        """Get the RTC alarm time."""
        return self._get_output("get rtc_alarm_time")

    def get_alarm_repeat(self):
        """Get the alarm repeat status."""
        return self._get_output("get alarm_repeat")

    def rtc_pi2rtc(self):
        """Sync the Pi time to RTC."""
        return self._get_output("rtc_pi2rtc")


