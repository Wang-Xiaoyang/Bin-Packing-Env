# this is to test the 2d bpp env

import gym
env = gym.make('gym_bpp_2d:bpp2d-v0')

obs = env.reset()


for t in range(10):
    print(obs[0])
    action = env.action_space.sample()
    obs, reward, done, _ = env.step(action)

    if done:
        print("Episode finished after {} timesteps".format(t+1))
        print(reward)
        break
