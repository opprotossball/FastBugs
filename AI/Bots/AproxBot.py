import random
from abc import abstractmethod, ABC

import numpy as np

from Backend.Bug import decode_bug
from Backend.GameState import GameState
from Backend.Player import Player
from info import PhaseType, opposing_side, Direction, ActionType, hatcheries, BugType, bug_cost
from Backend.GameMaster import perform_action


class AproxBot(Player, ABC):

    def __init__(self, side):
        super().__init__(side)
        self.valid_kills = []

    def get_valid_actions(self, game_state):
        phase_type = game_state.phase_type()
        if phase_type == PhaseType.COMBAT:
            valid_actions = self.get_valid_kills(game_state)
        else:
            self.valid_kills = []
        if phase_type == PhaseType.MOVE:
            valid_actions = self.get_valid_moves(game_state)
        elif phase_type == PhaseType.HATCH:
            valid_actions = self.get_valid_hatches(game_state)
        valid_actions.append((ActionType.PASS,))
        return valid_actions

    @abstractmethod
    def get_action(self, game_state):
        pass

    @abstractmethod
    def get_score(self, game_state):
        pass

    def get_valid_kills(self, games_state):
        if self.valid_kills:
            return self.valid_kills
        for army in games_state.armies[opposing_side(self.side)]:
            if army.kills < 1:
                continue
            for bug_code in army.bugs:
                bug = decode_bug(bug_code)
                x, y = bug.get_x(), bug.get_y()
                if games_state.has_enemy_neighbour(x, y):
                    self.valid_kills.append((ActionType.KILL, x, y))
                    continue
        return self.valid_kills

    def get_valid_moves(self, game_state):
        valid_actions = []
        for army_id, army in enumerate(game_state.armies[self.side]):
            if army.moves_left > 0:
                for dirc in Direction:
                    valid_actions.append((ActionType.MOVE, army_id, dirc))
        return valid_actions

    def get_valid_hatches(self, game_state):
        valid_actions = []
        for bug_type in BugType:
            if game_state.active_player_resources < bug_cost[bug_type] or game_state.players_bugs[self.side, bug_type] < 1:
                continue
            for hatch_id, (x, y) in enumerate(hatcheries[self.side]):
                if game_state.board[x, y] == 0:
                    valid_actions.append((ActionType.HATCH, bug_type, hatch_id))
        return valid_actions

    def choose_randomly(self, game_state):
        valid_actions = self.get_valid_actions(game_state)
        if len(valid_actions) == 1:
            return valid_actions[0]
        action = valid_actions[random.randint(0, len(valid_actions) - 2)]
        return action

    def choose_best(self, game_state):
        best = (ActionType.PASS,), -np.inf
        for action in self.get_valid_actions(game_state):
            new_game_state = GameState(game_state)
            perform_action(self.side, action, new_game_state)
            score = self.get_score(new_game_state)
            if score == best and random.randint(0, 1):
                best = action, score
            elif score > best[1]:
                best = action, score
        return best[0]
