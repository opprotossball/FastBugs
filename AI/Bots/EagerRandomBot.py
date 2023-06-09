import random
from AI.Bots.AproxBot import AproxBot


class EagerRandomBot(AproxBot):
    def get_score(self, game_state):
        pass

    def __init__(self, side):
        super().__init__(side)

    def get_action(self, game_state):
        valid_actions = self.get_valid_actions(game_state)
        if len(valid_actions) == 1:
            return valid_actions[0]
        action = valid_actions[random.randint(0, len(valid_actions) - 2)]
        return action
