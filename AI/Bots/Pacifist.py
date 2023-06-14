import math
from AI.Bots.AproxBot import AproxBot
from AI.Bots.Territorial import Territorial
from AI.rewardMap import rewardMap
from AI.resorcesDistance import get_dist
from info import PhaseType


class Pacifist(Territorial):
    def __init__(self, side):
        super().__init__(side)

    def get_action(self, game_state):
        if game_state.phase_type() == PhaseType.COMBAT:
            return self.choose_randomly(game_state)
        else:
            return self.choose_best(game_state)

    def get_score(self, game_state):
        attacked = 0
        for bug in game_state.player_bugs_iterate(self.side):
            attacked += game_state.has_enemy_neighbour(bug.get_x(), bug.get_y())
        return super().get_score(game_state) - attacked

