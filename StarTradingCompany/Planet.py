import pygame
from enum import Enum

from StarTradingCompany import Units, ResourceManager


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


_unit_placements_with_planet = {
    0: (0.45, 0.77),
    1: (0.79, 0.55),
    2: (0.07, 0.55)
}

_unit_placements_without_planet = {
    0: (0.48, 0.47),
    1: (0.39, 0.58),
    2: (0.59, 0.58)
}


def draw_cell_outline(surface, pos, offset, cell_size, color, line_width=2):
    pygame.draw.rect(surface, color, (pos, cell_size), line_width)


class CelestialObject:
    def __init__(self, type, x, y):
        self.type = type
        self.x = x
        self.y = y
        self.visible = False
        self.selected = False
        self.space_station = None
        self.anim_index = 128
        self.show_location = False
        self.name = "{:04d}.{:04d}".format(self.x, self.y)
        self.production = {}

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

    def get_units(self):
        return Units.units[(self.x, self.y)]

    def is_visible(self):
        return self.visible

    def set_visible(self, visible):
        self.visible = visible

    def is_selected(self):
        return self.selected

    def set_selected(self, selected):
        self.anim_index = 128
        self.selected = selected

    def set_space_station(
            self, space_station):
        self.space_station = space_station

    def get_space_station(self):
        return self.space_station

    def has_space_station(self):
        return self.space_station is not None

    def get_target_selected(self, mouse_pos, cell_pos, cell_size):
        if not self.is_visible:
            return None

        target = self
        units = Units.units.get_units_for((self.x, self.y))
        if units is not None and len(units) > 0:
            for index in range(0, len(units)):
                unit_pos = self.calc_unit_location(index, cell_pos, cell_size)
                if unit_pos[0] <= mouse_pos[0] <= unit_pos[0] + 16 and unit_pos[1] <= mouse_pos[1] <= unit_pos[1] + 16:
                    target = units[index]
                    break

        return target

    def calc_unit_location(self, index, cell_pos, cell_size):
        global _unit_placements_with_planet
        global _unit_placements_without_planet

        if self.type is CelestialObjectTypes.NONE:
            mods = _unit_placements_without_planet.get(index)
        else:
            mods = _unit_placements_with_planet.get(index)
        return cell_pos[0] + (cell_size[0] * mods[0]), cell_pos[1] + (cell_size[1] * mods[1])

    def draw_unit(self, surface, unit, index, cell_pos, cell_size):
        ship_image = self.resource_manager.get_image(
            unit.type.value)
        if unit.selected:
            ship_image = ship_image.copy()
            ship_image.set_colorkey((0, 0, 0))
            ship_image.fill((self.anim_index / 2, self.anim_index / 2,
                             self.anim_index / 2), special_flags=pygame.BLEND_RGB_ADD)
        surface.blit(
            ship_image, self.calc_unit_location(index, cell_pos, cell_size))

    def draw_cell(self, surface, cell_pos, cell_size):
        if self.show_location:
            text = self.resource_manager.get_font("TruenoBd", 11).render(
                "{0}:{1}".format(self.x, self.y), True, (128, 128, 255))
            surface.blit(
                text, (cell_pos[0] + (cell_size[0] * 0.4), cell_pos[1] + (cell_size[1] * 0.10)))

        if not self.is_visible():
            pygame.draw.rect(surface, (10, 10, 10), (cell_pos, cell_size))
            return

        image = self.get_image()
        if image is not None:
            img_w = image.get_size()[0]
            img_h = image.get_size()[1]

            surface.blit(image, (cell_pos[0] + ((cell_size[0] - img_w) / 2) + 1,
                                 cell_pos[1] + ((cell_size[1] - img_h) / 2)))

        units = Units.units[(self.x, self.y)]

        if len(units) > 0:
            self.draw_unit(surface, units[0], 0, cell_pos, cell_size)

        if len(units) > 1:
            self.draw_unit(surface, units[1], 1, cell_pos, cell_size)

        if len(units) > 2:
            self.draw_unit(surface, units[2], 2, cell_pos, cell_size)

        if self.has_space_station():
            ship_image = self.resource_manager.get_image(
                "space_station")
            surface.blit(ship_image, (cell_pos[0] + (cell_size[0] * 0.45),
                                      cell_pos[1] + (cell_size[1] * 0.10)))

        if self.is_selected():
            draw_cell_outline(
                surface, cell_pos, (0, 0), cell_size, (self.anim_index, self.anim_index, self.anim_index))

        self.anim_index = self.anim_index + 17
        if self.anim_index > 255:
            self.anim_index = 128

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


