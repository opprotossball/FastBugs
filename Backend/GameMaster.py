from Backend.GameState import GameState
from info import ActionType, Side


class GameMaster:

    def __init__(self):
        self.game = None
        self.players = []
        self.steps = 0
        self.steps_max = 1200

    def new_game(self, white_player, black_player):
        self.players = [white_player, black_player]
        print(white_player.side)
        print(black_player.side)
        self.game = GameState()
        while self.game.get_winner() is None and self.steps < self.steps_max:
            active_side = self.game.active_side()
            action = self.players[active_side].get_action(self.game)
            self.perform_players_action(active_side, action)
            self.steps += 1
        winner = self.game.get_winner()
        if winner is not None:
            print(f"Game ended with {Side(winner)} victory in {self.steps}")
        else:
            print("Game ended in a draw")

    def perform_players_action(self, side, action):
        action_type = action[0]
        if action_type == ActionType.PASS:
            self.game.end_phase(side)
        elif action_type == ActionType.KILL:
            self.game.kill(side, action[1], action[2])
        elif action_type == ActionType.MOVE:
            self.game.move(side, army_id=action[1], dirc=action[2])
        elif action_type == ActionType.HATCH:
            self.game.hatch(side, bug_type=action[1], hatch_id=action[2])
