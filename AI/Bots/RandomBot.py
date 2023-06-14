import random

from AI.Bots.AproxBot import AproxBot


class RandomBot(AproxBot):

    def get_score(self, game_state):
        pass

    def __init__(self, side):
        super().__init__(side)

    def get_action(self, game_state):
        return self.choose_randomly(game_state)
