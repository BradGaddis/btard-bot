import gym
from gym import spaces
import numpy as np
from trader import trader_agent
import csv
import os
import config

def list_cryptos():
    out = []
    with open(os.path.join(config.DATA_PATH, "tradable_crypto.csv"), "r") as f:
        reader = csv.reader(f)
        for row in reader:
            out.append(row)
    return out[0]


N_MULTIDISCRETE_ACTIONS = [3, # buy, sell, or hold
1] 

class paca_env(gym.Env):
    def __init__(self, agent) -> None:
        super(paca_env, self).__init__
        self.action_space = spaces.MultiDiscrete(N_MULTIDISCRETE_ACTIONS)
        # Example for using image as input (channel-first; channel-last also works)D:
        self.observation_space = spaces.Box(low=0, high=255,
                                            shape=(1, ), dtype=np.float32)
        self.trade_agent = agent

    def step(self, action):
        # observe current positions
        postion = "BTC/USD"

        # determine how to find an asset in the first place


        # Do not allow 'buy' if account has too many positions, open or otherwise
        if action == 1:        
            self.trade_agent.buy_position(action)
            # add some reward 
        elif action == 2:
            # hold
            # add some base reward just for holding
            pass
        elif action == 3:
            self.trade_agent.sell_position(action)
            # if sell was profitable, add reward
            # if sell was detrimental, reduce reward

        # get positions
        info = {}

        # subscribe to stock bars or some shit
        
        return self.observation, self.reward, self.done, info



    def reset(self):
        self.done = False
        self.positions
        self.past_trades = np.array()

        
        return self.observation  # reward, done, info can't be included
    def render(self, mode="human"):
        pass
    def close (self):
        pass