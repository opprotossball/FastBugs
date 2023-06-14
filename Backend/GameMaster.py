import math
import time

import pygame.time

from Backend.GameState import GameState
from FrontEnd.Display import Display
from FrontEnd.GameScene import GameScene
from info import ActionType


def perform_action(side, action, game):
    action_type = action[0]
    if action_type == ActionType.PASS:
        return game.end_phase(side)
    elif action_type == ActionType.KILL:
        return game.kill(side, action[1], action[2])
    elif action_type == ActionType.MOVE:
        return game.move(side, army_id=action[1], dirc=action[2])
    elif action_type == ActionType.HATCH:
        return game.hatch(side, bug_type=action[1], hatch_id=action[2])
    return False


class GameMaster:

    def __init__(self):
        self.game = None
        self.players = []
        self.steps = 0
        self.steps_max = math.inf
        self.max_rounds = 100

        self.display = None
        self.clock = None
        self.fps = 40
        self.sleep_after_action = 0.5  # s

    def new_game(self, white_player, black_player, visualize=False):
        self.players = [white_player, black_player]
        self.game = GameState()
        last_was_valid = True
        if visualize:
            self.display = Display()
            self.display.set_scene(GameScene())
            self.clock = pygame.time.Clock()
        while self.game.get_winner() is None and self.steps < self.steps_max and self.game.round < self.max_rounds:
            if visualize:
                self.display.update_window(self.game)
                self.clock.tick(self.fps)
                if last_was_valid:
                    self.wait()
            active_side = self.game.active_side()
            action = self.players[active_side].get_action(self.game)
            last_was_valid = self.perform_players_action(active_side, action)
            self.steps += 1
        winner = self.game.get_winner()
        return winner

    def wait(self):
        start = time.time()
        while time.time() - start < self.sleep_after_action:
            self.display.update_window(self.game)
            self.clock.tick(self.fps)

    def perform_players_action(self, side, action):
        return perform_action(side, action, self.game)
