# Gym stuff
import gym
import gym_anytrading

# Stable baselines - rl stuff
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3 import A2C

# Processing libraries
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from trader import trader_agent
from cryptomanager import historical_data_df

tester = trader_agent()

df = historical_data_df()

env = gym.make('forex-v0', df=df, frame_bound=(5,100), window_size=5)


# env_maker = lambda: gym.make('forex-v0', df=df, frame_bound=(5,100), window_size=5)
# env = DummyVecEnv([env_maker])  

# model = A2C('MlpLstmPolicy', env, verbose=1) 
# model.learn(total_timesteps=1000000)

# env = gym.make('forex-v0', df=df, frame_bound=(90,110), window_size=5)
# obs = env.reset()


# while True: 
#     obs = obs[np.newaxis, ...]
#     action, _states = model.predict(obs)
#     obs, rewards, done, info = env.step(action)
#     if done:
#         print("info", info)
#         break