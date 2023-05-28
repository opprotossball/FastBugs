import numpy as np

from Bug import Bug, decode_bug


class Army:

    def __init__(self):
        self.bugs = []
        self.moves_left = 5

    def add_bug(self, bug_code):
        self.bugs.append(bug_code)
        self.moves_left = min(self.moves_left, decode_bug(bug_code).get_moves_left())

    def __str__(self):
        return f"Army. Moves left: {self.moves_left}. Bugs: " + " ".join(["{" + str(decode_bug(v)) + "}" for v in self.bugs])
