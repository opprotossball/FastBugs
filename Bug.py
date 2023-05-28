import info
from info import Side, BugType


def get_bug_side(bug_code):
    return Side(bug_code & 1)


def get_bug_type(bug_code):
    return BugType((bug_code >> 1) & 3)


def get_bug_x(bug_code):
    return (bug_code >> 3) & 15


def get_bug_y(bug_code):
    return (bug_code >> 7) & 15


def get_bug_moves_left(bug_code):
    return (bug_code >> 11) & 7

#
# def get_bug_army_id(bug_code):
#     return (bug_code >> 15) & 15


def decode_bug(bug_code):
    if bug_code == 0:
        return None
    side = get_bug_side(bug_code)
    bug_type = get_bug_type(bug_code)
    x = get_bug_x(bug_code)
    y = get_bug_y(bug_code)
    moves_left = get_bug_moves_left(bug_code)
    # army_id = get_bug_army_id(bug_code)
    return Bug(side, bug_type, x, y, moves_left)


class Bug:

    def __init__(self, side, bug_type, x, y, moves_left=None, army_id=None):
        self.bug_code = 0
        self.set_side(side)
        self.set_type(bug_type)
        self.set_x(x)
        self.set_y(y)
        if moves_left is None:
            self.set_moves_left(self.get_max_move())
        else:
            self.set_moves_left(moves_left)
        # if army_id is None:
        #     self.set_army_id(info.army_id_not_assigned)
        # else:
        #     self.set_army_id(army_id)

    def set_side(self, side):
        self.bug_code &= ~1
        self.bug_code |= side

    def set_type(self, bug_type):
        self.bug_code &= ~(3 << 1)
        self.bug_code |= (bug_type << 1)

    def set_x(self, x):
        self.bug_code &= ~(15 << 3)
        self.bug_code |= (x << 3)

    def set_y(self, y):
        self.bug_code &= ~(15 << 7)
        self.bug_code |= (y << 7)

    def set_moves_left(self, moves_left):
        self.bug_code &= ~(7 << 11)
        self.bug_code |= (moves_left << 11)

    # def set_army_id(self, army_id):
    #     self.bug_code &= ~(15 << 15)
    #     self.bug_code |= (army_id << 15)

    def get_attack(self):
        return info.bug_attack[get_bug_type(self.bug_code)]

    def get_max_move(self):
        return info.bug_move[get_bug_type(self.bug_code)]

    def get_toughness(self):
        return info.bug_toughness[get_bug_type(self.bug_code)]

    def get_side(self):
        return get_bug_side(self.bug_code)

    def get_type(self):
        return get_bug_type(self.bug_code)

    def get_x(self):
        return get_bug_x(self.bug_code)

    def get_y(self):
        return get_bug_y(self.bug_code)

    def get_moves_left(self):
        return get_bug_moves_left(self.bug_code)

    # def get_army_id(self):
    #     return get_bug_army_id(self.bug_code)

    def __str__(self):
        lst = [self.get_side().name, self.get_type().name, f"X:{self.get_x()}", f"Y:{self.get_y()}" + f" Moves:{self.get_moves_left()}"]
        return " ".join(lst)
