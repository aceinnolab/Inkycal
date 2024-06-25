"""JSON Cache
Can be used to cache JSON data to disk. This is useful for caching data to survive reboots.
"""
import json
import os

from inkycal.settings import Settings

settings = Settings()


class JSONCache:
    def __init__(self, name: str, create_if_not_exists: bool = True):
        self.path = os.path.join(settings.CACHE_PATH,f"{name}.json")

        if not os.path.exists(settings.CACHE_PATH):
            os.makedirs(settings.CACHE_PATH)

        if create_if_not_exists and not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as file:
                json.dump({}, file)

    def read(self):
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def write(self, data: dict):
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, sort_keys=True)
