from Backend.AproxBot import AproxBot
from Backend.GameMaster import GameMaster
from Backend.RandomBot import RandomBot
from Backend.info import Side


class Arena(GameMaster):
    def __init__(self):
        super().__init__()

    def duel(self):
        self.new_game(RandomBot(Side.WHITE), RandomBot(Side.BLACK))


if __name__ == "__main__":
    a = Arena()
    a.duel()
