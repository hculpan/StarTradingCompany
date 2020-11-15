import random


class SectorRandom:
    def __init__(self):
        self.seed_mod = 78092345
        self.random = random.Random()

    def set_seed(self, location):
        self.random.seed(((int(location[0]) << 32) | int(location[1]) ^ self.seed_mod))

    def randint(self, a, b):
        return self.random.randint(a, b)
