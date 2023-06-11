import random

from AI.AproxBot import AproxBot


class RandomBot(AproxBot):

    def __init__(self, side):
        super().__init__(side, -1)

    def get_action(self, game_state):
        valid_actions = self.get_valid_actions(game_state)
        #print(valid_actions)
        #print(game_state.board, 2*"\n")
        return valid_actions[random.randint(0, len(valid_actions) - 1)]
