#!/usr/bin/env python

import copy
import math
from datetime import datetime
import random

import cv2
from PIL import Image
import sys

import gym
import numpy as np
import pyglet
from pyglet.window import key

# import navigator
#from TCP.TCPClient import ClientSocket
# import glob

from gym_duckietown.envs import DuckietownEnv
import cv2.aruco as aruco

env = DuckietownEnv(map_name="map_test")
#cli_sock = ClientSocket(1000, 'hello server')
# env = gym.make("Duckietown-udem1-v0")

env.reset()
env.render()

#graph = navigator.Graph("duckietown map graph exemple.json")
#navi = navigator.Navi(graph)

max_dataset_count = 1005
max_num = 0
_counter = 0
_dataset_done = False


def findArucoMarkers(img, markerSize=6, totalMarkers=250, draw=True):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    key = getattr(aruco, f'DICT_{markerSize}X{markerSize}_{totalMarkers}')
    aruco_dict = aruco.Dictionary_get(key)
    aruco_param = aruco.DetectorParameters_create()
    bboxs, ids, rejected = aruco.detectMarkers(gray, aruco_dict, parameters=aruco_param)
    # print(ids)
    if draw:
        aruco.drawDetectedMarkers(img, bboxs)
    return [bboxs, ids]


@env.unwrapped.window.event
def on_key_press(symbol, modifiers):
    global _prev_delta
    """
    This handler processes keyboard commands that
    control the simulation
    """

    if symbol == key.BACKSPACE or symbol == key.SLASH:
        print("RESET")
        prev_delta = 0
        env.reset()
        env.render()
    elif symbol == key.PAGEUP:
        env.unwrapped.cam_angle[0] = 0
    elif symbol == key.ESCAPE:
        env.close()
        sys.exit(0)
    elif symbol == key.RETURN:
        print('saving screenshot')
        img = env.render('rgb_array')
        img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        cv2.imwrite('screenshot ' + str(datetime.now().minute) + " " + str(datetime.now().second) + '.jpg', img)


# Register a keyboard handler
key_handler = key.KeyStateHandler()
env.unwrapped.window.push_handlers(key_handler)

_prev_delta = 0
_prev_step = 0
_flag = 0
next_move = "forward"
edge_line_flag = 0

