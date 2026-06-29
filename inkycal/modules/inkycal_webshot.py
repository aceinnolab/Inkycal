"""
Webshot module for Inkycal
by https://github.com/worstface
"""
import logging
import os
import shutil
import subprocess
from typing import Optional

from PIL import Image

from inkycal.settings import Settings
from inkycal.utils.functions import internet_available
from inkycal.utils.inky_image import Inkyimage as Images, image_to_palette
from inkycal.modules.template import InkycalModule

logger = logging.getLogger(__name__)

settings = Settings()


def _find_browser_binary() -> Optional[str]:
    candidates = [
        os.getenv("INKYCAL_BROWSER_BIN"),
        "chromium",
        "chromium-browser",
        "google-chrome",
        "google-chrome-stable",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]

    for candidate in candidates:
        if not candidate:
            continue
        if os.path.isabs(candidate) and os.path.exists(candidate):
            return candidate
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def _find_chromedriver_binary() -> Optional[str]:
    candidates = [
        os.getenv("INKYCAL_CHROMEDRIVER_BIN"),
        "chromedriver",
        "/usr/bin/chromedriver",
    ]
    for candidate in candidates:
        if not candidate:
            continue
        if os.path.isabs(candidate) and os.path.exists(candidate):
            return candidate
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None

class Webshot(InkycalModule):
    name = "Webshot - Displays screenshots of webpages"

    # required parameters
    requires = {

        "url": {
            "label": "Please enter the url",
        },
        "palette": {
            "label": "Which color palette should be used for the webshots?",
            "options": ["bw", "bwr", "bwy"]
        }
    }

    optional = {

        "crop_x": {
            "label": "Please enter the crop x-position",
        },
        "crop_y": {
            "label": "Please enter the crop y-position",
        },
        "crop_w": {
            "label": "Please enter the crop width",
        },
        "crop_h": {
            "label": "Please enter the crop height",
        },
        "rotation": {
            "label": "Please enter the rotation. Must be either 0, 90, 180 or 270",
        },
        "wait_time": {
            "label": "Wait time in seconds for JS-heavy pages before screenshot",
        },
        "dither": {
            "label": "Use dithering when mapping the screenshot to the selected palette?",
            "options": [True, False],
        },
    }

    def __init__(self, config):

        super().__init__(config)

        config = config['config']

        self.url = config['url']
        self.palette = config['palette']

        if "crop_h" in config and isinstance(config["crop_h"], str):
            self.crop_h = int(config["crop_h"])
        else:
            self.crop_h = 2000

        if "crop_w" in config and isinstance(config["crop_w"], str):
            self.crop_w = int(config["crop_w"])
        else:
            self.crop_w = 2000

        if "crop_x" in config and isinstance(config["crop_x"], str):
            self.crop_x = int(config["crop_x"])
        else:
            self.crop_x = 0

        if "crop_y" in config and isinstance(config["crop_y"], str):
            self.crop_y = int(config["crop_y"])
        else:
            self.crop_y = 0

        self.rotation = 0
        if "rotation" in config:
            self.rotation = int(config["rotation"])
            if self.rotation not in [0, 90, 180, 270]:
                raise Exception("Rotation must be either 0, 90, 180 or 270")

        self.wait_time = 2
        if "wait_time" in config and config["wait_time"]:
            self.wait_time = int(config["wait_time"])

        self.dither = True
        if "dither" in config:
            dither_value = config["dither"]
            if isinstance(dither_value, str):
                self.dither = dither_value.strip().lower() in {"true", "1", "yes", "on"}
            else:
                self.dither = bool(dither_value)

        # give an OK message
        logger.debug(f'Inkycal webshot loaded')

    @staticmethod
    def is_backend_available() -> bool:
        return _find_browser_binary() is not None

    def _capture_webshot(self, output_path: str) -> None:
        browser = _find_browser_binary()

        if browser is None:
            logger.warning("No Chromium/Chrome executable found; trying Selenium fallback")
            self._capture_webshot_with_selenium(output_path)
            return

        # Render a larger viewport first, then crop to keep previous behavior.
        viewport_w = max(self.crop_w + self.crop_x, 320)
        viewport_h = max(self.crop_h + self.crop_y, 320)

        command = [
            browser,
            "--headless",
            "--disable-gpu",
            "--hide-scrollbars",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions",
            "--run-all-compositor-stages-before-draw",
            f"--virtual-time-budget={max(1000, self.wait_time * 1000)}",
            f"--window-size={viewport_w},{viewport_h}",
            f"--screenshot={output_path}",
            self.url,
        ]

        if os.name != "nt":
            command.insert(1, "--no-sandbox")

        try:
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            logger.warning("Direct headless browser capture failed; trying Selenium fallback")
            self._capture_webshot_with_selenium(output_path)
            return

        with Image.open(output_path) as shot:
            x0 = min(max(0, self.crop_x), shot.width)
            y0 = min(max(0, self.crop_y), shot.height)
            x1 = min(shot.width, max(x0 + 1, x0 + self.crop_w))
            y1 = min(shot.height, max(y0 + 1, y0 + self.crop_h))
            shot.crop((x0, y0, x1, y1)).save(output_path, "PNG")

    def _capture_webshot_with_selenium(self, output_path: str) -> None:
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
        except ImportError as error:
            raise FileNotFoundError(
                "Selenium fallback is unavailable. Install selenium and chromium/chromedriver "
                "or set INKYCAL_BROWSER_BIN to a Chromium executable."
            ) from error

        browser = _find_browser_binary()
        driver_bin = _find_chromedriver_binary()
        if not browser or not driver_bin:
            raise FileNotFoundError(
                "No usable Chromium + chromedriver setup found. Install chromium and chromedriver "
                "or set INKYCAL_BROWSER_BIN and INKYCAL_CHROMEDRIVER_BIN."
            )

        viewport_w = max(self.crop_w + self.crop_x, 320)
        viewport_h = max(self.crop_h + self.crop_y, 320)

        options = Options()
        options.binary_location = browser
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--hide-scrollbars")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"--window-size={viewport_w},{viewport_h}")

        service = Service(executable_path=driver_bin)
        driver = webdriver.Chrome(service=service, options=options)
        try:
            driver.get(self.url)
            if self.wait_time > 0:
                import time
                time.sleep(self.wait_time)
            driver.save_screenshot(output_path)
        finally:
            driver.quit()

        with Image.open(output_path) as shot:
            x0 = min(max(0, self.crop_x), shot.width)
            y0 = min(max(0, self.crop_y), shot.height)
            x1 = min(shot.width, max(x0 + 1, x0 + self.crop_w))
            y1 = min(shot.height, max(y0 + 1, y0 + self.crop_h))
            shot.crop((x0, y0, x1, y1)).save(output_path, "PNG")

    def generate_image(self):
        """Generate image for this module"""

        # Create tmp path
        tmpFolder = settings.TEMPORARY_FOLDER

        if not os.path.exists(tmpFolder):
            print(f"Creating tmp directory {tmpFolder}")
            os.mkdir(tmpFolder)

        # Define new image size with respect to padding
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))
        if self.rotation in (90, 270):
            im_width, im_height = im_height, im_width
        im_size = im_width, im_height
        logger.debug('image size: {} x {} px'.format(im_width, im_height))

        # Create an image for black pixels and one for coloured pixels (required)
        im_black = Image.new('RGB', size=im_size, color='white')
        im_colour = Image.new('RGB', size=im_size, color='white')

        # Check if internet is available
        if internet_available():
            logger.info('Connection test passed')
        else:
            logger.error("Network not reachable. Please check your connection.")
            raise Exception('Network could not be reached :/')

        logger.info(
            f'preparing webshot from {self.url}... cropH{self.crop_h} cropW{self.crop_w} cropX{self.crop_x} cropY{self.crop_y}')

        logger.info(f'getting webshot from {self.url}...')

        try:
            self._capture_webshot(f"{tmpFolder}/webshot.png")
        except subprocess.CalledProcessError as error:
            logger.error(error.stderr.decode("utf-8", errors="ignore"))
            raise Exception("Could not get webshot. Make sure Chromium can run in headless mode.")
        except FileNotFoundError as error:
            raise Exception(str(error))


        logger.info(f'got webshot...')

        webshotSpaceBlack = Image.new('RGBA', (im_width, im_height), (255, 255, 255, 255))
        webshotSpaceColour = Image.new('RGBA', (im_width, im_height), (255, 255, 255, 255))

        im = Images()
        im.load(f'{tmpFolder}/webshot.png')
        im.remove_alpha()

        imageAspectRatio = im_width / im_height
        webshotAspectRatio = im.image.width / im.image.height

        if webshotAspectRatio > imageAspectRatio:
            imageScale = im_width / im.image.width
        else:
            imageScale = im_height / im.image.height

        webshotHeight = int(im.image.height * imageScale)

        im.resize(width=int(im.image.width * imageScale), height=webshotHeight)

        im_webshot_black, im_webshot_colour = image_to_palette(
            im.image.convert("RGB"),
            self.palette,
            dither=self.dither,
        )

        webshotCenterPosY = int((im_height / 2) - (im.image.height / 2))

        centerPosX = int((im_width / 2) - (im.image.width / 2))


        if self.rotation != 0:
            webshotSpaceBlack.paste(im_webshot_black, (centerPosX, webshotCenterPosY))
            im_black.paste(webshotSpaceBlack)
            im_black = im_black.rotate(self.rotation, expand=True)

            webshotSpaceColour.paste(im_webshot_colour, (centerPosX, webshotCenterPosY))
            im_colour.paste(webshotSpaceColour)
            im_colour = im_colour.rotate(self.rotation, expand=True)
        else:
            webshotSpaceBlack.paste(im_webshot_black, (centerPosX, webshotCenterPosY))
            im_black.paste(webshotSpaceBlack)

            webshotSpaceColour.paste(im_webshot_colour, (centerPosX, webshotCenterPosY))
            im_colour.paste(webshotSpaceColour)

        im.clear()
        logger.info(f'added webshot image')

        # Save image of black and colour channel in image-folder
        return im_black, im_colour