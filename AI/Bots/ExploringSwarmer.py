import random
from AI.Bots.Swarmer import Swarmer
from info import PhaseType


class ExploringSwarmer(Swarmer):
    def __init__(self, side):
        super().__init__(side)

    def get_action(self, game_state):
        if game_state.phase_type() == PhaseType.COMBAT:
            return self.choose_randomly(game_state)
        else:
            return self.choose_best(game_state)

    def get_score(self, game_state):
        return super().get_score(game_state) + random.randint(0, 3)