"""
def pd_driver(obs, unwrapped_env):
    global prev_delta, prev_step, flag, next_move, edge_line_flag
    wheel_distance = 0.102
    min_rad = 0.08

    action = np.array([0.0, 0.0])

    v1 = action[0]
    v2 = action[1]
    # Limit radius of curvature
    if v1 == 0 or abs(v2 / v1) > (min_rad + wheel_distance / 2.0) / (min_rad - wheel_distance / 2.0):
        # adjust velocities evenly such that condition is fulfilled
        delta_v = (v2 - v1) / 2 - wheel_distance / (4 * min_rad) * (v1 + v2)
        v1 += delta_v
        v2 -= delta_v

    action[0] = v1
    action[1] = v2

    # Speed boost
    if key_handler[key.LSHIFT]:
        action *= 1.5

    img_right = cv2.cvtColor(obs, cv2.COLOR_BGR2RGB)
    img_left = copy.deepcopy(img_right)
    img_right = img_right[250:, 300:, :]
    img_left = img_left[160:300, :340, :]

    mask = cv2.inRange(img_right, (22, 75, 82), (255, 255, 255))
    cv2.imshow("mask", mask)
    left_mask = cv2.inRange(img_left, (20, 20, 70), (50, 50, 170))
    cv2.imshow("left mask", left_mask)
    red_mask = cv2.inRange(img_right, (20, 20, 70), (50, 50, 170))
    cv2.imshow("red mask", red_mask)

    edges = cv2.Canny(mask, 50, 150, apertureSize=5)
    cv2.imshow("edges", edges)
    lines = cv2.HoughLines(edges, 4, np.pi / 180, 200)
    lines_img = copy.deepcopy(img_right)
    edge_line_img = copy.deepcopy(img_right)
    edge_line = []

    edges = cv2.Canny(red_mask, 50, 150, apertureSize=5)
    cv2.imshow("red edges", edges)
    red_lines = cv2.HoughLines(edges, 4, np.pi / 180, 200)
    red_lines_img = copy.deepcopy(img_right)
    red_edge_line_img = copy.deepcopy(img_right)
    red_edge_line = []

    edges = cv2.Canny(left_mask, 50, 150, apertureSize=5)
    cv2.imshow("left edges", edges)
    left_lines = cv2.HoughLines(edges, 4, np.pi / 180, 200)
    left_lines_img = copy.deepcopy(img_left)
    left_edge_line_img = copy.deepcopy(img_left)
    left_edge_line = []

    if lines is not None:
        for line in range(len(lines)):
            rho, theta = lines[line][0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * a)
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * a)
            if line == 0:
                cv2.line(edge_line_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                edge_line.append([(x1, y1), (x2, y2)])
            # elif line == len(lines) - 1:
            #    cv2.line(edge_line_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            #    edge_line.append([(x1, y1), (x2, y2)])
            lines_img = cv2.line(lines_img, (x1, y1), (x2, y2), (0, 255, 0), 2)

    if red_lines is not None:
        for line in range(len(red_lines)):
            rho, theta = red_lines[line][0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * a)
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * a)
            if line == 0:
                cv2.line(red_edge_line_img, (x1, y1), (x2, y2), (255, 0, 0), 2)
                red_edge_line.append([(x1, y1), (x2, y2)])
            # elif line == len(lines) - 1:
            #    cv2.line(edge_line_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            #    edge_line.append([(x1, y1), (x2, y2)])
            red_lines_img = cv2.line(red_lines_img, (x1, y1), (x2, y2), (255, 0, 0), 2)

    if left_lines is not None:
        for line in range(len(left_lines)):
            rho, theta = left_lines[line][0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * a)
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * a)
            if line == 0:
                cv2.line(left_edge_line_img, (x1, y1), (x2, y2), (255, 0, 0), 2)
                left_edge_line.append([(x1, y1), (x2, y2)])
            # elif line == len(lines) - 1:
            #    cv2.line(edge_line_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            #    edge_line.append([(x1, y1), (x2, y2)])
            left_lines_img = cv2.line(left_lines_img, (x1, y1), (x2, y2), (255, 0, 0), 2)

    sample_lines = [(340, 200), (165, 0)]
    red_sample_lines = [(0, 115), (340, 115)]
    left_sample_lines = [(0, 115), (340, 115)]
    cv2.line(edge_line_img, sample_lines[0], sample_lines[1], (0, 0, 255), 2)
    cv2.line(red_edge_line_img, red_sample_lines[0], red_sample_lines[1], (0, 255, 255), 2)
    cv2.line(left_edge_line_img, left_sample_lines[0], left_sample_lines[1], (0, 255, 255), 2)
    # cv2.line(edge_line_img, sample_lines[1][0], sample_lines[1][1], (0, 0, 255), 2)
    cv2.imshow("edge lines", edge_line_img)
    cv2.imshow("all lines", lines_img)
    cv2.imshow("red edge lines", red_edge_line_img)
    cv2.imshow("red all lines", red_lines_img)
    cv2.imshow("left edge lines", left_edge_line_img)
    cv2.imshow("left all lines", left_lines_img)

    delta = 0
    k = 0.015
    if edge_line:
        ex1 = sample_lines[0][0] - edge_line[0][0][0]
        ex2 = sample_lines[1][0] - edge_line[0][1][0]
        ey1 = sample_lines[0][1] - edge_line[0][0][1]
        ey2 = sample_lines[1][1] - edge_line[0][1][1]

        delta = ((ex1 + ex2) - (ey1 + ey2))
    else:
        delta = -180

    if red_edge_line and not flag:
        rex1 = red_sample_lines[0][0] - (1000 + red_edge_line[0][0][0])
        rex2 = red_sample_lines[1][0] - (1340 - red_edge_line[0][1][0])
        rey1 = red_sample_lines[0][1] - red_edge_line[0][0][1]
        rey2 = red_sample_lines[1][1] - red_edge_line[0][1][1]
        # print(rex1, rex2, rey1, rey2)
        # print(red_edge_line[0][0][0], red_edge_line[0][1][0], red_edge_line[0][0][1], red_edge_line[0][1][1])
        if -75 < rex1 < 75 and -75 < rex2 < 75 and -75 < rey1 < 75 and -75 < rey2 < 75:
            flag = 1
            next_move = "error"
            while next_move == "error":
                x, y = round(unwrapped_env.cur_pos[0], 2), round(unwrapped_env.cur_pos[2], 2)
                angle = round(unwrapped_env.cur_angle * 57)
                print(x, y, angle)
                now_id = graph.get_point_id(x, y, angle)
                print(now_id)
                neighbours = graph.get_neighbours_id(now_id)
                print(neighbours)
                chosen_neighbour = random.choice(neighbours)
                print(chosen_neighbour)
                direction = navi.get_direction_from_point(now_id, chosen_neighbour, angle)
                print(direction)
                next_move = direction
            prev_step = unwrapped_env.step_count
    # print(flag)
    if flag:
        if next_move == "forward":
            if left_edge_line:
                rex1 = left_sample_lines[0][0] - (1000 + left_edge_line[0][0][0])
                rex2 = left_sample_lines[1][0] - (1340 - left_edge_line[0][1][0])
                rey1 = left_sample_lines[0][1] - left_edge_line[0][0][1]
                rey2 = left_sample_lines[1][1] - left_edge_line[0][1][1]
                # print(rex1, rex2, rey1, rey2)
                if -50 < rex1 < 50 and -50 < rex2 < 50 and -50 < rey1 < 50 and -50 < rey2 < 50:
                    flag = 0
        else:
            if edge_line and edge_line_flag == 1:
                prev_step = unwrapped_env.step_count
                flag = 0
                edge_line_flag = 0
                print("ok")
            elif not edge_line:
                if unwrapped_env.step_count - prev_step > 50:
                    edge_line_flag = 1
            print(edge_line_flag, len(edge_line))
    elif prev_step != 0:
        if unwrapped_env.step_count - prev_step > 70:
            prev_step = 0
            flag = 0

        # lane_pose = env.get_lane_pos2(env.cur_pos, env.cur_angle)
        # angle_from_straight_in_rads = lane_pose.angle_rad
        # kd = 1
    p = 0.5
    if flag:
        if next_move == "left":
            delta = 80
        # elif next_move == "right":
        #    delta = -140
        elif next_move == "forward":
            delta = 0

    delta = delta * k
    # delta_d = kd * (prev_delta - (0 - angle_from_straight_in_rads))
    # delta_d = kd * (prev_delta - delta)
    # delta += delta_d
    # kp = 0.1
    # p += kp * delta_d
    action += np.array([p, delta])
    # prev_delta = delta
    # print(delta)
    return action"""


