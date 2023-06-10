from abc import abstractmethod, ABC

from Backend.Bug import decode_bug
from Backend.Player import Player
from Backend.info import PhaseType, opposing_side, Direction, ActionType, hatcheries, BugType, bug_cost, Phase


class AproxBot(Player, ABC):

    def __init__(self, side, score_function):
        super().__init__(side)
        self.score_function = score_function
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
