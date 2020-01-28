from enum import Enum

_next_id = 1001


class ShipType(Enum):
    Explorer = "Explorer"
    Settler = "Settler"
    Builder = "Builder"
    Fighter = "Fighter"
    Freighter = "Freighter"


class Unit:
    def __init__(self, type, position):
        global _next_id

        self.type = type
        self.id = _next_id
        self.position = position
        if type == ShipType.Explorer:
            self.moves = 3
        elif type == ShipType.Freighter or type == ShipType.Fighter:
            self.moves = 2
        else:
            self.moves = 1
        self.moves_remaining = self.moves
        self.selected = False
        self.alert = False

        _next_id += 1

    def get_name(self):
        return f"{self.type.value} {self.id}"


class Units:
    def __init__(self):
        self._unit_dict = {}

    def __len__(self):
        return len(self.unit_dict)

    def __getitem__(self, key):
        if key in self._unit_dict:
            return self._unit_dict[key]
        else:
            return []

    def __setitme__(self, key, value):
        self._unit_dict[key] = value

    def aslist(self):
        result = []
        for value in self._unit_dict.values():
            result.extend(value)
        return result

    def add_unit(self, type, position, moves):
        self.add(Unit(type, position), position)

    def add(self, unit, position):
        if position in self._unit_dict:
            self._unit_dict[position].append(unit)
        else:
            list = [unit]
            self._unit_dict[position] = list
        unit.position = position

    def start_turn(self):
        for key, value in self._unit_dict.items():
            for item in value:
                item.moves_remaining = item.moves
                item.moved = False

    def get_units_for(self, position):
        if position in self._unit_dict:
            return self._unit_dict[position]
        else:
            return []

    def remove_unit(self, unit):
        old_position = unit.position
        unit_list = self._unit_dict[old_position]
        unit_list.remove(unit)

    def move_unit(self, unit, delta, universe_size):
        old_position = unit.position
        self.remove_unit(unit)
        newx = old_position[0] + delta[0]
        if newx < 0:
            newx = 0
        elif newx >= universe_size[0]:
            newx = universe_size[0] - 1
        newy = old_position[1] + delta[1]
        if newy < 0:
            newy = 0
        elif newy >= universe_size[1]:
            newy = universe_size[1] - 1
        self.add(unit, (newx, newy))
        return (newx, newy)


units = Units()
