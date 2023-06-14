import math

import numpy as np

from info import BugType
from Backend.Bug import decode_bug


class Army:

    def __init__(self):
        self.bugs = []
        self.was_attacked = False
        self.kills = 0
        self.grasshooper_count = 0
        self.moves_left = 5

    def add_bug(self, bug_code):
        self.bugs.append(bug_code)
        self.moves_left = min(self.moves_left, decode_bug(bug_code).get_moves_left())
        bug = decode_bug(bug_code)
        if bug.get_type() == BugType.GRASSHOOPER:
            self.grasshooper_count += 1

    def __str__(self):
        return f"Army. Moves left: {self.moves_left}. Bugs: " + " ".join(["{" + str(decode_bug(v)) + "}" for v in self.bugs])

    def calculate_toughness(self):
        toughness = 0
        for bug_code in self.bugs:
            toughness |= decode_bug(bug_code).get_toughness()
        return toughness

    def calculate_attack(self):
        attack_values = np.zeros(6, dtype=int)
        for bug_code in self.bugs:
            attack_values[decode_bug(bug_code).get_attack()] += 1
        for i in range(len(attack_values) - 1, 0, -1):
            if attack_values[i] >= math.ceil(len(self.bugs) / 2):
                return i
            attack_values[i - 1] += attack_values[i]
        return 0
