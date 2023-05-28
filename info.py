from enum import IntEnum

import numpy as np

# board layout
board_array_size = 9
board_size = 5
resources = [(5, 4), (2, 7), (5, 1)]
white_hatchery = [(0, 5), (0, 4), (1, 3)]
black_hatchery = [(7, 5), (8, 4), (8, 3)]
hatcheries = [white_hatchery, black_hatchery]
blocked_tiles = []

# bug stats
bug_cost = [1, 1, 2, 3]
bug_attack = [0, 1, 3, 5]
bug_move = [3, 4, 4, 2]
bug_toughness = [
    0b00000001,  # 1
    0b00001100,  # 3, 4
    0b00000111,  # 1, 2, 3
    0b00111000,  # 4, 5, 6
]

army_id_not_assigned = 15


def starting_bugs():
    return np.array([[3, 3, 3, 3], [3, 3, 3, 3]])


class Phase(IntEnum):
    W_COMBAT = 0
    W_MOVE = 1
    W_HATCH = 2
    B_COMBAT = 3
    B_MOVE = 4
    B_HATCH = 5


class BugType(IntEnum):
    GRASSHOOPER = 0
    ANT = 1
    SPIDER = 2
    BEETLE = 3


class Side(IntEnum):
    WHITE = 0
    BLACK = 1


class Direction(IntEnum):
    ES = 0
    WS = 1
    WN = 2
    W = 3
    EN = 4
    E = 5


