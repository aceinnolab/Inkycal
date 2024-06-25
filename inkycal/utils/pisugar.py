"""PiSugar helper class for Inkycal."""

import logging
import subprocess

from inkycal.settings import Settings
import arrow

settings = Settings()

logger = logging.getLogger(__name__)


class PiSugar:

    def __init__(self):
        # replace "command" with actual command
        self.command_template = 'echo "command" | nc -q 0 127.0.0.1 8423'
        self.allowed_commands = ["get battery", "get model", "get rtc_time", "get rtc_alarm_enabled",
                                 "get rtc_alarm_time", "get alarm_repeat", "rtc_pi2rtc", "rtc_alarm_set"]

    def _get_output(self, command, param=None):
        if command not in self.allowed_commands:
            logger.error(f"Command {command} not allowed")
            return None
        if param:
            cmd = self.command_template.replace("command", f"{command} {param}")
        else:
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

    def get_battery(self) -> float or None:
        """Get the battery level in percentage.

        Returns:
            int or None: The battery level in percentage or None if the command fails.
        """
        battery_output = self._get_output("get battery")
        if battery_output:
            for line in battery_output.splitlines():
                if 'battery:' in line:
                    return float(line.split(':')[1].strip())
        return None

    def get_model(self) -> str or None:
        """Get the PiSugar model."""
        model_output = self._get_output("get model")
        if model_output:
            for line in model_output.splitlines():
                if 'model:' in line:
                    return line.split(':')[1].strip()
        return None

    def get_rtc_time(self) -> arrow.arrow or None:
        """Get the RTC time."""
        result = self._get_output("get rtc_time")
        if result:
            rtc_time = result.split("rtc_time: ")[1].strip()
            return arrow.get(rtc_time)
        return None

    def get_rtc_alarm_enabled(self) -> str or None:
        """Get the RTC alarm enabled status."""
        result = self._get_output("get rtc_alarm_enabled")
        if result:
            second_line = result.splitlines()[1]
            output = second_line.split('rtc_alarm_enabled: ')[1].strip()
            return True if output == "true" else False
        return None

    def get_rtc_alarm_time(self) -> arrow.arrow or None:
        """Get the RTC alarm time."""
        result = self._get_output("get rtc_alarm_time")
        if result:
            alarm_time = result.split('rtc_alarm_time: ')[1].strip()
            return arrow.get(alarm_time)
        return None

    def get_alarm_repeat(self) -> dict or None:
        """Get the alarm repeat status.

        Returns:
            dict or None: A dictionary with the alarm repeating days or None if the command fails.
        """
        result = self._get_output("get alarm_repeat")
        if result:
            repeating_days = f"{int(result.split('alarm_repeat: ')[1].strip()):8b}".strip()
            data = {"Monday": False, "Tuesday": False, "Wednesday": False, "Thursday": False, "Friday": False,
                    "Saturday": False, "Sunday": False}
            if repeating_days[0] == "1":
                data["Monday"] = True
            if repeating_days[1] == "1":
                data["Tuesday"] = True
            if repeating_days[2] == "1":
                data["Wednesday"] = True
            if repeating_days[3] == "1":
                data["Thursday"] = True
            if repeating_days[4] == "1":
                data["Friday"] = True
            if repeating_days[5] == "1":
                data["Saturday"] = True
            if repeating_days[6] == "1":
                data["Sunday"] = True
            return data
        return None

    def rtc_pi2rtc(self) -> bool:
        """Sync the Pi time to RTC.

        Returns:
            bool: True if the sync was successful, False otherwise.
        """
        result = self._get_output("rtc_pi2rtc")
        if result:
            status = result.split('rtc_pi2rtc: ')[1].strip()
            if status == "done":
                return True
        return False

    def rtc_alarm_set(self, time: arrow.arrow, repeat:int=127) -> bool:
        """Set the RTC alarm time.

        Args:
            time (arrow.arrow): The alarm time in ISO 8601 format.
            repeat: int representing 7-bit binary number of repeating days. e.g. 127 = 1111111 = repeat every day

        Returns:
            bool: True if the alarm was set successfully, False otherwise.
        """
        iso_format = time.isoformat()
        result = self._get_output("rtc_alarm_set", f"{iso_format } {repeat}")
        if result:
            status = result.split('rtc_alarm_set: ')[1].strip()
            if status == "done":
                return True
        return False


