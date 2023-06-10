import numpy as np

from Backend.Bug import decode_bug


def visualize_board(board):
    for row in board:
        print()
        for bug_code in row:
            if bug_code == 0:
                print("[  ]", end="")
            else:
                print(f"[{decode_bug(bug_code).short_str()}]", end="")
    print()
