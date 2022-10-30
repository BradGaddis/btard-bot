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
        self.observation_space = self.populate_obs_space(self.agent.get_cur_pos_df()[0])
        

        self.reward = 0


    def populate_obs_space(self,dict_in):
        dict_out = {}
        for key in dict_in.index:
            shape = dict_in[key:key].to_numpy().shape
            # print(key)
            box = spaces.Box(low=-np.inf, high =np.inf , shape = shape)
            dict_out[key] = box
                    
        obs_space = spaces.Dict(dict_out)        
        
        return obs_space

    def step(self, action):
        # print(action[0][1]) # just to help me remember how the hell that worked. This algorithim is fucked rn lol

        # position in question
        asset_to_sell = self.positions[action[0][0]]

        selling = False

        if self.len_pos > 1:
            if action[0][3] == 1: # sell position in question
                # if sell was profitable, add reward # if sell was detrimental, reduce reward
                profit = self.agent.sell_position_market(asset_to_sell)
                self.reward += profit
                selling = True

        crypto_to_buy = usd_crypto[action[0][1]]
        # if no positions in portfolio, reduce reward
        if not crypto_to_buy == asset_to_sell and not selling:
            if action[0][2]: # should buy some asset in question
                self.agent.buy_position_at_market(crypto_to_buy)

        # subscribe to stock bars or some shit TODO

        obs = self.get_obs(self.agent.get_cur_pos_df()[0], self.positions[action[0][0]])
        
        self.observation_space = self.populate_obs_space(self.agent.get_cur_pos_df()[0])
        
        info = {}
        return obs, self.reward, self.done, info

    def get_obs(self,df, asset):
        row = df[asset:asset]
        nparr = np.ndarray.astype( row.to_numpy() , dtype=np.float64)
        output = {asset : nparr}
        return output

    def get_all_obs(self,df):
        output = {}
        for asset in df.index:
            output[asset] = np.ndarray.astype(  df[asset:asset].to_numpy() , dtype=np.float64)
        return output
        
    def reset(self):
        self.done = False
        self.positions = self.agent.get_position_tickers()
        self.len_pos = len(self.positions)
        if len(self.positions) == 0:
            self.len_pos = 1
        self.n_actions = [ self.len_pos, # which position to take a peak at on each iteration
        CRYPTO_LEN, # which asset to look at that we haven't bought
        2,  # choose to buy or skip asset
        2  # choose to sell or hold asset
        ]
        self.action_space = spaces.MultiDiscrete(self.n_actions)

        obs = self.get_all_obs(self.agent.get_cur_pos_df()[0])

        return obs  # reward, done, info can't be included

    def render(self, mode="human"):
        pass

    def close (self):
        self.agent.cancel_orders()
