import gym
from gym import spaces
import numpy as np
from trader import trader_agent
import csv
import os
import config
import pandas as pd
import cryptomanager as cryptoman


def list_cryptos():
    out = []
    with open(os.path.join(config.DATA_PATH, "tradable_crypto.csv"), "r") as f:
        reader = csv.reader(f)
        for row in reader:
            out.append(row)
    return out[0]


def crypto_usd():
    out = []
    for crypto in list_cryptos():
        if crypto.split("/")[1] == "USD":
            out.append(crypto)
    return out

usd_crypto = crypto_usd()
crypto_len = len(usd_crypto)

N_MULTIDISCRETE_ACTIONS = [3, # buy, sell, or hold
crypto_len # which asset to look at
]


# maybe use a dict for actions space
class paca_env(gym.Env):
    def __init__(self, agent) -> None:
        super(paca_env, self).__init__
        self.action_space = spaces.MultiDiscrete(N_MULTIDISCRETE_ACTIONS)
        self.agent = agent
        self.observation = self.agent.get_all_orders_df().to_numpy()
        self.obs_shape = self.observation.shape
        self.observation_space = spaces.Box(low=0, high=1, shape = self.obs_shape)
        self.positions = agent.get_position_tickers()
        self.reward = 0
        print(self.obs_shape)
    def step(self, action):
        # observe current positions
        # loop through current positions, decide if we should sell them
            # make some observation about each position

        # loop through available tickers to determine which that we should buy
        # make some observation about each ticker
        for crypto in usd_crypto:
            # self.observation + cryptoman
            pass
        


        # Do not allow 'buy' if account has too many positions, open or otherwise
        if action[0] == 0:        
            self.trade_agent.buy_position(action)
            # add some reward 
        elif action[0] == 1:
            # hold
            # add some base reward just for holding
            # increas reward so long as holding and profit is increasing
            pass
        elif action[0] == 2:
            self.trade_agent.sell_position(action)
            # if sell was profitable, add reward
            # if sell was detrimental, reduce reward

        # get positions
        info = {}
        
        # subscribe to stock bars or some shit
        self.obs_shape = self.observation.shape


        self.observation_space = spaces.Box(low=0, high=1, shape = self.obs_shape)
        return self.observation, self.reward, self.done, info



    def reset(self):
        self.done = False
        self.positions = self.agent.get_position_tickers()
        # self.past_trades = np.array()
        self.observation = self.agent.get_all_orders_df().to_numpy()
        self.obs_shape = self.observation.shape
        self.observation_space = spaces.Box(low=0, high=1, shape = self.obs_shape)

        return self.observation  # reward, done, info can't be included
    def render(self, mode="human"):
        pass
    def close (self):
        pass
