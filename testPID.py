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

mask = np.zeros([400, 400, 1], dtype='float32')


def glue(mat):
    return np.append(np.append(mat[:, :, 0], mat[:, :, 1], 0), mat[:, :, 2], 0)


def get_ct_color(contour, image):
    mask = np.zeros(image.shape, dtype='uint8')
    print(contour.shape)
    cv2.fillPoly(mask, contour.swapaxes(0, 1), [255, 255, 255])
    mask = mask & image
    cv2.imshow('w', mask)
    cv2.waitKey()


class MoveController:
    def __init__(self, kp=20, kd=25, ki=0):
        self.speed = 0.3
        self.pid_ld = 0
        self.kp, self.kd, self.ki = kp, kd, ki
        self.__state = 'waiting/connection'
        ...
        self.__state = 'waiting/move'
        ...
        self.__state = 'move/crossroad'
        self.__tmpdata = None

    def pid(self, err):
        p = self.kp * err
        d = self.kd * (self.pid_ld - err)
        i = self.ki
        self.pid_ld = err
        return p + i + d

    def get_state(self):
        return self.__state

    def new_info(self, info):
        self.__state = info

    def choose_action(self, env, camera):
        action = np.array([0, 0])
        if 'move' in self.__state:
            err_dir = env.get_lane_pos2(env.cur_pos, env.cur_angle).dist
            err_angle = env.get_lane_pos2(env.cur_pos, env.cur_angle).angle_rad
            if 'crossroad' in self.__state:
                mask_down = cv2.cvtColor(camera[camera.shape[0] - 100:,
                                         100:camera.shape[1] - 100, :], cv2.COLOR_RGB2HSV)
                cv2.imshow('hsv', np.append(np.append(mask_down[:, :, 0],
                                                      mask_down[:, :, 1], 0), mask_down[:, :, 2], 0))
                if (((10 > mask_down[:, :, 0]) | (mask_down[:, :, 0] > 165)) & (mask_down[:, :, 2] > 100)).sum() < 5000:
                    x = self.pid((err_dir-0.03) + err_angle/3)
                    action = np.array([self.speed - abs(x) / 30, x])
                else:
                    self.__state = 'waiting/move'
            elif 'turn' in self.__state:
                if 'left' in self.__state:

                    if self.__tmpdata is None:
                        self.__tmpdata = env.cur_angle + np.pi / 2
                        self.__tmpdata = self.__tmpdata if self.__tmpdata < np.pi else self.__tmpdata - np.pi * 2
                    print(abs(self.__tmpdata - env.cur_angle))
                    if abs(self.__tmpdata - env.cur_angle) > 0.05:
                        action = np.array([self.speed, 0.9])
                    else:
                        self.__state = 'waiting/move'
                elif 'right' in self.__state:
                    pass
        return action


def on_key_press(symbol, modifiers):
    if symbol == key.BACKSPACE or symbol == key.SLASH:
        print("RESET")
        env.reset()
        env.render()
    elif symbol == key.PAGEUP:
        env.unwrapped.cam_angle[0] = 0
    elif symbol == key.ESCAPE:
        env.close()
        sys.exit(0)


def update(dt):
    global obs, mover
    action = np.array([0, 0])
    if key_handler[key.UP]:
        action += np.array([3, 0])
    if key_handler[key.DOWN]:
        action -= np.array([3, 0])
    if key_handler[key.LEFT]:
        action += np.array([0, 6])
    if key_handler[key.RIGHT]:
        action += np.array([0, -6])

    #action = mover.choose_action(env, obs)

    cv2.circle(mask, (env.cur_pos[[0, 2]]*100).astype("int32"), 1, [1])
    mask_down_clear = obs[obs.shape[0] - 300:, :, :].copy()
    mask_down = cv2.morphologyEx(mask_down_clear.astype('float32'), cv2.MORPH_GRADIENT, np.ones([3, 3]))
    mask_down = ((mask_down[:, :, 0] + mask_down[:, :, 1] + mask_down[:, :, 2]) / 3).astype('uint8')
    _, mask_down = cv2.threshold(mask_down, 20, 255, cv2.THRESH_BINARY_INV)
    contours, hierarchy = cv2.findContours(mask_down.astype('uint8'), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    drawing = np.zeros((mask_down.shape[0], mask_down.shape[1], 3), dtype=np.uint8)
    for i in range(len(contours)):
        if 250 < cv2.contourArea(contours[i]) < 30000:
            approx = cv2.approxPolyDP(contours[i], 0.008 * cv2.arcLength(contours[i], True), True)
            if not (250 < cv2.contourArea(approx) < 30000):
                continue
            M = cv2.moments(contours[i])
            color_rgb = mask_down_clear[int(M["m01"] / M["m00"]), int(M["m10"] / M["m00"]), ::-1]
            color_hsv = cv2.cvtColor(np.array([[color_rgb]]), cv2.COLOR_RGB2HSV)[0][0]
            if color_hsv[2] > 70:
                cv2.drawContours(drawing, [approx], 0, tuple([int(i) for i in color_rgb]), 3)
    cv2.imshow('path', drawing)
    cv2.waitKey(1)
    obs, reward, done, info = env.step(action)

    if key_handler[key.SPACE]:
        mover.new_info('move/crossroad')
    if key_handler[key.Z]:
        mover.new_info('waiting/move')
    if key_handler[key.R]:
        env.reset()
    if key_handler[key.LEFT]:
        mover.new_info('move/turn/left')

    if done:
        print("done!")
        # env.reset()

    env.render()


env = DuckietownEnv()

env.reset()
obs = env.step(np.array([0, 0]))[0]
env.render()

mover = MoveController()

key_handler = key.KeyStateHandler()
env.unwrapped.window.push_handlers(key_handler)

pyglet.clock.schedule_interval(update, 0.05)

# Enter main event loop
pyglet.app.run()

env.close()
