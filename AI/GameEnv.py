import gym
import numpy as np
from gym import spaces

from AI.Bots.Territorial import Territorial
from Backend.GameState import GameState
from info import board_array_size, Side, Phase, ActionType
from Arena import perform_action
from actionMap import move_action_list, move_actions_codes

class GameEnv(gym.Env):
    def __init__(self, render_mode=None):
        self.loss_reward = -1000
        self.win_reward = 1000
        self.phases = np.zeros(6, dtype=bool)  # Phases in which DQN Agent plays
        self.phases[Phase.W_MOVE] = True
        self.dummy_players = [Territorial(Side.WHITE), Territorial(Side.BLACK)]
        self.observation_space = spaces.Box(-25, 25, shape=((board_array_size + 1) * board_array_size, 1), dtype=int)
        self.action_space = spaces.Discrete(len(move_action_list))
        self.state = {}
        self.done = False
        self.max_rounds = 30
        self.steps_to_do = 1000
        self.steps_done = 0
        self.last_was_valid = True
        self.show = render_mode
        self.test = False
        self.reset()

    def reset(self):
        self.steps_done = 0
        self.done = False
        self.game = GameState()
        return self._observe()

    def render(self, mode=None):
        return

    def step(self, action_id):
        while not self.phases[self.game.phase]:
            dummy_bot = self.dummy_players[self.game.active_side()]
            action = dummy_bot.get_action(self.game)
            self.last_was_valid = perform_action(dummy_bot.side, action, self.game)
            if self.game.get_winner() == dummy_bot.side:
                # self.done = True
                print("dqn lost")
                return self._observe(), self.loss_reward + self.game.round, True, {}
        action = move_action_list[action_id]
        if self.test:
            print(str(Phase(self.game.phase)) + ":", action, sep=" ")
        self.last_was_valid = perform_action(self.game.active_side(), action, self.game)
        if action[0] == ActionType.PASS:
            reward = 0
        elif self.last_was_valid:
            reward = 10
        else:
            reward = -2
            perform_action(self.game.active_side(), (ActionType.PASS, ), self.game)
        done = False
        if self.game.get_winner() is not None:
            done = True
            reward += self.win_reward - self.game.round
            print("dqn won")
        self.steps_done += 1
        if self.steps_done >= self.steps_to_do or self.game.round >= self.max_rounds:
            print("draw")
            done = True
        return self._observe(), reward, done, {}

    def _observe(self):
        arr = np.zeros((board_array_size, board_array_size + 1))
        for bug in self.game.bugs_iterate():
            arr[bug.get_x(), bug.get_y()] = self.encode_bug(bug)
        arr[-1] = 1 - 2 * self.game.active_side()
        return arr.flatten()

    @staticmethod
    def encode_bug(bug):
        bug_code = (bug.get_type() + 1) * 5
        bug_code += bug.get_moves_left()
        bug_code *= (2 * bug.get_side()) - 1
        return bug_code
