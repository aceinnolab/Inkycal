#!python3
"""
Inkycal custom Exceptions
"""


class SettingsFileNotFoundError(Exception):
    def __init__(self, message="Inkycal could not find a settings.json file. Please check the settings-file path"):
        self.message = message
        super().__init__(self.message)


class NetworkNotReachableError(Exception):
    def __init__(self, message="Inkycal could not establish a connection to the web"):
        self.message = message
        super().__init__(self.message)
