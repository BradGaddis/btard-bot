import gym
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class TradingEnv(gym.Env):
    def __init__(self, df: pd.DataFrame) -> None:
        # Store the dataframe that contains the historical data
        self.df = df

        # Set the current index to the beginning of the dataframe
        self.current_index = 0

        # Store the current row in the dataframe
        self.current_row = None

        # Set the "done" flag to False
        self.done = False
        self.rewards = []
        # Define the action space and the observation space
        self.action_space = gym.spaces.Discrete(3)  # "Buy", "Sell", or "Hold"
        self.observation_space = gym.spaces.Box(
            low=0, high=1, shape=(len(df.columns),), dtype=np.float32
        )

        # Translates action to "buy", "sell", or "hold"
        self.action_dict= {0: "Buy", 1: "Sell", 2: "Hold"}

    def plot_results(self):
        plt.figure(figsize=(15, 6))
        plt.plot(self.rewards)
        plt.xlabel("Step")
        plt.ylabel("Reward")
        plt.show()

    def _get_reward(self, prev_close: float, current_close: float, action: int) -> float:
        # Calculate the reward for the given action
        if action == 0:
            # Buy
            return current_close - prev_close
        elif action == 1:
            # Sell
            return prev_close - current_close
        else:
            # Hold
            return 0
    

    def reset(self):
        # Reset the current index to the beginning of the dataframe
        self.current_index = 0

        # Store the first row in the dataframe
        self.current_row = self.df.iloc[self.current_index]

        # Set the "done" flag to False
        self.done = False

        self.plot_results()

        # Return the first row in the dataframe as the observation
        return self.current_row.values

    def step(self, action: int):
        # Advance to the next time step
        self.current_index += 1
        self.current_row = self.df.iloc[self.current_index]

        # Set the "done" flag to True if we have reached the end of the dataframe
        self.done = self.current_index >= len(self.df) - 1

        # Calculate the reward for the given action
        prev_close = self.df.iloc[self.current_index - 1]["Close"]
        current_close = self.current_row["Close"]
        reward = self._get_reward(prev_close, current_close, action)

        # Return the observation, the reward, the "done" flag, and an empty dictionary
        return self.current_row.values, reward, self.done, {}
