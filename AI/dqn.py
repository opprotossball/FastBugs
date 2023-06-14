from keras.models import Sequential
from keras.layers import Dense, Flatten, Input
from keras.optimizers import Adam
from rl.agents import DQNAgent
from rl.memory import SequentialMemory
from rl.policy import BoltzmannQPolicy, MaxBoltzmannQPolicy
from AI.GameEnv import GameEnv
from AI.actionMap import move_action_list


def build_model(states_shape, n_actions):
    model = Sequential()
    n_states = states_shape[0]
    model.add(Flatten(input_shape=(1, n_states)))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(150, activation='relu'))
    model.add(Dense(200, activation='relu'))
    model.add(Dense(150, activation='relu'))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(n_actions, activation='linear'))
    return model


def build_agent(model, actions):
    policy = BoltzmannQPolicy()
    memory = SequentialMemory(limit=50000, window_length=1)
    dqn = DQNAgent(model=model, memory=memory, policy=policy, nb_actions=actions, nb_steps_warmup=1000, target_model_update=0.1)
    return dqn


def train_agent(file_path, nb_steps, learning_rate, load=False):
    env = GameEnv()
    model = build_model(env.observation_space.shape, len(move_action_list))
    model.summary()
    dqn = build_agent(model, len(move_action_list))
    dqn.compile(Adam(lr=learning_rate), metrics=['mae'])
    if load:
        dqn.load_weights(file_path)
    dqn.fit(env, nb_steps=nb_steps, visualize=False, verbose=1)
    dqn.save_weights(file_path, overwrite=True)


def test_agent(file_path, nb_episodes):
    env = GameEnv()
    env.test = True
    model = build_model(env.observation_space.shape, len(move_action_list))
    dqn = build_agent(model, len(move_action_list))
    dqn.compile(Adam(lr=1e-2), metrics=['mae'])
    dqn.load_weights(file_path)
    _ = dqn.test(env, nb_episodes=nb_episodes, visualize=True)


if __name__ == "__main__":
    #test_agent('Models/DQN/dqn1_weights.h5f', 1)
    train_agent('Models/DQN/dqn2_weights.h5f', 200000, learning_rate=1e-6, load=False)
