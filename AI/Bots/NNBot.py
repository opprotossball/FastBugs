import random

from AI.Bots.AproxBot import AproxBot
from AI.PositionEvaluator import PositionEvaluator

evaluator = PositionEvaluator()
evaluator.load("C:/Users/janst/source/Games/Robale/FastBugs/AI/Models/PosEv/new0")


class NNBot(AproxBot):

    def get_score(self, game_state):
        pred = evaluator.predict(game_state)
        return (pred[0] - pred[1]) * (2 * self.side - 1)

    def __init__(self, side):
        super().__init__(side)

    def get_action(self, game_state):
        return self.choose_randomly(game_state)
