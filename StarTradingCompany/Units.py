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
        self.name = f"{self.type.value} {self.id}"

        _next_id += 1


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

    def move_unit(self, unit, delta):
        self.remove_unit(unit)
        newpos = (unit.position[0] + delta[0], unit.position[1] + delta[1])
        self.add(unit, newpos)
        return newpos


units = Units()
