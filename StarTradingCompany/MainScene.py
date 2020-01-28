from StarTradingCompany import SceneBase, Sector, Planet, Units, GameState, ResourceManager
import pygame
import random
from StarTradingCompany.Planet import *


class MainScene(SceneBase.SceneBase):
    def __init__(self, width, height):
        super().__init__(width, height)

        self.next = self
        self.MINI_MAP_SCALE = 4

        self.grid_base_x = 10
        self.grid_base_y = 110
        self.grid_cell_width = 105
        self.grid_cell_height = 120
        self.grid_view_cols = 8
        self.grid_view_rows = 8

        self.sector = Sector.Sector()
        self.sector_size = self.sector.get_size()
        self.mini_map_x = width - \
            (self.sector_size[0] * self.MINI_MAP_SCALE) - 10
        self.mini_map_y = 10
        self.mini_map_surface = None

        self.view_x = int(self.sector_size[0] / 2 - (self.grid_view_cols / 2))
        self.view_y = int(self.sector_size[1] / 2 - (self.grid_view_rows / 2))

        self.last_selected = None

        self.is_blue = True
        self.done = False

        self.resource_manager = ResourceManager.ResourceManager()

        surface = pygame.Surface((1029, 1029))
        for x in range(0, 8):
            for y in range(0, 8):
                self.draw_hex(surface, (x, y), (0, 0),
                              (self.grid_cell_width, self.grid_cell_height), (128, 128, 128))

        self.image_grid = surface

    def draw_top_bar(self, screen):
        global game_state

        text = self.resource_manager.get_font("TruenoBd", 24).render(
            "Turn {0}".format(GameState.game_state.turn), True, (128, 128, 255))
        screen.blit(text, (20, 20))

    def draw_hex(self, surface, pos, offset, cell_size, color):
        x = pos[0]
        y = pos[1]

        quarter_height = int(cell_size[1] / 4)

        cell_x = offset[0] + (cell_size[0] * x)
        cell_y = offset[1] + (cell_size[1] * y) - (y * quarter_height)

        if (y - self.view_y) % 2 != 0:
            cell_x += int(cell_size[0] / 2)
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
        ], 2)

    def handle_mouse(self, event):
        pos = pygame.mouse.get_pos()
        if pos[0] >= self.mini_map_x and \
                pos[0] <= self.sector_size[0] * self.MINI_MAP_SCALE + self.mini_map_x and \
                pos[1] >= self.mini_map_y and \
                pos[1] <= self.sector_size[1] * self.MINI_MAP_SCALE + self.mini_map_y:
            self.selected_x = -1
            self.selected_y = -1
            self.view_x = int(
                (pos[0] - self.mini_map_x) / self.MINI_MAP_SCALE - self.grid_view_cols / 2)
            self.view_y = int(
                (pos[1] - self.mini_map_y) / self.MINI_MAP_SCALE - self.grid_view_rows / 2)
            if self.view_x < 0:
                self.view_x = 0
            elif self.view_x + self.grid_view_cols > self.sector_size[0]:
                self.view_x = self.sector_size[0] - self.grid_view_cols
            if self.view_y < 0:
                self.view_y = 0
            elif self.view_y + self.grid_view_rows > self.sector_size[1]:
                self.view_y = self.sector_size[1] - self.grid_view_rows
        else:
            selected = self.find_selected_hex(pos)
            if selected != None:
                if self.last_selected == selected:
                    selected.selected = False
                    self.last_selected = None
                elif self.last_selected != None:
                    selected.selected = True
                    self.last_selected.selected = False
                    self.last_selected = selected
                else:
                    selected.selected = True
                    self.last_selected = selected

    def find_selected_hex(self, pos):
        for x in range(0, self.grid_view_cols):
            for y in range(0, self.grid_view_rows):
                planet = self.sector.get_planet(
                    x + self.view_x, y + self.view_y)
                target = planet.get_target_selected(pos, self.calculate_pos_for_hex(
                    x, y), (self.grid_cell_width, self.grid_cell_height))
                if target != None:
                    return target
        return None

    def move_unit_to(self, unit, delta):
        oldloc = unit.position
        newloc = Units.units.move_unit(
            self.last_selected, delta, self.sector.get_size())
        if oldloc != newloc:
            unit.moves_remaining -= 1
        planet = self.sector.get_planet(newloc[0], newloc[1])
        if unit.type == Units.ShipType.Explorer:
            self.sector.reveal_neighbors(newloc[0], newloc[1])
        else:
            planet.set_visible(True)
        self.mini_map_surface = None
        unit.moved = True

        # Now move view if necessary
        if newloc[0] - self.view_x < 1:
            self.view_x -= 1
        elif newloc[0] - self.view_x >= self.grid_view_cols - 1:
            self.view_x += 1
        if newloc[1] - self.view_y < 1:
            self.view_y -= 1
        elif newloc[1] - self.view_y >= self.grid_view_rows - 1:
            self.view_y += 1

        if unit.moves_remaining <= 0:
            self.select_next_unit()

    def process_input_for_unit(self, events, pressed_keys):
        if pressed_keys[pygame.K_KP9]:
            if self.last_selected.position[1] % 2 == 0:
                self.move_unit_to(self.last_selected, (0, -1))
            else:
                self.move_unit_to(self.last_selected, (1, -1))
        if pressed_keys[pygame.K_KP7]:
            if self.last_selected.position[1] % 2 == 0:
                self.move_unit_to(self.last_selected, (-1, -1))
            else:
                self.move_unit_to(self.last_selected, (0, -1))
        if pressed_keys[pygame.K_KP3]:
            if self.last_selected.position[1] % 2 == 0:
                self.move_unit_to(self.last_selected, (0, 1))
            else:
                self.move_unit_to(self.last_selected, (1, 1))
        if pressed_keys[pygame.K_KP1]:
            if self.last_selected.position[1] % 2 == 0:
                self.move_unit_to(self.last_selected, (-1, 1))
            else:
                self.move_unit_to(self.last_selected, (0, 1))
        if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_KP4]:
            self.move_unit_to(self.last_selected, (-1, 0))
        if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_KP6]:
            self.move_unit_to(self.last_selected, (1, 0))
        if pressed_keys[pygame.K_SPACE]:
            self.last_selected.moved = True
            self.select_next_unit()

    def process_input_for_hex(self, events, pressed_keys):
        if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_KP8] and self.view_y > 0:
            self.view_y -= 2
        if pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_KP2] and self.view_y + self.grid_view_rows < self.sector_size[1]:
            self.view_y += 2
        if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_KP4] and self.view_x > 0:
            self.view_x -= 1
        if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_KP6] and self.view_x + self.grid_view_cols < self.sector_size[0]:
            self.view_x += 1

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse(event)

        if self.last_selected != None and isinstance(self.last_selected, Units.Unit):
            self.process_input_for_unit(events, pressed_keys)
        else:
            self.process_input_for_hex(events, pressed_keys)

    def calculate_pos_for_hex(self, vx, vy):
        basex = self.grid_base_x + (vx * self.grid_cell_width)
        basey = self.grid_base_y + \
            (vy * self.grid_cell_height) - ((self.grid_cell_height / 4) * vy)

        # odd-numbered rows are indented half a hex
        if vy % 2 != 0:
            basex += self.grid_cell_width / 2

        return (int(basex), int(basey))

    def display_image_on_grid(self, planet, vx, vy):
        if planet == None:
            return

        planet.draw_hex(self.screen, self.calculate_pos_for_hex(vx, vy),
                        (self.grid_cell_width, self.grid_cell_height))

    def display_planet_info(self, planet):
        if planet != None and planet.get_type() != CelestialObjectTypes.NONE:
            yloc = int(self.sector_size[1] * self.MINI_MAP_SCALE + 32)

            # display name
            if (planet.get_type() == CelestialObjectTypes.ASTEROIDS):
                text = self.resource_manager.get_font("TruenoBd", 18).render(
                    "Asteroids: " + planet.get_name(), True, (128, 128, 255))
            else:
                text = self.resource_manager.get_font("TruenoBd", 18).render(
                    "Planet: " + planet.get_name(), True, (128, 128, 255))
            self.screen.blit(text, (950, yloc))
            yloc += 30

            # display units
            units = planet.get_units()
            for unit in units:
                image = self.resource_manager.get_image(unit.get_type().value)
                self.screen.blit(image, (950, yloc))
                text = self.resource_manager.get_font("TruenoBd", 12).render(
                    "{0} {1}".format(
                        str(unit.get_type())[9:], unit.get_name()), True, (200, 200, 200))
                self.screen.blit(text, (974, yloc))
                yloc += 17

            # display space station info
            if planet.has_space_station():
                yloc += 5
                image = self.resource_manager.get_image("space_station")
                self.screen.blit(image, (950, yloc))
                text = self.resource_manager.get_font("TruenoBd", 12).render(
                    "Space Station", True, (200, 200, 200))
                self.screen.blit(text, (974, yloc))
                yloc += 17

            # display production potential
            items = planet.get_production_potential()
            yloc += 5
            for item in items:
                text = self.resource_manager.get_font("TruenoBd", 12).render(
                    "{0}: {1}".format(
                        str(item)[13:], items[item]), True, (200, 200, 200)
                )
                self.screen.blit(text, (950, yloc))
                yloc += 17

    def display_unit_info(self, unit):
        if unit != None:
            yloc = int(self.sector_size[1] * self.MINI_MAP_SCALE + 32)

            # display units
            image = self.resource_manager.get_image(unit.type.value)
            self.screen.blit(image, (950, yloc))
            text = self.resource_manager.get_font("TruenoBd", 12).render(
                unit.get_name(), True, (200, 200, 200))
            self.screen.blit(text, (974, yloc))
            yloc += 17
            text = self.resource_manager.get_font("TruenoBd", 12).render(
                "Moves: {0} ({1})".format(
                    unit.moves_remaining, unit.moves), True, (200, 200, 200))
            self.screen.blit(text, (974, yloc))

    def display_on_grid(self, x, y):
        planet = self.sector.get_planet(x, y)
        if planet == None:
            return

        if (x >= self.view_x and x < self.view_x + self.grid_view_cols and
                y >= self.view_y and y < self.view_y + self.grid_view_rows):
            self.display_image_on_grid(
                planet, x - self.view_x, y - self.view_y)

    def generate_mini_map(self):
        width = int(self.sector_size[0] * self.MINI_MAP_SCALE + 2)
        height = int(self.sector_size[1] * self.MINI_MAP_SCALE + 2)
        surface = pygame.Surface((width, height))
        pygame.draw.rect(surface, (0, 0, 0),
                         (0, 0, width, height))
        pygame.draw.rect(surface, (255, 255, 0),
                         (0, 0, width, height), 1)
        for x in range(0, self.sector_size[0]):
            for y in range(0, self.sector_size[1]):
                planet = self.sector.get_planet(x, y)
                if planet.is_visible():
                    pygame.draw.rect(
                        surface, planet.get_mini_map_color(),
                        (x * self.MINI_MAP_SCALE + 1, y * self.MINI_MAP_SCALE + 1, self.MINI_MAP_SCALE, self.MINI_MAP_SCALE))
        return surface

    def draw_mini_map(self):
        if self.mini_map_surface == None:
            self.mini_map_surface = self.generate_mini_map()

        self.screen.blit(self.mini_map_surface,
                         (self.mini_map_x, self.mini_map_y))

        # Draw viewport indicator
        pygame.draw.rect(self.screen, (255, 255, 255),
                         (self.mini_map_x + (self.view_x * self.MINI_MAP_SCALE),
                          self.mini_map_y +
                          (self.view_y * self.MINI_MAP_SCALE),
                          self.grid_view_cols * self.MINI_MAP_SCALE,
                          self.grid_view_rows * self.MINI_MAP_SCALE), 1)

    def Update(self):
        if not GameState.game_state.in_turn:
            GameState.game_state.start_turn()
            self.start_turn()

    def center_view(self, pos):
        self.view_x = pos[0] - int(self.grid_view_cols / 2)
        self.view_y = pos[1] - int(self.grid_view_rows / 2)
        if self.view_x < 0:
            self.view_x = 0
        elif self.view_x + self.grid_view_cols >= self.sector.get_size()[0]:
            self.view_x = self.sector.get_size()[0] - 1 - self.grid_view_cols
        if self.view_y < 0:
            self.view_y = 0
        elif self.view_y + self.grid_view_rows >= self.sector.get_size()[1]:
            self.view_y = self.sector.get_size()[1] - 1 - self.grid_view_rows

    def move_view_to_unit(self, unit):
        pos = unit.position
        if pos[0] < self.view_x or pos[0] >= self.view_x + self.grid_view_cols or pos[1] < self.view_y or pos[1] >= self.view_y + self.grid_view_rows:
            self.center_view(unit.position)

    def select_next_unit(self):
        flist = list(filter(lambda x: x.moves_remaining > 0 and not x.moved,
                            Units.units.aslist()))
        if len(flist) > 1:
            selected = flist[0]
            if selected == self.last_selected:
                selected = flist[1]
            if self.last_selected != None:
                self.last_selected.selected = False
            self.last_selected = selected
            selected.selected = True
            self.move_view_to_unit(selected)
            return selected
        elif len(flist) == 1:
            selected = flist[0]
            if self.last_selected != None:
                self.last_selected.selected = False
            self.last_selected = selected
            selected.selected = True
            self.move_view_to_unit(selected)
            return selected
        else:
            if self.last_selected != None:
                self.last_selected.selected = False
            self.end_turn()
            return None

    def end_turn(self):
        GameState.game_state.in_turn = False

    def start_turn(self):
        Units.units.start_turn()
        self.select_next_unit()

    def Render(self, screen):
        self.screen = screen

        screen.fill((0, 0, 0))

        self.draw_top_bar(screen)

        screen.blit(
            self.image_grid, (self.grid_base_x, self.grid_base_y))
        for x in range(0, self.sector_size[0]):
            for y in range(0, self.sector_size[1]):
                self.display_on_grid(x, y)

        if self.last_selected != None and isinstance(self.last_selected, Planet.CelestialObject):
            self.display_planet_info(self.last_selected)
        elif self.last_selected != None and isinstance(self.last_selected, Units.Unit):
            self.display_unit_info(self.last_selected)

        self.draw_mini_map()
