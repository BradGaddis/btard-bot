import gym
from gym import spaces
import numpy as np
from trader import trader_agent

N_DISCRETE_ACTIONS = 3 # buy, sell, and hold

class paca_env(gym.Env):
    def __init__(self, agent) -> None:
        super(paca_env, self).__init__
        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.Discrete(N_DISCRETE_ACTIONS)
        # Example for using image as input (channel-first; channel-last also works):
        self.observation_space = spaces.Box(low=0, high=255,
                                            shape=(1, ), dtype=np.float32)
        self.agent = agent


    def step(self, action):
        # observe current positions
        postion = "BTC/USD"

        # determine how to find an asset in the first place


        # Do not allow 'buy' if account has too many positions, open or otherwise
        if action == 1:        
            self.agent.buy_position()
            # add some reward 
        elif action == 2:
            # hold
            # add some base reward
            pass
        elif action == 3:
            self.agent.sell_position()
            # if sell was profitable, add reward
            # if sell was detrimental, reduce reward

        # get positions
        info = {}

        # subscribe to stock bars or some shit
        
        return self.observation, self.reward, self.done, info



    def reset(self):
        self.done = False
        self.positions
        self.past_trades

        
        return self.observation  # reward, done, info can't be included
    def render(self, mode="human"):
        pass
    def close (self):
        pass