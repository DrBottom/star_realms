import basics
# TODO: импорт файла с картами


class GameTurn:
    def __init__(self, players: list[basics.Player], shop: basics.CardShop, ctx: basics.GameContext = None):
        self.players = players
        self.shop = shop
        self.ctx = ctx

    def main_phase(self):
        pass

    def discard_phase(self):
        pass

    def draw_phase(self):
        pass
