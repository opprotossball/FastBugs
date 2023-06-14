import pickle
import time

import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow import keras
from keras import layers
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split

from Backend.Bug import decode_bug
from Backend.GameState import GameState
from info import board_array_size


class PositionEvaluator:

    def __init__(self, position_table_path=None, path=None):
        self.model = None
        self.bug_codes = [[1, 2, 3, 4], [-1, -2, -3, -4]]
        self.train_test = 0.9
        self.threshold = 5
        self.save_path = "Models/PosEv/tmp/" if path is None else path
        self.position_table_path = "../Data/PositionTables/PositionTable.p" if position_table_path is None else position_table_path

    def build_dnn(self):
        self.model = keras.Sequential([
            layers.Dense(50, input_shape=(board_array_size * (board_array_size + 1), )),
            layers.Dense(100, activation='relu'),
            layers.Dense(150, activation='relu'),
            layers.Dense(100, activation='relu'),
            layers.Dense(50, activation='relu'),
            # layers.Dense(20, activation='relu'),
            # layers.Dense(100, activation='relu'),
            layers.Dense(3)
        ])
        self.model.compile(loss='mean_absolute_error', optimizer=Adam(5e-6))
        self.model.summary()

    def prepare_data(self, threshold=None):
        if threshold is None:
            threshold = self.threshold
        s = time.time()
        with open(self.position_table_path, "rb") as f:
            pos_table = pickle.load(f)
            xs = []
            ys = []
        for k, v in pos_table.items():
            if sum(v[1:]) >= threshold:
                xs.append(self.position2array(v[0]))
                ys.append(self.norm(v[1:]))
        del pos_table
        print("Data prepared in: ", round(time.time() - s, 2), "s")
        print(len(xs), " records.")
        return xs, ys

    def norm(self, arr):
        s = sum(arr)
        if s == 0:
            return [0 for _ in arr]
        return [v/s for v in arr]

    def visualize(self, history):
        fig, axes = plt.subplots(figsize=(8, 5))

        # Plot loss
        axes.plot(history.history['loss'])
        axes.plot(history.history['val_loss'])
        axes.set_title('Model Loss')
        axes.set_ylabel('Loss')
        axes.set_xlabel('Epoch')
        axes.legend(['Train', 'Validation'], loc='upper right')
        plt.tight_layout(pad=2.0)
        plt.show()

    def position2array(self, pos_code):
        arr = np.zeros((board_array_size, board_array_size + 1))
        bugs = pos_code.split("-")
        for i in range(1, len(bugs)):
            bug = decode_bug(int(bugs[i]))
            arr[bug.get_x(), bug.get_y()] = self.bug_codes[bug.get_side()][bug.get_type()]
        arr[-1] = 1 - 2 * (bugs[0][0] == "B")
        return arr.flatten()

    def game_state2array(self, game_state):
        arr = np.zeros((board_array_size, board_array_size + 1))
        for bug in game_state.bugs_iterate:
            arr[bug.get_x(), bug.get_y()] = self.bug_codes[bug.get_side()][bug.get_type()]
        arr[-1] = 1 - 2 * game_state.active_side()
        return arr.flatten()

    def train(self):
        self.build_dnn()
        xs, ys = self.prepare_data(self.threshold)
        xs = np.array(xs)
        ys = np.array(ys)
        x_train, x_test, y_train, y_test = train_test_split(xs, ys, test_size=1-self.train_test, random_state=2137)
        history = self.model.fit(
            x_train,
            y_train,
            validation_split=self.train_test,
            batch_size=32,
            epochs=400,
            validation_data=(x_test, y_test)
        )
        self.visualize(history)
        self.model.save(self.save_path)

    def test(self):
        xs, ys = self.prepare_data(self.threshold)
        xs = np.array(xs)
        ys = np.array(ys)
        x_train, x_test, y_train, y_test = train_test_split(xs, ys, test_size=1 - self.train_test)
        self.load()
        self.model.summary()
        for t in x_test:
            t = np.reshape(t, (1, -1))
            print(self.model.predict(t))

    def load(self, path=None):
        if path is None:
            path = self.save_path
        self.model = keras.models.load_model(path)

    def predict_from_game_state(self, pos_code):
        if self.model is None:
            self.load()
        inp = self.position2array(pos_code)
        return self.model.predict(np.reshape(inp, (1, -1)), verbose=0)

    def predict(self, position):
        if self.model is None:
            self.load()
        if isinstance(position, GameState):
            inp = self.game_state2array(position)
        elif isinstance(position, str):
            inp = self.position2array(position)
        else:
            raise Exception("Invalid position type given!")
        return self.model.predict(np.reshape(inp, (1, -1)), verbose=0)


#evaluator = PositionEvaluator("Data/PositionTables/ExploringTerritorialPositionTable.p", path="Models/PosEv/new3/")
#evaluator.load()

if __name__ == "__main__":
    pos = PositionEvaluator("C:/Users/janst/source/Games/Robale/FastBugs/Data/PositionTables/ExploringTerritorialPositionTable.p", "Models/PosEv/new0/")
    pos.train()
    #pos.test()
