# from PIL import Image
# import argparse
# import sys
# import gym
import numpy as np
import cv2
# import cv2.aruco as aruco
# from TCP.TCPClient import ClientSocket
# import random as rng

#cli_sock = ClientSocket(25565, 'hello server', '192.168.189.74')

mask = np.zeros([400, 400, 1], dtype='float32')

"""
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
"""

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
        self.__state = 'connection'
        ...
        self.__state = 'waiting'
        ...
        #self.__state = 'move/crossroad'
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
        # print('NEW INFO')
        self.__state = info

    def choose_action(self, env, camera, aruco_id):
        action = np.array([0, 0])
        # print(self.__state)
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
                    if 'move_in' in self.__state and 'waiting' in self.__state:
                        mask_down = cv2.cvtColor(camera[camera.shape[0] - 100:,
                                                 100:camera.shape[1] - 100, :], cv2.COLOR_RGB2HSV)
                        cv2.imshow('hsv', np.append(np.append(mask_down[:, :, 0],
                                                              mask_down[:, :, 1], 0), mask_down[:, :, 2], 0))
                        if (((10 > mask_down[:, :, 0]) | (mask_down[:, :, 0] > 165)) & (
                                mask_down[:, :, 2] > 100)).sum() < 5000:
                            x = self.pid((err_dir - 0.03) + err_angle / 3)
                            action = np.array([self.speed - abs(x) / 30, x])
                    else:
                        self.__state = 'waiting/send'
                        print('send', aruco_id)
                    # cli_sock.sendSTR(str(aruco_id))
                    # cli_sock.sendPos([int(env.cur_angle)])
            elif 'turn' in self.__state:
                if 'left' in self.__state:

                    if self.__tmpdata is None:
                        self.__tmpdata = env.cur_angle + np.pi / 2
                        self.__tmpdata = self.__tmpdata if self.__tmpdata < np.pi else self.__tmpdata - np.pi * 2
                    print(abs(self.__tmpdata - env.cur_angle))
                    if abs(self.__tmpdata - env.cur_angle) > 0.05:
                        action = np.array([self.speed, 0.9])
                    else:
                        self.__state = 'waiting'
                elif 'right' in self.__state:
                    pass
        return action

"""
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

    img = cv2.cvtColor(obs, cv2.COLOR_BGR2RGB)
    # cv2.imshow("original", img)
    aruco_img = img.copy()
    aruco_marks = findArucoMarkers(aruco_img, draw=False)
    # loop through all the markers and augment each one
    aruco_idx = 0
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
            if max_width > 30 and max_height > 30:
                #print("ok")
                cv2.line(aruco_img, (int(bbox[0][0][0]), int(bbox[0][0][1])),
                         (int(bbox[0][1][0]), int(bbox[0][1][1])),
                         (255, 0, 0), 2)

                cv2.line(aruco_img, (int(bbox[0][1][0]), int(bbox[0][1][1])),
                         (int(bbox[0][2][0]), int(bbox[0][2][1])),
                         (255, 0, 0), 2)

                cv2.line(aruco_img, (int(bbox[0][2][0]), int(bbox[0][2][1])),
                         (int(bbox[0][3][0]), int(bbox[0][3][1])),
                         (255, 0, 0), 2)

                cv2.line(aruco_img, (int(bbox[0][3][0]), int(bbox[0][3][1])),
                         (int(bbox[0][0][0]), int(bbox[0][0][1])),
                         (255, 0, 0), 2)
                #print(id[0], [int(env.cur_angle)])
                aruco_idx = id[0]
    cv2.imshow('aruco img', aruco_img)

    action = mover.choose_action(env, obs, aruco_idx)

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
    ines_img = drawing.copy()
    lines = cv2.HoughLines(mask_down, 4, np.pi / 180, 200)
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
            cv2.line(lines_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.imshow("lines", lines_img)
    #cv2.waitKey(1)
    obs, reward, done, info = env.step(action)

    if key_handler[key.SPACE]:
        mover.new_info('move/crossroad')
        key_handler[key.SPACE] = False
    if key_handler[key.Z]:
        mover.new_info('waiting')
    if key_handler[key.R]:
        env.reset()
    if key_handler[key.LEFT]:
        mover.new_info('move/turn/left')

    if done:
        print("done!")
        # env.reset()

    env.render()


env = DuckietownEnv(map_name="map_test")

env.reset()
obs = env.step(np.array([0, 0]))[0]
env.render()

mover = MoveController()

key_handler = key.KeyStateHandler()
env.unwrapped.window.push_handlers(key_handler)

pyglet.clock.schedule_interval(update, 0.05)

# Enter main event loop
pyglet.app.run()

env.close()"""