"""
Webshot module for Inkycal
by https://github.com/worstface
"""

from htmlwebshot import WebShot

from inkycal.custom import *
from inkycal.modules.inky_image import Inkyimage as Images, image_to_palette
from inkycal.modules.template import inkycal_module

logger = logging.getLogger(__name__)


class Webshot(inkycal_module):
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

        # give an OK message
        logger.debug(f'Inkycal webshot loaded')

    def generate_image(self):
        """Generate image for this module"""

        # Create tmp path
        tmpFolder = "temp"

        if not os.path.exists(tmpFolder):
            print(f"Creating tmp directory {tmpFolder}")
            os.mkdir(tmpFolder)

        # Define new image size with respect to padding
        im_width = int(self.width - (2 * self.padding_left))
        im_height = int(self.height - (2 * self.padding_top))
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

        shot = WebShot(size=(im_height, im_width))

        shot.params = {
            "--crop-x": self.crop_x,
            "--crop-y": self.crop_y,
            "--crop-w": self.crop_w,
            "--crop-h": self.crop_h,
        }

        logger.info(f'getting webshot from {self.url}...')

        try:
            shot.create_pic(url=self.url, output=f"{tmpFolder}/webshot.png")
        except:
            print(traceback.format_exc())
            print("If you have not already installed wkhtmltopdf, please use: sudo apt-get install wkhtmltopdf. See here for more details: https://github.com/1Danish-00/htmlwebshot/")
            raise Exception('Could not get webshot :/')


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

        im_webshot_black, im_webshot_colour = image_to_palette(im.image.convert("RGB"), self.palette)

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
