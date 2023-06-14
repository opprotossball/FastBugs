from Backend import board
from info import board_size, resources

INF = 99
MAX_DIST = 7


def get_dist(x, y, from_hatch):
    return dists_map[from_hatch][x][y]


def __dfs(x, y, depth):
    depth += 1
    for nx, ny in board.neigh_generator(x, y):
        if dist[nx][ny] > depth:
            dist[nx][ny] = depth
            __dfs(nx, ny, depth)


dists_map = []
size = board_size
for x, y in resources:
    dist = [[INF for _ in range(2 * size - 1)] for _ in range(2 * size - 1)]
    dist[x][y] = 0
    __dfs(x, y, 0)
    dists_map.append(dist)
