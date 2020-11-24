from gym.envs.registration import register

register(
        id='bpp2d-v0',
        entry_point='gym_bpp_2d.envs:BppEnv',
    )
