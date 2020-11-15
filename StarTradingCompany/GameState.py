from StarTradingCompany import Units


def get_unit_list_key(unit):
    return unit.get_id()


class GameState:
    def __init__(self):
        self.turn = 0
        self.in_turn = False

    def start_turn(self):
        self.in_turn = True
        self.turn += 1
        Units.units.start_turn()

    def end_turn(self):
        self.in_turn = False
        pass


game_state = GameState()
