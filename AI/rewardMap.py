from Backend import board
from info import board_array_size, resources


INF = 99
distance_reward = {
    0: 10,
    1: 5,
    2: 3,
    3: 2,
    4: 1
}


class RewardMap:

    def __init__(self):
        self.reward = [[INF for _ in range(board_array_size)] for _ in range(board_array_size)]

        for x, y in resources:
            self.reward[x][y] = 0
            self.__dfs(x, y, 0)

        for row in self.reward:
            row[:] = [distance_reward.get(dist, 0) for dist in row]

    def __dfs(self, x, y, depth):
        depth += 1
        for nx, ny in board.neigh_generator(x, y):
            if self.reward[nx][ny] > depth:
                self.reward[nx][ny] = depth
                self.__dfs(nx, ny, depth)

    def get_reward(self, x, y):
        return self.reward[x][y]


rewardMap = RewardMap()
