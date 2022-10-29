import gym
from gym import spaces
from gym.spaces import space
import numpy as np
from trader import trader_agent
import csv
import os
import config
import pandas as pd
from cryptomanager import historical_data_df
import time


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
        if len(self.positions) == 0:
            self.len_pos = 1
        else:
            self.len_pos = len(self.positions)
        
        self.n_actions = [ self.len_pos, # which position to take a peak at on each iteration
        CRYPTO_LEN, # which asset to look at that we haven't bought
        2,  # choose to buy or skip asset
        2  # choose to sell or hold asset
        ]
        
        self.action_space = spaces.MultiDiscrete(self.n_actions)
        self.observation_space = self.populate_obs_space(self.agent.get_cur_pos_df()[1])
        

        self.reward = 0

    def populate_obs_space(self,dict_in):
        dict_out = {}
        box = spaces.Box(low=-np.inf, high =np.inf , shape =(1,))
        for key in dict_in.keys():
            dict_out[key] = key
            inner_dict = {}
            for item in dict_in[key]:
                for item_key in item.keys():
                    inner_dict[item_key] = box
            dict_out[key] = spaces.Dict(inner_dict)
                
                    
        obs_space = spaces.Dict(dict_out)        
        
                    
        return obs_space

    def step(self, action):
        # print(action[0][1]) # just to help me remember how the hell that worked. This algorithim is fucked rn lol
        # observe current positions
        # loop through current positions, decide if we should sell them
            # make some observation about each position

        # loop through available tickers to determine which that we should buy
        # make some observation about each ticker
        # for crypto in usd_crypto:
        #     self.observation += np.asfarray(historical_data_df(cryptos=[crypto]).to_numpy().flatten())
        if self.len_pos > 1:
            # position in question
            if action[0][3] == 1: # sell position in question
                profit = self.agent.sell_position_market(self.positions[action[0][0]])
                self.reward += profit
                # if sell was profitable, add reward
                # if sell was detrimental, reduce reward

        # if no positions in portfolio, reduce reward
        if action[0][2]: # should buy some asset in question
            print(usd_crypto[action[0][1]])
            self.agent.buy_position_at_market(usd_crypto[action[0][1]])
        info = {}
        self.observation_space = self.populate_obs_space(self.agent.get_cur_pos_df()[1])
        self.obersvation = self.agent.get_cur_pos_df()[1]

        # subscribe to stock bars or some shit

        return self.observation, self.reward, self.done, info



    def reset(self):
        self.done = False
        self.positions = self.agent.get_position_tickers()
        # self.past_trades = np.array()
        self.observation_space = self.populate_obs_space(self.agent.get_cur_pos_df()[1])
        self.obersvation = self.agent.get_cur_pos_df()[1]
        if len(self.positions) == 0:
            self.len_pos = 1
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
        self.agent.cancel_orders()
