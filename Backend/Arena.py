import concurrent.futures
import math
import time

from Backend.GameMaster import GameMaster
from AI.RandomBot import RandomBot
from Backend.info import Side


class Arena(GameMaster):
    def __init__(self):
        super().__init__()

    def duel(self, white_bot, black_bot):
        return self.new_game(white_bot(Side.WHITE), black_bot(Side.BLACK))

    def series(self, white_bot, black_bot, n_threads, n_games):
        with concurrent.futures.ProcessPoolExecutor() as e:
            futures = [e.submit(self.duel, white_bot, black_bot, math.ceil(n_games / n_threads)) for _ in
                       range(n_threads)]


if __name__ == "__main__":
    a = Arena()
    results = [0, 0, 0]
    s = time.time()
    for _ in range(100):
        r = a.duel(RandomBot, RandomBot)
        if r is None:
            results[2] += 1
        else:
            results[r] += 1
    print(results)
    print(round(time.time() - s, 5), "s")
