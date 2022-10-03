#!python3
import os
import unittest
from inkycal.modules import TextToDisplay as Module
from helper_functions import *

environment = get_environment()

# Set to True to preview images. Only works on Raspberry Pi OS with Desktop
use_preview = False

file_path = None

dummy_data = [
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit.', ' Donec feugiat facilisis neque vel blandit.',
    'Integer viverra dolor risus.', ' Etiam neque tellus, sollicitudin at nisi a, mollis ornare enim.',
    'Quisque sed ante eu leo dictum sagittis quis nec nisi.',
    'Suspendisse id nulla dictum, sollicitudin urna id, iaculis elit.',
    'Nulla luctus pellentesque diam, ac consequat urna molestie vitae.',
    'Donec elementum turpis eget augue laoreet, nec maximus lacus malesuada.', '\n\nEtiam eu nunc mauris.',
    'Nullam aliquam tristique leo, at dignissim turpis sodales vitae.',
    'Aenean cursus laoreet neque, sit amet semper orci tincidunt et.',
    'Proin orci urna, efficitur malesuada mattis at, pretium commodo odio.',
    'Maecenas in ante id eros aliquam porttitor quis eget est.',
    'Duis ex urna, porta nec semper nec, dignissim eu urna.', ' Quisque eleifend non magna at rutrum.',
    '\nSed at eros blandit, tempor quam et, mollis ante.', ' Etiam fringilla euismod gravida.',
    'Curabitur facilisis consectetur luctus.',
    'Integer lectus augue, convallis a consequat id, sollicitudin eget lorem.',
    'Curabitur tincidunt suscipit nibh quis mollis.',
    'Fusce cursus, orci ut maximus fringilla, velit mauris dictum est, sed ultricies ante orci viverra erat.',
    'Quisque pellentesque, mauris nec vulputate commodo, risus libero volutpat nibh, vel tristique mi neque id quam.',
    '\nVivamus blandit, dolor ut interdum sagittis, arcu tortor finibus nibh, ornare convallis dui velit quis nunc.',
    'Sed turpis justo, pellentesque eu risus scelerisque, vestibulum vulputate magna.',
    'Vivamus tincidunt sollicitudin nisl, feugiat euismod nulla consequat ut.',
    'Praesent bibendum, sapien sit amet aliquet posuere, tellus purus porta lectus, ut volutpat purus tellus tempus est.',
    'Maecenas condimentum lobortis erat nec dignissim', ' Nulla molestie posuere est',
    'Proin ultrices, nisl id luctus lacinia, augue ipsum pharetra leo, quis commodo augue dui varius urna.',
    'Morbi ultrices turpis malesuada tellus fermentum vulputate.',
    'Aliquam viverra nulla aliquam viverra gravida.', ' Pellentesque eu viverra massa.',
    'Vestibulum id nisl vehicula, aliquet dui sed, venenatis eros.',
    'Nunc iaculis, neque vitae euismod viverra, nisl mauris luctus velit, a aliquam turpis erat fringilla libero.',
    'Ut ligula elit, lacinia convallis tempus interdum, finibus ut ex.',
    'Nulla efficitur ac ligula sit amet dignissim.', ' Donec sed mi et justo venenatis faucibus.',
    'Sed tincidunt nibh erat, in vestibulum purus consequat eget.',
    '\nNulla iaculis volutpat orci id efficitur.', ' Vivamus vehicula sit amet augue tristique dignissim.',
    'Praesent eget nulla est.', ' Integer nec diam fermentum, convallis metus lacinia, lobortis mauris.',
    'Nulla venenatis metus fringilla, lacinia sem nec, pharetra sapien.',
    'Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas.',
    'Duis facilisis sapien est, a elementum lorem maximus ut.'
]

tests = [
    {
        "position": 1,
        "name": "TextToFile",
        "config": {
            "size": [500, 100],
            "filepath": file_path,
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en"
        }
    },
    {
        "position": 1,
        "name": "TextToFile",
        "config": {
            "size": [500, 400],
            "filepath": file_path,
            "padding_x": 10,
            "padding_y": 10,
            "fontsize": 12,
            "language": "en"
        }
    },
]


class TestTextToDisplay(unittest.TestCase):
    def test_get_config(self):
        print('getting data for web-ui...', end="")
        Module.get_config()
        print('OK')

    def test_generate_image(self):
        delete_file_after_parse = False

        if not file_path:
            delete_file_after_parse = True
            print("Filepath does not exist. Creating dummy file")

            tmp_path = "tmp.txt"
            with open(tmp_path, mode="w") as file:
                file.writelines(dummy_data)

            # update tests with new temp path
            for test in tests:
                test["config"]["filepath"] = tmp_path

        else:
            make_request = True if file_path.startswith("https://") else False
            if not make_request and not os.path.exists(file_path):
                raise FileNotFoundError("Your text file could not be found")

        for test in tests:
            print(f'test {tests.index(test) + 1} generating image..')
            module = Module(test)
            im_black, im_colour = module.generate_image()
            print('OK')
            if use_preview and environment == 'Raspberry':
                preview(merge(im_black, im_colour))
            im = merge(im_black, im_colour)
            im.show()

        if delete_file_after_parse:
            print("cleaning up temp file")
            os.remove("tmp.txt")


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.level = logging.DEBUG
    logger.addHandler(logging.StreamHandler(sys.stdout))

    unittest.main()