_observ = np.uint8(np.zeros((480, 640, 3)))


def update(dt):
    global _counter, _prev_step, _observ, _flag, _dataset_done
    wheel_distance = 0.102
    min_rad = 0.08

    action = np.array([0.0, 0.0])

    if key_handler[key.UP]:
        action += np.array([0.44, 0.0])
    if key_handler[key.DOWN]:
        action -= np.array([0.44, 0])
    if key_handler[key.LEFT]:
        action += np.array([0, 1])
    if key_handler[key.RIGHT]:
        action -= np.array([0, 1])
    if key_handler[key.SPACE]:
        action = np.array([0, 0])
    v1 = action[0]
    v2 = action[1]
    # Limit radius of curvature
    if v1 == 0 or abs(v2 / v1) > (min_rad + wheel_distance / 2.0) / (min_rad - wheel_distance / 2.0):
        # adjust velocities evenly such that condition is fulfilled
        delta_v = (v2 - v1) / 2 - wheel_distance / (4 * min_rad) * (v1 + v2)
        v1 += delta_v
        v2 -= delta_v

    action[0] = v1
    action[1] = v2

    # Speed boost
    if key_handler[key.LSHIFT]:
        action *= 1.5

    # print(round(env.cur_pos[0], 2), round(env.cur_pos[2], 2))
    # print("step_count = %s, reward=%.3f" % (env.unwrapped.step_count, reward))
    img = cv2.cvtColor(observ, cv2.COLOR_BGR2RGB)
    # cv2.imshow("original", img)
    aruco_img = img.copy()
    aruco_marks = findArucoMarkers(aruco_img, draw=False)
    # loop through all the markers and augment each one
    if len(aruco_marks[0]) != 0:
        for bbox, id in zip(aruco_marks[0], aruco_marks[1]):
            max_width = 0
            max_height = 0
            for i in range(1, len(bbox[0]), 2):
                if max_width < bbox[0][i][0] - bbox[0][i - 1][0]:
                    max_width = bbox[0][i][0] - bbox[0][i - 1][0]

            for i in range(2, len(bbox[0]), 2):
                if max_height < bbox[0][i][1] - bbox[0][i - 1][1]:
                    max_height = bbox[0][i][1] - bbox[0][i - 1][1]

            # print(bbox[0], max_width, max_height)
            distortion_k = abs(max_height - max_width)
            if max_width > 20 and max_height > 20 and distortion_k < 15:
                print("ok")
                cv2.line(aruco_img, (int(bbox[0][0][0]), int(bbox[0][0][1])), (int(bbox[0][1][0]), int(bbox[0][1][1])),
                         (255, 0, 0), 2)

                cv2.line(aruco_img, (int(bbox[0][1][0]), int(bbox[0][1][1])), (int(bbox[0][2][0]), int(bbox[0][2][1])),
                         (255, 0, 0), 2)

                cv2.line(aruco_img, (int(bbox[0][2][0]), int(bbox[0][2][1])), (int(bbox[0][3][0]), int(bbox[0][3][1])),
                         (255, 0, 0), 2)

                cv2.line(aruco_img, (int(bbox[0][3][0]), int(bbox[0][3][1])), (int(bbox[0][0][0]), int(bbox[0][0][1])),
                         (255, 0, 0), 2)
                print(id, max_width, max_height)
    cv2.imshow('aruco img', aruco_img)

    # if key_handler[key.F]:
    #     action = pd_driver(observ, env.unwrapped)
    observ, reward, done, info = env.step(action)

    # white_mask = cv2.inRange(cutted_image, (10, 29, 77), (101, 84, 171))
    # cv2.imshow("white mask", white_mask)

    if key_handler[key.RETURN]:
        im = Image.fromarray(observ)
        im.save("pic.png")

    if done:
         print("done!")
         flag = 0
         env.reset()
         env.render()

    """if counter // 20 > max_dataset_count:
        dataset_done = True

    if dataset_done:
        print("dataset is done!")
        env.close()
        sys.exit(0)"""

    env.render()


pyglet.clock.schedule_interval(update, 1.0 / env.unwrapped.frame_rate)

# Enter main event loop
pyglet.app.run()

env.close()
