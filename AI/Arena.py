import concurrent.futures
import datetime
import math
import os
import time
import pandas as pd


from AI.Bots.ExploringSwarmer import ExploringSwarmer
from AI.Bots.ExploringTerritorial import ExploringTerritorial
from AI.Bots.NNBot import NNBot
from AI.Bots.Swarmer import Swarmer
from AI.Bots.Territorial import Territorial
from Backend.GameMaster import GameMaster
from AI.Bots.RandomBot import RandomBot
from Backend.GameState import GameState
from AI.Zobrist import Zobrist
from AI.positionTable import update_position_table
from info import Side, PhaseType, ActionType


def perform_action(side, action, game):
    action_type = action[0]
    if action_type == ActionType.PASS:
        return game.end_phase(side)
    elif action_type == ActionType.KILL:
        return game.kill(side, action[1], action[2])
    elif action_type == ActionType.MOVE:
        return game.move(side, army_id=action[1], dirc=action[2])
    elif action_type == ActionType.HATCH:
        return game.hatch(side, bug_type=action[1], hatch_id=action[2])
    return False


class Arena(GameMaster):
    def __init__(self):
        super().__init__()
        self.zobrist = Zobrist()
        self.switch = None

    def new_game(self, white_bot, black_bot, update_position_table=False):
        players = [white_bot(Side.WHITE), black_bot(Side.BLACK)]
        game = GameState()
        steps = 0
        switched = False
        last_was_valid = True
        positions = {}
        while game.get_winner() is None and steps < self.steps_max and game.round < self.max_rounds:
            active_side = game.active_side()
            action = players[active_side].get_action(game)
            last_was_valid = perform_action(active_side, action, game)
            if update_position_table and game.phase_type() == PhaseType.MOVE:
                pos_hash = self.zobrist.zobrist_hash(game)
                prev_data = positions.get(pos_hash)
                if prev_data is None:
                    positions[pos_hash] = (game.position_code(), 1)
                else:
                    positions[pos_hash] = (prev_data[0], prev_data[1] + 1)
            steps += 1
            if self.switch is not None and self.switch > game.round and not switched:
                players = [Territorial(Side.WHITE), Territorial(Side.BLACK)]
                switched = True
        winner = game.get_winner()
        return winner, steps, positions

    def series(self, white_bot, black_bot, n_games, update_position_table=False):
        data = pd.DataFrame(columns=["Winner", "NTurns"])
        pos_data = {}
        for i in range(n_games):
            winner, nmoves, positions = self.new_game(white_bot, black_bot, update_position_table)
            data.loc[len(data.index)] = [winner, nmoves]
            if update_position_table:
                for k, v in positions.items():
                    prev_data = pos_data.get(k)
                    if prev_data is None:
                        pos_data[k] = (v[0], int(winner == 0), int(winner == 1), int(winner is None))
                    else:
                        pos_data[k] = (prev_data[0], prev_data[1] + int(winner == 0), prev_data[2] + int(winner == 1), prev_data[3] + int(winner is None))
        return data, pos_data

    def tournament(self, types_list, n_games, n_threads=8, position_table_path=""):
        suf = datetime.datetime.now().strftime("%d_%m_%H_%M_%S")
        path = f"../Data/Tournaments/{len(types_list)}BotsTournament{suf}"
        os.mkdir(path)
        pos_res = []
        for white in types_list:
            for black in types_list:
                res = []
                with concurrent.futures.ProcessPoolExecutor() as e:
                    futures = [e.submit(self.series, white, black, math.ceil(n_games / n_threads), bool(position_table_path)) for _ in range(n_threads)]
                    for f in concurrent.futures.as_completed(futures):
                        res.append(f.result()[0])
                        if position_table_path:
                            pos_res.append(f.result()[1])
                data = pd.concat(res, ignore_index=True)
                name = white.__name__ + "_" + black.__name__
                data.to_csv(path + "/" + name + ".csv")
                print(name + " series finished")
        if position_table_path:
            update_position_table(position_table_path, pos_res)


if __name__ == "__main__":
    a = Arena()
    a.max_rounds = 30
    s = time.time()
    a.switch = 15
    a.tournament([NNBot], 240, n_threads=6, position_table_path="../Data/PositionTables/Switch15NNPositionTable.p")
    print(round(time.time() - s, 5), "s")
