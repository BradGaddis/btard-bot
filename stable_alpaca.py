import gym
from gym import spaces
import numpy as np
from trader import trader_agent
import csv
import os
import config
import pandas as pd
from cryptomanager import historical_data_df


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
CRYPTO_LEN = len(usd_crypto)



# maybe use a dict for actions space
class paca_env(gym.Env):
    def __init__(self, agent) -> None:
        super(paca_env, self).__init__
        self.agent = agent
        self.positions = self.agent.get_position_tickers() # the assets that we are presently holding
        self.len_pos = len(self.positions)

        self.n_actions = [ self.len_pos, # which position to take a peak at on each iteration
        CRYPTO_LEN, # which asset to look at that we haven't bought
        2,  # choose to buy or skip asset
        2  # choose to sell or hold asset
        ]
        
        self.action_space = spaces.MultiDiscrete(self.n_actions)
        self.observation = self.agent.get_all_orders_df().to_numpy()
        self.obs_shape = self.observation.shape
        self.observation_space = spaces.Box(low=0, high=1, shape = self.obs_shape)
        self.reward = 0
        print("idk butts or something" , self.obs_shape)

        
    def step(self, action):
        # observe current positions
        # loop through current positions, decide if we should sell them
            # make some observation about each position

        # loop through available tickers to determine which that we should buy
        # make some observation about each ticker
        for crypto in usd_crypto:
            self.observation + historical_data_df(cryptos=crypto).to_numpy()
        

        # Do not allow 'buy' if account has too many positions, open or otherwise
        if action[2] == 1:        
            self.trade_agent.buy_position_at_market(usd_crypto[action[1]])
            # add some reward 
        elif action[0] == 1:
            # hold
            # add some base reward just for holding
            # increase reward so long as holding and profit is increasing
            pass
        elif action[0] == 2:
            # how do I know if sell was profitable?
            # loop through positions, sell one?
            for position in self.positions:
                pass

            self.trade_agent.sell_position(action)
            # if sell was profitable, add reward
            # if sell was detrimental, reduce reward

        # if no positions in portfolio, reduce reward

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
        self.len_pos = len(self.positions)
        self.n_actions = [ self.len_pos, # which position to take a peak at on each iteration
        CRYPTO_LEN, # which asset to look at that we haven't bought
        2,  # choose to buy or skip asset
        2  # choose to sell or hold asset
        ]
        self.action_space = spaces.MultiDiscrete(self.n_actions)

        return self.observation  # reward, done, info can't be included
    def render(self, mode="human"):
        pass
    def close (self):
        pass
