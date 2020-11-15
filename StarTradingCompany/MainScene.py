from StarTradingCompany import SceneBase, Sector, Planet, GameState
from StarTradingCompany.Planet import *
import random


def end_turn():
    GameState.game_state.in_turn = False


class MainScene(SceneBase.SceneBase):
    def __init__(self, width, height):
        super().__init__(width, height)

        self.random = random.Random()

        self.sector = Sector.Sector()

        self.next = self  # for scene management

        # view window stuff
        self.grid_base_x = 10
        self.grid_base_y = 100
        self.grid_cell_width = 120
        self.grid_cell_height = 120
        self.grid_view_cols = 8
        self.grid_view_rows = 8

        self.view_x = 4996
        self.view_y = 4996

        # mini-map stuff
        self.MINI_MAP_PIXEL_SCALE = 4
        self.MINI_MAP_VIEW_SCALE = 75
        self.mini_map_x = width - 315
        self.mini_map_y = 10
        self.mini_map_surface = None
        self.mini_map_width = self.MINI_MAP_PIXEL_SCALE * self.MINI_MAP_VIEW_SCALE
        self.mini_map_height = self.mini_map_width

        self.last_selected = None

        self.show_grid = False
        self.done = False

        self.resource_manager = ResourceManager.ResourceManager()

        self.image_grid = self.view_background()
        self.screen = None

    def view_background(self):
        width = self.grid_view_cols * self.grid_cell_width
        height = self.grid_view_rows * self.grid_cell_height
        surface = pygame.Surface((width + 2, height + 2))
        for x in range(1, width + 1):
            for y in range(1, height + 1):
                if self.random.randint(1, 1000) < 2:
                    c = self.random.randint(128, 255)
                    surface.set_at((x, y), (c, c, c))
        return surface

    def draw_top_bar(self, screen):
        global game_state

        text = self.resource_manager.get_font("TruenoBd", 24).render(
            "Turn {0}".format(GameState.game_state.turn), True, (128, 128, 255))
        screen.blit(text, (20, 20))

    def draw_cell(self, surface, pos, offset, cell_size, color):
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
        if self.mini_map_x <= pos[0] <= self.mini_map_x + self.mini_map_width and \
                self.mini_map_y <= pos[1] <= self.mini_map_y + self.mini_map_height:
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
            selected = self.find_selected_cell(pos)
            if selected is not None:
                if self.last_selected == selected:
                    selected.selected = False
                    self.last_selected = None
                elif self.last_selected is not None:
                    selected.selected = True
                    self.last_selected.selected = False
                    self.last_selected = selected
                else:
                    selected.selected = True
                    self.last_selected = selected

    def calculate_pos_for_cell(self, view_location):
        """Calculate the screen x,y coordinate for the given view cell"""
        return self.grid_base_x + (self.grid_cell_width * int(view_location[0])), \
               self.grid_base_y + (self.grid_cell_height * int(view_location[1]))

    def find_selected_cell(self, mouse_pos):
        mousex, mousey = mouse_pos
        vx = (mousex - self.grid_base_x) / self.grid_cell_width
        vy = (mousey - self.grid_base_y) / self.grid_cell_height
        planet = self.sector.get_planet(
            vx + self.view_x, vy + self.view_y)
        target = planet.get_target_selected(mouse_pos, self.calculate_pos_for_cell(
            (vx, vy)), (self.grid_cell_width, self.grid_cell_height))
        if target is not None:
            return target
        return None

    def move_unit_to(self, unit, delta):
        if unit.moves_remaining <= 0: return

        oldloc = unit.position
        newloc = Units.units.move_unit(self.last_selected, delta)
        if oldloc != newloc:
            unit.moves_remaining -= 1
        planet = self.sector.get_planet(newloc[0], newloc[1])
        if unit.type == Units.ShipType.Explorer:
            self.sector.reveal_neighbors(newloc)
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
            self.move_unit_to(self.last_selected, (1, -1))
        if pressed_keys[pygame.K_KP7]:
            self.move_unit_to(self.last_selected, (-1, -1))
        if pressed_keys[pygame.K_KP3]:
            self.move_unit_to(self.last_selected, (1, 1))
        if pressed_keys[pygame.K_KP1]:
            self.move_unit_to(self.last_selected, (-1, 1))
        if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_KP4]:
            self.move_unit_to(self.last_selected, (-1, 0))
        if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_KP6]:
            self.move_unit_to(self.last_selected, (1, 0))
        if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_KP8]:
            self.move_unit_to(self.last_selected, (0, -1))
        if pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_KP2]:
            self.move_unit_to(self.last_selected, (0, 1))
        if pressed_keys[pygame.K_SPACE]:
            self.last_selected.moved = True
            self.select_next_unit()
        if pressed_keys[pygame.K_c]:
            self.center_view(self.last_selected.position)

    def process_input_for_hex(self, events, pressed_keys):
        if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_KP8]:
            self.view_y -= 1
        if pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_KP2]:
            self.view_y += 1
        if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_KP4]:
            self.view_x -= 1
        if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_KP6]:
            self.view_x += 1
        if pressed_keys[pygame.K_SPACE]:
            self.select_next_unit()

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse(event)

        if pressed_keys[pygame.K_g]:
            self.show_grid = not self.show_grid
        elif self.last_selected is not None and isinstance(self.last_selected, Units.Unit):
            self.process_input_for_unit(events, pressed_keys)
        else:
            self.process_input_for_hex(events, pressed_keys)

    def display_image_on_grid(self, planet, x, y):
        if planet is None:
            return

        planet.draw_cell(self.screen, self.calculate_pos_for_cell((x - self.view_x, y - self.view_y)),
                         (self.grid_cell_width, self.grid_cell_height))

    def display_planet_info(self, planet):
        if planet is not None and planet.type is not CelestialObjectTypes.NONE:
            yloc = 330

            # display name
            text = self.resource_manager.get_font("TruenoBd", 18).render(
                planet.name, True, (128, 128, 255))
            self.screen.blit(text, (1000, yloc))
            yloc += 30

            # display units
            units = planet.get_units()
            for unit in units:
                image = self.resource_manager.get_image(unit.type.value)
                self.screen.blit(image, (1000, yloc))
                text = self.resource_manager.get_font("TruenoBd", 12).render(
                    "{0} {1}".format(
                        str(unit.type)[9:], unit.name), True, (200, 200, 200))
                self.screen.blit(text, (1024, yloc))
                yloc += 17

            # display space station info
            if planet.has_space_station():
                yloc += 5
                image = self.resource_manager.get_image("space_station")
                self.screen.blit(image, (1000, yloc))
                text = self.resource_manager.get_font("TruenoBd", 12).render(
                    "Space Station", True, (200, 200, 200))
                self.screen.blit(text, (1024, yloc))
                yloc += 17

            # display production potential
            items = planet.production
            yloc += 5
            for item in items:
                text = self.resource_manager.get_font("TruenoBd", 12).render(
                    "{0}: {1}".format(
                        str(item)[13:], items[item]), True, (200, 200, 200)
                )
                self.screen.blit(text, (1000, yloc))
                yloc += 17

    def display_unit_info(self, unit):
        if unit is not None:
            yloc = 330

            # display units
            image = self.resource_manager.get_image(unit.type.value)
            self.screen.blit(image, (1000, yloc))
            text = self.resource_manager.get_font("TruenoBd", 12).render(
                unit.name, True, (200, 200, 200))
            self.screen.blit(text, (1024, yloc))
            yloc += 17
            text = self.resource_manager.get_font("TruenoBd", 12).render(
                "Moves: {0} ({1})".format(
                    unit.moves_remaining, unit.moves), True, (200, 200, 200))
            self.screen.blit(text, (1024, yloc))

    def generate_mini_map(self):
        #        width = int(self.sector_size[0] * self.MINI_MAP_SCALE + 2)
        #        height = int(self.sector_size[1] * self.MINI_MAP_SCALE + 2)
        #        surface = pygame.Surface((width, height))
        #        pygame.draw.rect(surface, (0, 0, 0),
        #                         (0, 0, width, height))
        #        pygame.draw.rect(surface, (255, 255, 0),
        #                         (0, 0, width, height), 1)
        #        for x in range(0, self.sector_size[0]):
        #            for y in range(0, self.sector_size[1]):
        #                planet = self.sector.get_planet(x, y)
        #                if planet.is_visible():
        #                    pygame.draw.rect(
        #                        surface, planet.get_mini_map_color(),
        #                        (x * self.MINI_MAP_SCALE + 1, y * self.MINI_MAP_SCALE + 1, self.MINI_MAP_SCALE, self.MINI_MAP_SCALE))
        surface = pygame.Surface((self.mini_map_width + 2, self.mini_map_height + 2))
        pygame.draw.rect(surface, (255, 255, 0),
                         (0, 0, self.mini_map_width + 2, self.mini_map_height + 2), 1)
        return surface

    def draw_mini_map(self):
        if self.mini_map_surface is None:
            self.mini_map_surface = self.generate_mini_map()

        self.screen.blit(self.mini_map_surface,
                         (self.mini_map_x, self.mini_map_y))

    def Update(self):
        if not GameState.game_state.in_turn:
            self.start_turn()

    def center_view(self, pos):
        self.view_x = pos[0] - int(self.grid_view_cols / 2)
        self.view_y = pos[1] - int(self.grid_view_rows / 2)

    def move_view_to_unit(self, unit):
        pos = unit.position
        if pos[0] < self.view_x or pos[0] >= self.view_x + self.grid_view_cols or pos[1] < self.view_y or pos[
            1] >= self.view_y + self.grid_view_rows:
            self.center_view(unit.position)

    def select_next_unit(self):
        f_list = sorted(list(filter(lambda x: x.moves_remaining > 0 and not x.moved,
                                    Units.units.aslist())), key=id)
        print("Select_next_unit")
        for unit in f_list:
            print(f"{unit.name}")
        if len(f_list) > 1:
            selected = f_list[0]
            if selected == self.last_selected:
                selected = f_list[1]
            if self.last_selected is not None:
                self.last_selected.selected = False
            self.last_selected = selected
            selected.selected = True
            self.move_view_to_unit(selected)
            return selected
        elif len(f_list) == 1:
            selected = f_list[0]
            if self.last_selected is not None:
                self.last_selected.selected = False
            self.last_selected = selected
            selected.selected = True
            self.move_view_to_unit(selected)
            return selected
        else:
            if self.last_selected is not None:
                self.last_selected.selected = False
            end_turn()
            return None

    def start_turn(self):
        GameState.game_state.start_turn()
        self.select_next_unit()

    def display_grid(self, surface):
        for x in range(1, self.grid_view_cols):
            x_pos = self.grid_base_x + (x * self.grid_cell_width)
            pygame.draw.line(surface, (75, 75, 75), (x_pos, self.grid_base_y + 1),
                             (x_pos, self.grid_base_y + (self.grid_view_rows * self.grid_cell_height)), 1)
        for y in range(1, self.grid_view_rows):
            y_pos = self.grid_base_y + (y * self.grid_cell_height)
            pygame.draw.line(surface, (75, 75, 75), (self.grid_base_x + 1, y_pos),
                             (self.grid_base_x + (self.grid_view_cols * self.grid_cell_width), y_pos), 1)

    def Render(self, screen):
        self.screen = screen

        screen.fill((0, 0, 0))

        self.draw_top_bar(screen)

        screen.blit(
            self.image_grid, (self.grid_base_x, self.grid_base_y))
        for x in range(self.view_x, self.view_x + self.grid_view_cols):
            for y in range(self.view_y, self.view_y + self.grid_view_rows):
                planet = self.sector.get_planet(x, y)
                if planet is not None:
                    self.display_image_on_grid(planet, x, y)
        pygame.draw.rect(screen, (100, 100, 100), (
        self.grid_base_x, self.grid_base_y, self.image_grid.get_width(), self.image_grid.get_height()), 1)
        if self.show_grid:
            self.display_grid(screen)

        if self.last_selected is not None and isinstance(self.last_selected, Planet.CelestialObject):
            self.display_planet_info(self.last_selected)
        elif self.last_selected is not None and isinstance(self.last_selected, Units.Unit):
            self.display_unit_info(self.last_selected)

        self.draw_mini_map()
