from StarTradingCompany import SectorRandom, Units, SpaceStation, GameState
from StarTradingCompany.Planet import *


class Sector:
    def __init__(self):
        global game_state

        super().__init__()
        self.width = 64
        self.height = 65

        self.random = SectorRandom.SectorRandom()

        self.planets = []
        for x in range(0, self.width):
            planet_row = []
            for y in range(0, self.height):
                planet_row.append(self.generate_planet(x, y))
            self.planets.append(planet_row)
        self.reveal_neighbors(int(self.width / 2), int(self.height / 2))

        home_pos = (int(self.width / 2), int(self.height / 2))
        Units.units.add_unit(Units.ShipType.Explorer, home_pos, 2)
        Units.units.add_unit(Units.ShipType.Fighter, home_pos, 1)
        Units.units.add_unit(Units.ShipType.Builder, home_pos, 1)

        self.planets[int(self.width / 2)
                     ][int(self.height / 2)].set_space_station(SpaceStation.SpaceStation())

    def get_size(self):
        return (self.width, self.height)

    def generate_planet(self, x, y):
        num = self.random.randint((x, y), 1, 100)

        if x == int(self.width / 2) and y == int(self.width / 2):
            return CelestialObject(CelestialObjectTypes.HOME, x, y)
        elif num < 3:
            return CelestialObject(CelestialObjectTypes.ASTEROIDS, x, y)
        elif num < 5:
            return CelestialObject(CelestialObjectTypes.RED, x, y)
        elif num < 7:
            return CelestialObject(CelestialObjectTypes.COPPER, x, y)
        elif num < 9:
            return CelestialObject(CelestialObjectTypes.GREEN, x, y)
        elif num < 10:
            return CelestialObject(CelestialObjectTypes.LAVA, x, y)
        else:
            return CelestialObject(CelestialObjectTypes.NONE, x, y)

    def get_planet_type(self, x, y):
        if x >= self.width or y >= self.height:
            return CelestialObjectTypes.NONE
        else:
            return self.planets[x][y].get_type()

    def get_planet(self, x, y):
        return self.planets[int(x)][int(y)]

    def reveal_neighbors(self, x, y):
        xm = x - 1
        xp = x + 1
        ym = y - 1
        yp = y + 1

        if xm < 0:
            xm = x
        elif xp >= self.get_size()[0]:
            xp = x
        if ym < 0:
            ym = y
        elif yp >= self.get_size()[1]:
            yp = y

        self.planets[x][y].set_visible(True)
        self.planets[xm][ym].set_visible(True)
        self.planets[x][ym].set_visible(True)
        self.planets[xp][y].set_visible(True)
        self.planets[x][yp].set_visible(True)
        self.planets[xm][yp].set_visible(True)
        self.planets[xm][y].set_visible(True)
