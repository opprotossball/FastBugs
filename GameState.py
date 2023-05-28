import copy

import numpy as np

import info
from Armies import Army
from Board import neigh_generator, neigh_coords, valid_tile
from Bug import Bug, decode_bug
from info import board_array_size, starting_bugs, Side, bug_cost


class GameState:

    def __init__(self, copied=None):
        if copied is not None:
            self.copy(copied)
            return
        self.board = np.zeros((board_array_size, board_array_size), dtype=int)
        self.combat_map = np.zeros((board_array_size, board_array_size))
        self.players_bugs = starting_bugs()
        self.phase = 0
        self.active_player_resources = 0
        self.winner = 0
        self.armies = [[], []]

    def copy(self, copied):
        self.board = np.copy(copied.board)
        self.combat_map = np.copy(copied.combat_map)
        self.players_bugs = np.copy(copied.players_bugs)
        self.phase = copied.phase
        self.active_player_resources = copied.active_player_resources
        self.winner = copied.winner
        # self.armies = copy.deepcopy(copied.armies) TODO

    def active_side(self):
        return Side(1 - 2 * (self.phase > 2))

    def hatch(self, side, bug_type, hatch_id):
        # validate phase TODO
        if side != self.active_side():
            return False
        cost = info.bug_cost[bug_type.value()]
        available = self.players_bugs[side, bug_type.value()]
        x, y = info.hatcheries[side.value(), hatch_id]
        if self.active_player_resources < cost or available < 1 or self.board[x, y] != 0:
            return False
        self.active_player_resources -= cost
        self.players_bugs[side, bug_type.value()] -= 1
        self.board[x, y] = Bug(side, bug_type, x, y).bug_code
        return True

    def enlist(self, x, y, army_ids, seen, side):
        if seen[x, y]:
            return
        bug_code = self.board[x, y]
        if bug_code == 0:
            seen[x, y] = True
            return
        bug = decode_bug(bug_code)
        if bug.get_side() != side:
            return
        self.armies[side][army_ids[side]].add_bug(bug.bug_code)
        seen[x, y] = True
        for nx, ny in neigh_generator(x, y):
            self.enlist(nx, ny, army_ids, seen, side)

    def update_armies(self):
        self.armies = [[], []]
        army_ids = [0, 0]
        seen = np.zeros((board_array_size, board_array_size), dtype=bool)
        for (x, y), bug_code in np.ndenumerate(self.board):
            if bug_code == 0 or seen[x, y]:
                seen[x, y] = True
                continue
            bug = decode_bug(bug_code)
            side = bug.get_side()
            self.armies[side].append(Army())
            self.enlist(x, y, army_ids, seen, side)
            army_ids[side] += 1

    def move_recursively(self, x, y, dirc, pinned_map):
        nx, ny = neigh_coords(x, y, dirc)
        if not valid_tile(nx, ny) or pinned_map[x, y] or pinned_map[nx, ny] or self.has_enemy_neighbour(x, y):
            pinned_map[x, y] = True
            self.decrement_move(x, y)
            return False
        if self.board[nx, ny] != 0:  # has teammate able to move
            self.move_recursively(nx, ny, dirc, pinned_map)
        if self.board[nx, ny] == 0:
            print("A")
            self.move_bug_to(x, y, nx, ny)
            pinned_map[nx, ny] = True
            self.decrement_move(nx, ny)
            return True
        return False

    def move(self, side, army_id, dirc):
        # validate phase TODO
        army = self.armies[side][army_id]
        if army.moves_left < 1:
            return False
        army.moves_left -= 1
        pinned_map = np.zeros((board_array_size, board_array_size), dtype=bool)
        something_moved = False
        for bug_code in army.bugs:
            bug = decode_bug(bug_code)
            x = bug.get_x()
            y = bug.get_y()
            if not pinned_map[x, y]:
                moved_now = self.move_recursively(x, y, dirc, pinned_map)
                something_moved = moved_now or something_moved
        if something_moved:
            self.update_armies()
        return something_moved

    def side_at_tile(self, x, y):
        if self.board[x, y] == 0:
            return None
        return decode_bug(self.board[x, y]).get_side()

    def has_enemy_neighbour(self, x, y):
        side = self.side_at_tile(x, y)
        if side is None:
            return False
        for nx, ny in neigh_generator(x, y):
            neigh_side = self.side_at_tile(nx, ny)
            if neigh_side is not None and neigh_side != side:
                return True
        return False

    def decrement_move(self, x, y):
        bug = decode_bug(self.board[x, y])
        if bug is not None:
            bug.set_moves_left(bug.get_moves_left() - 1)
        self.board[x, y] = bug.bug_code

    def move_bug_to(self, x, y, target_x, target_y):
        bug = decode_bug(self.board[x, y])
        bug.set_x(target_x)
        bug.set_y(target_y)
        self.board[x, y] = 0
        self.board[target_x, target_y] = bug.bug_code
