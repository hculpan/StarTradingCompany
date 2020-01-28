from StarTradingCompany import Units, ResourceManager
from enum import Enum

import pygame
import random


class CelestialObjectTypes(Enum):
    NONE = 0
    HOME = 1
    RED = 2
    COPPER = 3
    GREEN = 4
    LAVA = 5
    ASTEROIDS = 6


class RawMaterials(Enum):
    Ore = 0
    Gas = 1
    Food = 2
    Water = 3
    Neodymium = 4


class ManufacturedMaterials(Enum):
    Machine_Parts = 0
    Jump_Tubes = 1
    Space_Stations = 2
    Water = 3
    Oxygen = 4
    Lasers = 5


_unit_placements = {
    0: (0.79, 0.55),
    1: (0.45, 0.77),
    2: (0.07, 0.55)
}


class CelestialObject:
    def __init__(self, type, x, y):
        self.type = type
        self.x = x
        self.y = y
        self.visible = False
        self.selected = False
        self.space_station = None
        self.anim_index = 128
        self.show_location = True
        self.resource_manager = ResourceManager.ResourceManager()

    def get_image(self):
        if self.type == CelestialObjectTypes.HOME:
            return self.resource_manager.get_image('home_planet.png')
        elif self.type == CelestialObjectTypes.RED:
            return self.resource_manager.get_image('red_planet.png')
        elif self.type == CelestialObjectTypes.COPPER:
            return self.resource_manager.get_image('copper_planet.png')
        elif self.type == CelestialObjectTypes.GREEN:
            return self.resource_manager.get_image('green_planet.png')
        elif self.type == CelestialObjectTypes.LAVA:
            return self.resource_manager.get_image('lava_planet.png')
        elif self.type == CelestialObjectTypes.ASTEROIDS:
            return self.resource_manager.get_image('asteroids.png')

    def add_unit(self, unit):
        self.units.append(unit)

    def get_units(self): return Units.units[(self.x, self.y)]

    def is_visible(self): return self.visible

    def set_visible(self, visible): self.visible = visible

    def is_selected(self): return self.selected

    def set_selected(self, selected):
        self.anim_index = 128
        self.selected = selected

    def set_space_station(
        self, space_station): self.space_station = space_station

    def get_space_station(self): return self.space_station

    def has_space_station(self): return self.space_station != None

    def get_target_selected(self, point, hex_pos, cell_size):
        if not self.is_visible:
            return None

        if point[0] >= hex_pos[0] and point[0] < hex_pos[0] + cell_size[0] and point[1] >= hex_pos[1] and point[1] < hex_pos[1] + cell_size[1]:
            index = 0
            for unit in self.get_units():
                loc = self.calc_unit_location(index, hex_pos, cell_size)
                if point[0] >= loc[0] and point[0] < loc[0] + 16 and point[1] >= loc[1] and point[1] < loc[1] + 16:
                    return unit
                index += 1

            return self

    def point_inside(self, point, hex_pos, cell_size):
        return (point[0] >= hex_pos[0] and point[0] < hex_pos[0] + cell_size[0]
                and point[1] >= hex_pos[1] and point[1] < hex_pos[1] + cell_size[1])

    def calc_unit_location(self, index, hex_pos, cell_size):
        mods = _unit_placements.get(index)
        return (hex_pos[0] + (cell_size[0] * mods[0]), hex_pos[1] + (cell_size[1] * mods[1]))

    def draw_unit(self, surface, unit, index, hex_pos, cell_size):
        global _unit_placements

        ship_image = self.resource_manager.get_image(
            unit.type.value)
        if unit.selected:
            ship_image = ship_image.copy()
            ship_image.set_colorkey((0, 0, 0))
            ship_image.fill((self.anim_index/2, self.anim_index/2,
                             self.anim_index/2), special_flags=pygame.BLEND_RGB_ADD)
        surface.blit(
            ship_image, self.calc_unit_location(index, hex_pos, cell_size))

    def draw_hex(self, surface, hex_pos, cell_size):
        if self.show_location:
            text = self.resource_manager.get_font("TruenoBd", 11).render(
                "{0}:{1}".format(self.x, self.y), True, (128, 128, 255))
            surface.blit(
                text, (hex_pos[0] + (cell_size[0] * 0.4), hex_pos[1] + (cell_size[1] * 0.05)))

        if not self.is_visible():
            return

        image = self.get_image()
        if image != None:
            img_w = image.get_size()[0]
            img_h = image.get_size()[1]

            surface.blit(image, (hex_pos[0] + ((cell_size[0] - img_w) / 2) + 1,
                                 hex_pos[1] + ((cell_size[1] - img_h) / 2) + 1))

        units = Units.units[(self.x, self.y)]

        if len(units) > 0:
            self.draw_unit(surface, units[0], 0, hex_pos, cell_size)

        if len(units) > 1:
            self.draw_unit(surface, units[1], 1, hex_pos, cell_size)

        if len(units) > 2:
            self.draw_unit(surface, units[2], 2, hex_pos, cell_size)

        if self.has_space_station():
            ship_image = self.resource_manager.get_image(
                "space_station")
            surface.blit(ship_image, (hex_pos[0] + (cell_size[0] * 0.45),
                                      hex_pos[1] + (cell_size[1] * 0.10)))

        if self.is_selected():
            self.draw_hex_outline(
                surface, hex_pos, (0, 0), cell_size, (self.anim_index, self.anim_index, self.anim_index))

        self.anim_index = self.anim_index + 17
        if self.anim_index > 255:
            self.anim_index = 128

    def draw_hex_outline(self, surface, pos, offset, cell_size, color, line_width=2):
        cell_x = pos[0]
        cell_y = pos[1]

        quarter_height = int(cell_size[1] / 4)

        pygame.draw.polygon(surface, color, [
            (cell_x + 1, cell_y + quarter_height),  # start pos
            (cell_x + int(cell_size[0] / 2) + 1, cell_y),  # left-upper
            (cell_x + cell_size[0] + 1, cell_y + \
                quarter_height),  # right-upper
            (cell_x + cell_size[0] + 1, cell_y + \
                (quarter_height * 3)),  # left side
            (cell_x + int(cell_size[0] / 2) + 1,
                cell_y + cell_size[1]),  # right-lower
            (cell_x + 1, cell_y + (quarter_height * 3))
        ], line_width)

    def get_name(self):
        if self.type == CelestialObjectTypes.HOME:
            return "Homeworld"
        else:
            return "{:02d}{:02d}".format(self.x, self.y)

    def get_mini_map_color(self):
        switcher = {
            CelestialObjectTypes.HOME: (128, 128, 255),
            CelestialObjectTypes.RED: (255, 0, 0),
            CelestialObjectTypes.COPPER: (255, 128, 255),
            CelestialObjectTypes.GREEN: (128, 255, 255),
            CelestialObjectTypes.LAVA: (255, 0, 255),
            CelestialObjectTypes.ASTEROIDS: (128, 128, 128)
        }
        return switcher.get(self.type, (0, 0, 0))

    def get_production_potential(self):
        switcher = {
            CelestialObjectTypes.HOME:
                {RawMaterials.Ore: 0,
                 RawMaterials.Food: 0,
                 RawMaterials.Water: 0,
                 RawMaterials.Gas: 0,
                 RawMaterials.Neodymium: 0},
            CelestialObjectTypes.RED:
                {RawMaterials.Ore: 1,
                 RawMaterials.Food: 0,
                 RawMaterials.Water: 1,
                 RawMaterials.Gas: 4,
                 RawMaterials.Neodymium: 0},
            CelestialObjectTypes.COPPER:
                {RawMaterials.Ore: 2,
                 RawMaterials.Food: 0,
                 RawMaterials.Water: 0,
                 RawMaterials.Gas: 2,
                 RawMaterials.Neodymium: 2},
            CelestialObjectTypes.GREEN:
                {RawMaterials.Ore: 1,
                 RawMaterials.Food: 4,
                 RawMaterials.Water: 2,
                 RawMaterials.Gas: 0,
                 RawMaterials.Neodymium: 1},
            CelestialObjectTypes.LAVA:
                {RawMaterials.Ore: 2,
                 RawMaterials.Food: 0,
                 RawMaterials.Water: 0,
                 RawMaterials.Gas: 0,
                 RawMaterials.Neodymium: 4},
            CelestialObjectTypes.ASTEROIDS:
                {RawMaterials.Ore: 4,
                 RawMaterials.Food: 0,
                 RawMaterials.Water: 0,
                 RawMaterials.Gas: 1,
                 RawMaterials.Neodymium: 2}
        }
        return switcher.get(self.type,
                            {RawMaterials.Ore: 0,
                             RawMaterials.Food: 0,
                             RawMaterials.Water: 0,
                             RawMaterials.Gas: 0,
                             RawMaterials.Neodymium: 0})

    def get_type(self):
        return self.type
