import random


class SectorRandom:
    def __init__(self):
        self.seed_mod = 1973256
        self.random = random.Random()

    def random_planet(self, location):
        self.random.seed((int(location[0]) << 16) | int(location[1]))

    def randint(self, location, a, b):
        self.random.seed((int(location[0]) << 16) | int(location[1]))
        return self.random.randint(a, b)
