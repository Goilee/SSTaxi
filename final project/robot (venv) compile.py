import cv2
from random import choice
import Duckietown_two_lanes_pd.Moving as Moving
from Duckietown_two_lanes_pd.Moving import MoveController
import arucoDetector as ad
import numpy as np
from PIL import Image
import sys
import gym
import pyglet
from pyglet.window import key
from TCP.TCPClient import ClientSocket
from gym_duckietown.envs import DuckietownEnv
import traceback

connect_flag = False

if connect_flag:
    # cli_sock = ClientSocket(25565, 'taxi', '192.168.189.26')
    cli_sock = ClientSocket(25565, 'taxi', '192.168.190.75')
    # cli_sock = ClientSocket(25565, 'taxi', 'localhost')

env = DuckietownEnv(map_name="map_test")

mask = np.zeros([400, 400, 1], dtype='float32')

env.reset()
obs = env.step(np.array([0, 0]))[0]
env.render()

mover = MoveController()
mover.new_action(Moving.ACTION_MOVE_TO_CR)

key_handler = key.KeyStateHandler()
env.unwrapped.window.push_handlers(key_handler)

observ = np.uint8(np.zeros((480, 640, 3)))
mark_id = [255]

wait_data_move_flag = False
on_start_flag = True
turn_flag = False

def update(dt):
    global observ, mover, mark_id, wait_data_move_flag, on_start_flag, turn_flag
    img = cv2.cvtColor(observ, cv2.COLOR_BGR2RGB)
    found_marks = ad.find_aruco_markers(img, draw=False)
    new_mark_id = ad.filter_bboxs(found_marks, img.copy(), drawing=True, debug=False)
    if new_mark_id[0] != 255:
        mark_id = new_mark_id
    else:
        pass
        # print("unrecognized cross")
    print(round(env.cur_angle / np.pi, 1))
    if mover.get_action() == Moving.ACTION_STOP and not wait_data_move_flag and not turn_flag:
        # send data to, receive data from host,
        # set new action there
        # angle = int(round(env.cur_angle / np.pi, 1) * 10) + 10
        if on_start_flag:
            on_start_flag = False
            angle = round(env.cur_angle / np.pi, 1)
            print(angle, mark_id[0])
            if connect_flag:
                cli_sock.sendCrossList(angle, mark_id[0])
        else:
            print(mark_id[0])
            if connect_flag:
                cli_sock.sendCrossId(mark_id[0])
        mover.new_action(Moving.ACTION_MOVE_TO_CR)
        wait_data_move_flag = True
    elif mover.get_action() == Moving.ACTION_STOP and turn_flag:
        turn_flag = False
        mover.new_action(Moving.ACTION_MOVE_TO_CR)
    # print(mover.get_action(), mover.see_red, wait_data_move_flag)
    if not mover.see_red and wait_data_move_flag:
        mover.new_action("waiting")
        print("waiting move")
        cli_sock.sendSTR("get move")
        new_move = cli_sock.waitSTR()
        if new_move != Moving.ACTION_MOVE_TO_CR:
            turn_flag = True
        mover.new_action(new_move)
        wait_data_move_flag = False
        print(new_move)
    # main control of machine
    action = mover.get_move_values(env, observ, dt)

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
    observ, reward, done, info = env.step(action)

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

    # if done:
        # print("done!")
        # env.reset()

    env.render()


pyglet.clock.schedule_interval(update, 0.05)

# Enter main event loop
try:
    pyglet.app.run()
    env.close()
except:
    traceback.print_exc()
    if connect_flag:
        print("closed")
        cli_sock.close()
