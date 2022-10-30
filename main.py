import tensorboard
import assetpicker as ap
from config import *
import os
import concurrent.futures
from trader import trader_agent
from stable_baselines3 import PPO
from stable_alpaca import paca_env
import sys
from stable_baselines3.common.env_checker import check_env
import time

trader = trader_agent()
env = paca_env(trader)
# # Instantiate the agent
model = PPO("MultiInputPolicy", env, verbose=1)
# # Train the agent and display a progress bar
# # Save the agent
# model.save("dqn_lunar")
# del model  # delete trained model to demonstrate loading

# # Load the trained agent
# # NOTE: if you have loading issue, you can pass `print_system_info=True`
# # to compare the system on which the model was trained vs the current one
# # model = DQN.load("dqn_lunar", env=env, print_system_info=True)
# model = DQN.load("dqn_lunar", env=env)

# # Evaluate the agent
# # NOTE: If you use wrappers with your environment that modify rewards,
# #       this will be reflected here. To evaluate with original rewards,
# #       wrap environment in a "Monitor" wrapper before other wrappers.
# mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=10)

# # Enjoy trained agent
# obs = env.reset()
# for i in range(1000):
#     action, _states = model.predict(obs, deterministic=True)
#     obs, rewards, dones, info = env.step(action)
#     env.render()

def main():
    try:
        trader.run()
        run_model()
        # check_env(env)
    except KeyboardInterrupt:
        print('Interrupted. Closing Model')
        env.close()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

def load_model(path, env):
    model = PPO.load(path, env)
    return model

def run_model():
    model_counter = 0
    while True:
        obs = env.reset()
        print("observation: ",obs)
        action = model.predict(obs)
        # print(action)
        # env.render()
        obs, reward, done, info = env.step(action)
        # print(reward)
        if model_counter % 10000 == 0:
            model.save(f"{os.path.join(MODEL_PATH), str(model_counter)}")
        

if __name__ == "__main__":
    main()


# model.learn(total_timesteps=int(10000), progress_bar=True, tensorboard=LOG_PATH)