from StarTradingCompany import SectorRandom, Units, SpaceStation, GameState
from StarTradingCompany.Planet import *
from collections import namedtuple

Location = namedtuple('Location', 'x y')


class Sector:
    def __init__(self):
        global game_state

        super().__init__()

        self.random = SectorRandom.SectorRandom()

        self.planets = {}

        self.home_pos = (5000, 5000)

    def get_production_potential(self, planet):
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
                 RawMaterials.Gas: 5,
                 RawMaterials.Neodymium: 0},
            CelestialObjectTypes.COPPER:
                {RawMaterials.Ore: 2,
                 RawMaterials.Food: 0,
                 RawMaterials.Water: 0,
                 RawMaterials.Gas: 2,
                 RawMaterials.Neodymium: 3},
            CelestialObjectTypes.GREEN:
                {RawMaterials.Ore: 3,
                 RawMaterials.Food: 5,
                 RawMaterials.Water: 4,
                 RawMaterials.Gas: 0,
                 RawMaterials.Neodymium: 2},
            CelestialObjectTypes.LAVA:
                {RawMaterials.Ore: 3,
                 RawMaterials.Food: 0,
                 RawMaterials.Water: 0,
                 RawMaterials.Gas: 2,
                 RawMaterials.Neodymium: 5},
            CelestialObjectTypes.ASTEROIDS:
                {RawMaterials.Ore: 5,
                 RawMaterials.Food: 0,
                 RawMaterials.Water: 4,
                 RawMaterials.Gas: 2,
                 RawMaterials.Neodymium: 3}
        }
        return switcher.get(planet.type,
                            {RawMaterials.Ore: 0,
                             RawMaterials.Food: 0,
                             RawMaterials.Water: 0,
                             RawMaterials.Gas: 0,
                             RawMaterials.Neodymium: 0})

    def generate_planet(self, x, y):
        self.random.set_seed((x, y))
        num = self.random.randint(1, 100)

        if x == self.home_pos[1] and y == self.home_pos[1]:
            planet = CelestialObject(CelestialObjectTypes.HOME, x, y)
            planet.name = 'Homeworld'
        elif num < 3:
            planet = CelestialObject(CelestialObjectTypes.ASTEROIDS, x, y)
        elif num < 5:
            planet = CelestialObject(CelestialObjectTypes.RED, x, y)
        elif num < 7:
            planet = CelestialObject(CelestialObjectTypes.COPPER, x, y)
        elif num < 9:
            planet = CelestialObject(CelestialObjectTypes.GREEN, x, y)
        elif num < 10:
            planet = CelestialObject(CelestialObjectTypes.LAVA, x, y)
        else:
            planet = CelestialObject(CelestialObjectTypes.NONE, x, y)
        production = self.get_production_potential(planet)
        planet.production[RawMaterials.Ore] = self.random.randint(0, production[RawMaterials.Ore])
        planet.production[RawMaterials.Gas] = self.random.randint(0, production[RawMaterials.Gas])
        planet.production[RawMaterials.Food] = self.random.randint(0, production[RawMaterials.Food])
        planet.production[RawMaterials.Water] = self.random.randint(0, production[RawMaterials.Water])
        planet.production[RawMaterials.Neodymium] = self.random.randint(0, production[RawMaterials.Neodymium])
        return planet

    def get_planet_type(self, x, y):
        return self.planets[int(x), int(y)].get_type()

    def get_planet(self, x, y):
        pos = int(x), int(y)
        if pos not in self.planets:
            planet = self.generate_planet(x, y)
            self.planets[pos] = planet
            if planet.type is CelestialObjectTypes.HOME:
                self.reveal_neighbors(pos)
                planet.set_space_station(SpaceStation.SpaceStation())
                Units.units.add_unit(Units.ShipType.Explorer, pos, 2)
                Units.units.add_unit(Units.ShipType.Fighter, pos, 1)
                Units.units.add_unit(Units.ShipType.Builder, pos, 1)
        return self.planets[pos]

    def reveal_neighbors(self, pos):
        x, y = pos
        xm = x - 1
        xp = x + 1
        ym = y - 1
        yp = y + 1

        planet = self.get_planet(xm, ym)
        planet.set_visible(True)
        planet = self.get_planet(x, ym)
        planet.set_visible(True)
        planet = self.get_planet(xp, ym)
        planet.set_visible(True)
        planet = self.get_planet(xm, y)
        planet.set_visible(True)
        planet = self.get_planet(x, y)
        planet.set_visible(True)
        planet = self.get_planet(xp, y)
        planet.set_visible(True)
        planet = self.get_planet(xm, yp)
        planet.set_visible(True)
        planet = self.get_planet(x, yp)
        planet.set_visible(True)
        planet = self.get_planet(xp, yp)
        planet.set_visible(True)
