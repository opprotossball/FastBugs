import math
from AI.Bots.AproxBot import AproxBot
from AI.rewardMap import rewardMap
from AI.resorcesDistance import get_dist
from Backend.Bug import decode_bug
from info import PhaseType
from info import resources


class Territorial(AproxBot):
    def __init__(self, side):
        super().__init__(side)

    def get_action(self, game_state):
        if game_state.phase_type() == PhaseType.COMBAT:
            return self.choose_randomly(game_state)
        else:
            return self.choose_best(game_state)

    def get_score(self, game_state):
        score = [0, 0, 0, 0]
        for bug in game_state.player_bugs_iterate(self.side):
            x, y = bug.get_x(), bug.get_y()
            for i in range(3):
                score[i] = max(score[i], math.pow(7 - get_dist(x, y, i), 2))
                score[-1] = score[-1] + rewardMap.get_reward(x, y)
        return sum(score)
