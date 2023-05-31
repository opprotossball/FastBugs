from abc import ABC, abstractmethod


class Player(ABC):

    def __init__(self, side):
        self.side = side

    @abstractmethod
    def get_action(self, game_state):
        pass
