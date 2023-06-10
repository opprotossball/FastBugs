from info import board_array_size, board_size, Direction, blocked_tiles

neighs = [
    (0, 1),
    (-1, 1),
    (0, -1),
    (1, 0),
    (1, -1),
    (-1, 0)
]


def valid_tile(x, y):
    if (x, y) in blocked_tiles:
        return False
    if not ((0 <= x < board_array_size) and (0 <= y < board_array_size)):
        return False
    if (x + y < board_size - 1) or (x + y >= 2 * board_array_size - board_size):
        return False
    return True


def neigh_coords(x, y, dirc):
    # if isinstance(dirc, Direction):
    #     dirc = dirc.value()
    return x + neighs[dirc][0], y + neighs[dirc][1]


def neigh_generator(x, y):
    for xo, yo in neighs:
        nx = x + xo
        ny = y + yo
        if valid_tile(nx, ny):
            yield nx, ny
