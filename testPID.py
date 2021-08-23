from PIL import Image
import argparse
import sys
import gym
import numpy as np
import pyglet
from pyglet.window import key
import cv2
import random as rng
from gym_duckietown.envs import DuckietownEnv
import Moving

mask = np.zeros([400, 400, 1], dtype='float32')


def update(dt):
    global obs, mover

    if mover.get_action() == Moving.ACTION_STOP:
        # send data to, receive data from host,
        # set new action there
        # mover.new_action(?)
        pass

    # main control of machine
    action = mover.get_move_values(env, obs, dt)

    if key_handler[key.UP]:
        action += np.array([3, 0])
    if key_handler[key.DOWN]:
        action -= np.array([3, 0])
    if key_handler[key.LEFT]:
        action += np.array([0, 6])
    if key_handler[key.RIGHT]:
        action += np.array([0, -6])

    cv2.circle(mask, (env.cur_pos[[0, 2]]*100).astype("int32"), 1, [1])

    # something(obs)
    obs, reward, done, info = env.step(action)

    if key_handler[key.W]:
        mover.new_action(Moving.ACTION_MOVE_TO_CR)
    if key_handler[key.A]:
        mover.new_action(Moving.ACTION_MOVE_LEFT)
    if key_handler[key.D]:
        mover.new_action(Moving.ACTION_MOVE_RIGHT)
    if key_handler[key.S]:
        mover.new_action(Moving.ACTION_STOP)
    if key_handler[key.X]:
        mover.new_action(Moving.ACTION_MOVE_TURNOVER)
    if key_handler[key.R]:
        env.reset()

    if done:
        print("done!")
        # env.reset()

    env.render()


env = DuckietownEnv()

env.reset()
obs = env.step(np.array([0, 0]))[0]
env.render()

mover = Moving.MoveController()
# leave this for machine to drive to first crossroad to initialize
mover.new_action(Moving.ACTION_MOVE_TO_CR)

key_handler = key.KeyStateHandler()
env.unwrapped.window.push_handlers(key_handler)

pyglet.clock.schedule_interval(update, 0.05)

# Enter main event loop
pyglet.app.run()

env.close()
