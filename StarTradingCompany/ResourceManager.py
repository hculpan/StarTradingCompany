from StarTradingCompany import SpriteSheet

import pygame
import os
import platform
import sys

_image_library = {}

_font_library = {}

_ship_sprite_info = {
    "Explorer": (28, 42 + 20, 16, 16),
    #    "settler": (28 + (20 * 4), 42 + (20 * 4), 16, 16),
    "Builder": (28, 42 + (20 * 5), 16, 16),
    "Fighter": (28 + (20 * 4), 42 + (20 * 3), 16, 16),
    "Freighter": (28 + (20 * 4), 42 + (20 * 9), 16, 16),
    "space_station": (28 + 20, 42 + (20 * 18), 16, 16)
}

_ship_sprite_sheet = None

IMAGES_PATH_PREFIX = 'Resources' + os.sep + 'images' + os.sep
FONT_PATH_PREFIX = 'Resources' + os.sep + 'fonts' + os.sep
if platform.system() == "Darwin" and sys.executable.endswith("/app"):
    IMAGES_PATH_PREFIX = sys.executable[:-4] + os.sep + IMAGES_PATH_PREFIX
    FONT_PATH_PREFIX = sys.executable[:-4] + os.sep + FONT_PATH_PREFIX


class ResourceManager:
    def __init__(self):
        global _ship_sprite_sheet

        if _ship_sprite_sheet == None:
            _ship_sprite_sheet = SpriteSheet.SpriteSheet(
                IMAGES_PATH_PREFIX + '16ShipCollection.png')

    def get_image(self, path):
        global _image_library
        global _ship_sprite_info
        global _ship_sprite_sheet

        image = _image_library.get(path)
        if image == None and path in _ship_sprite_info:
            image = _ship_sprite_sheet.image_at((_ship_sprite_info.get(path)))
            image = pygame.transform.flip(image, True, False)
            image.set_colorkey((0, 0, 0))
            _image_library[path] = image
        elif image == None:
            canonicalized_path = IMAGES_PATH_PREFIX + path
            image = pygame.image.load(canonicalized_path)
            _image_library[path] = image

        return image

    def get_font(self, font_name, font_size):
        global _font_library
        font = _font_library.get((font_name, font_size))
        if font == None:
            font = pygame.font.Font(
                FONT_PATH_PREFIX + font_name + ".otf", font_size)
            _font_library[(font_name, font_size)] = font
        return font
