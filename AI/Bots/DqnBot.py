import math
from AI.Bots.AproxBot import AproxBot
from AI.rewardMap import rewardMap
from AI.resorcesDistance import get_dist
from Backend.Bug import decode_bug
from info import PhaseType
from info import resources


class DqnBot(AproxBot):
    def __init__(self, side):
        super().__init__(side)

    def get_action(self, game_state):
        if game_state.phase_type() != PhaseType.MOVE:
            return self.choose_randomly(game_state)
        else:
            return self.choose_best(game_state)

    def get_score(self, game_state):
        pass