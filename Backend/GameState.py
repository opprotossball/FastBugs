import copy
import math
import random

import numpy as np

import info
from Army import Army
from Board import neigh_generator, neigh_coords, valid_tile
from Bug import Bug, decode_bug
from info import board_array_size, starting_bugs, Side, Phase, PhaseType


class GameState:

    def __init__(self, copied=None):
        if copied is not None:
            self.copy(copied)
            return
        self.board = np.zeros((board_array_size, board_array_size), dtype=int)
        self.players_bugs = starting_bugs()
        self.phase = 0
        self.active_player_resources = 0
        self.__winner = None
        self.armies = [[], []]

    def copy(self, copied):
        self.board = np.copy(copied.board)
        self.players_bugs = np.copy(copied.players_bugs)
        self.phase = copied.phase
        self.active_player_resources = copied.active_player_resources
        self.__winner = copied.__winner
        self.armies = copy.deepcopy(copied.armies)

    def active_side(self):
        return Side(self.phase > 2)

    def phase_type(self):
        return PhaseType(self.phase % 3)

    def validate_action_type(self, action_type, side):
        return self.phase == action_type + 3 * side

    def hatch(self, side, bug_type, hatch_id):
        if not self.validate_action_type(info.ActionType.HATCH, side):
            print("Invalid phase for hatching!")
            return False
        cost = info.bug_cost[bug_type]
        available = self.players_bugs[side, bug_type]
        x, y = info.hatcheries[side][hatch_id]
        if self.active_player_resources < cost or available < 1 or self.board[x, y] != 0:
            return False
        self.active_player_resources -= cost
        self.players_bugs[side, bug_type] -= 1
        self.board[x, y] = Bug(side, bug_type, x, y).bug_code
        return True

    def end_phase(self, side):
        if side != self.active_side():
            return False
        else:
            self.__next_phase()

    def kill(self, side, x, y):
        if not self.validate_action_type(info.ActionType.KILL, side):
            print("Invalid phase for killing!")
            return False
        bug_code = self.board[x, y]
        if bug_code == 0:
            return False
        bug = decode_bug(bug_code)
        attacked_side = bug.get_side()
        if attacked_side == side:
            return False
        attacked_army = self.armies[attacked_side][bug.get_army_id()]
        if attacked_army.kills < 1 or not self.has_enemy_neighbour(x, y):
            return False
        attacked_army.kills -= 1
        self.board[x, y] = 0
        return True

    def get_winner(self):
        return self.__winner

    def __enlist(self, x, y, army_ids, seen, side):
        if seen[x, y]:
            return
        bug_code = self.board[x, y]
        if bug_code == 0:
            seen[x, y] = True
            return
        bug = decode_bug(bug_code)
        if bug.get_side() != side:
            return
        bug.set_army_id(army_ids[side])
        self.armies[side][army_ids[side]].add_bug(bug.bug_code)
        self.board[x, y] = bug.bug_code
        seen[x, y] = True
        for nx, ny in neigh_generator(x, y):
            self.__enlist(nx, ny, army_ids, seen, side)

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
            self.__enlist(x, y, army_ids, seen, side)
            army_ids[side] += 1

    def __move_recursively(self, x, y, dirc, pinned_map):
        nx, ny = neigh_coords(x, y, dirc)
        if not valid_tile(nx, ny) or pinned_map[x, y] or pinned_map[nx, ny] or self.has_enemy_neighbour(x, y):
            pinned_map[x, y] = True
            self.__decrement_move(x, y)
            return False
        if self.board[nx, ny] != 0:  # has teammate able to move
            self.__move_recursively(nx, ny, dirc, pinned_map)
        if self.board[nx, ny] == 0:
            print("A")
            self.__move_bug_to(x, y, nx, ny)
            pinned_map[nx, ny] = True
            self.__decrement_move(nx, ny)
            return True
        return False

    def move(self, side, army_id, dirc):
        if not self.validate_action_type(info.ActionType.MOVE, side):
            print("Invalid phase for moving!")
            return False
        if army_id < len(self.armies[side]):
            return False
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
                moved_now = self.__move_recursively(x, y, dirc, pinned_map)
                something_moved = moved_now or something_moved
        if something_moved:
            self.update_armies()
        return something_moved

    def __side_at_tile(self, x, y):
        if self.board[x, y] == 0:
            return None
        return decode_bug(self.board[x, y]).get_side()

    def has_enemy_neighbour(self, x, y):
        side = self.__side_at_tile(x, y)
        if side is None:
            return False
        for nx, ny in neigh_generator(x, y):
            neigh_side = self.__side_at_tile(nx, ny)
            if neigh_side is not None and neigh_side != side:
                return True
        return False

    def __decrement_move(self, x, y):
        bug = decode_bug(self.board[x, y])
        if bug is not None:
            bug.set_moves_left(bug.get_moves_left() - 1)
        self.board[x, y] = bug.bug_code

    def __move_bug_to(self, x, y, target_x, target_y):
        bug = decode_bug(self.board[x, y])
        bug.set_x(target_x)
        bug.set_y(target_y)
        self.board[x, y] = 0
        self.board[target_x, target_y] = bug.bug_code

    def __attack_army(self, side, army_id):  # assigns number of kills to chosen army
        attackers = set()
        attacking_armies = set()
        attack_value = 0
        army = self.armies[side][army_id]
        for bug_code in army.bugs:
            bug = decode_bug(bug_code)
            for nx, ny in neigh_generator(bug.get_x(), bug.get_y()):
                neigh_code = self.board[nx, ny]
                neigh_side = self.__side_at_tile(nx, ny)
                if neigh_side is None or neigh_side == side:
                    continue
                neigh = decode_bug(neigh_code)
                if (neigh.get_x(), neigh.get_y()) not in attackers:
                    attack_value += 1
                    attackers.add((neigh.get_x(), neigh.get_y()))
                    neigh_army = neigh.get_army_id()
                    if neigh_army not in attacking_armies:
                        attack_value += self.armies[neigh_side][neigh_army].calculate_attack()
                        attacking_armies.add(neigh_army)
        damage = 0
        toughness = army.calculate_toughness()
        for roll in self.__roll_combat(attack_value):
            if not (toughness >> (roll - 1)) & 1:
                damage += 1
        army.kills = int(damage / 2)

    def __roll_combat(self, dice_count):
        roll_array = [random.randint(1, 10) for _ in range(dice_count)]
        return roll_array

    def __gather_resources(self):
        side = self.active_side()
        resources = 1
        for x, y in info.resources:
            bug_code = self.board[x, y]
            if bug_code == 0:
                continue
            bug = decode_bug(bug_code)
            if bug.get_side() != side:
                continue
            resources += self.armies[side][bug.get_army_id()].grasshooper_count
        self.active_player_resources = resources

    def __next_phase(self):
        if self.phase_type() != PhaseType.MOVE:
            self.update_armies()
        else:
            self.__winner = self.__check_winner()  # check winner after move
        self.phase += 1  # next phase
        if self.phase > 5:
            self.phase = 0
        if self.phase_type() == PhaseType.HATCH:
            self.__gather_resources()
        elif self.phase == PhaseType.COMBAT:
            self.__attack_all_opponents_armies()

    def __attack_all_opponents_armies(self):
        inactive_side = (self.active_side() == 0)
        for army_id in range(len(self.armies[inactive_side])):
            self.__attack_army(inactive_side, army_id)

    def __check_winner(self):
        bug_code = self.board[info.resources[0]]
        if bug_code == 0:
            return None
        side = decode_bug(bug_code).get_side()
        for res_id in [1, 2]:
            bug_code = self.board[info.resources[res_id]]
            if bug_code == 0 or decode_bug(bug_code).get_side() != side:
                return None
        return side
