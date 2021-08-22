import cv2
import cv2.aruco as aruco

if __name__ == '__main__':
    print("starting env")
    # !/usr/bin/env python

    import copy
    import math
    from datetime import datetime
    import random

    from PIL import Image
    import sys

    import gym
    import numpy as np
    import pyglet
    from pyglet.window import key

    # import navigator
    # from TCP.TCPClient import ClientSocket
    # import glob

    from gym_duckietown.envs import DuckietownEnv

    _env = DuckietownEnv(map_name="map_test")
    # cli_sock = ClientSocket(1000, 'hello server')
    # env = gym.make("Duckietown-udem1-v0")

    _env.reset()
    _env.render()

    # graph = navigator.Graph("duckietown map graph exemple.json")
    # navi = navigator.Navi(graph)

    _max_dataset_count = 1005
    _max_num = 0
    _counter = 0
    _dataset_done = False


    @_env.unwrapped.window.event
    def on_key_press(_symbol, _modifiers):
        global _prev_delta
        """
        This handler processes keyboard commands that
        control the simulation
        """

        if _symbol == key.BACKSPACE or _symbol == key.SLASH:
            print("RESET")
            _prev_delta = 0
            _env.reset()
            _env.render()
        elif _symbol == key.PAGEUP:
            _env.unwrapped.cam_angle[0] = 0
        elif _symbol == key.ESCAPE:
            _env.close()
            sys.exit(0)
        elif _symbol == key.RETURN:
            print('saving screenshot')
            _img = _env.render('rgb_array')
            _img = cv2.cvtColor(_img, cv2.COLOR_BGR2HSV)
            cv2.imwrite('screenshot ' + str(datetime.now().minute) + " " + str(datetime.now().second) + '.jpg', _img)


    # Register a keyboard handler
    _key_handler = key.KeyStateHandler()
    _env.unwrapped.window.push_handlers(_key_handler)

    _observ = np.uint8(np.zeros((480, 640, 3)))


    def update(dt):
        global _counter, _prev_step, _observ, _flag, _dataset_done
        _wheel_distance = 0.102
        _min_rad = 0.08

        _action = np.array([0.0, 0.0])

        if _key_handler[key.UP]:
            _action += np.array([0.44, 0.0])
        if _key_handler[key.DOWN]:
            _action -= np.array([0.44, 0])
        if _key_handler[key.LEFT]:
            _action += np.array([0, 1])
        if _key_handler[key.RIGHT]:
            _action -= np.array([0, 1])
        if _key_handler[key.SPACE]:
            _action = np.array([0, 0])
        _v1 = _action[0]
        _v2 = _action[1]
        # Limit radius of curvature
        if _v1 == 0 or abs(_v2 / _v1) > (_min_rad + _wheel_distance / 2.0) / (_min_rad - _wheel_distance / 2.0):
            # adjust velocities evenly such that condition is fulfilled
            _delta_v = (_v2 - _v1) / 2 - _wheel_distance / (4 * _min_rad) * (_v1 + _v2)
            _v1 += _delta_v
            _v2 -= _delta_v

        _action[0] = _v1
        _action[1] = _v2

        # Speed boost
        if _key_handler[key.LSHIFT]:
            _action *= 1.5

        # print(round(env.cur_pos[0], 2), round(env.cur_pos[2], 2))
        # print("step_count = %s, reward=%.3f" % (env.unwrapped.step_count, reward))
        _img = cv2.cvtColor(_observ, cv2.COLOR_BGR2RGB)
        # cv2.imshow("original", img)
        _aruco_img = _img.copy()
        _markerSize = 6
        _totalMarkers = 250
        _gray = cv2.cvtColor(_aruco_img, cv2.COLOR_BGR2GRAY)
        key = getattr(aruco, f'DICT_{_markerSize}X{_markerSize}_{_totalMarkers}')
        _aruco_dict = aruco.Dictionary_get(key)
        _aruco_param = aruco.DetectorParameters_create()
        _bboxs, ids, rejected = aruco.detectMarkers(_gray, _aruco_dict, parameters=_aruco_param)
        # print(ids)
        aruco.drawDetectedMarkers(_aruco_img, _bboxs)
        _aruco_marks = _bboxs
        # _aruco_marks = findArucoMarkers(_aruco_img, draw=False)
        # loop through all the markers and augment each one
        if len(_aruco_marks[0]) != 0:
            for bbox, id in zip(_aruco_marks[0], _aruco_marks[1]):
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
                    cv2.line(_aruco_img, (int(bbox[0][0][0]), int(bbox[0][0][1])),
                             (int(bbox[0][1][0]), int(bbox[0][1][1])),
                             (255, 0, 0), 2)

                    cv2.line(_aruco_img, (int(bbox[0][1][0]), int(bbox[0][1][1])),
                             (int(bbox[0][2][0]), int(bbox[0][2][1])),
                             (255, 0, 0), 2)

                    cv2.line(_aruco_img, (int(bbox[0][2][0]), int(bbox[0][2][1])),
                             (int(bbox[0][3][0]), int(bbox[0][3][1])),
                             (255, 0, 0), 2)

                    cv2.line(_aruco_img, (int(bbox[0][3][0]), int(bbox[0][3][1])),
                             (int(bbox[0][0][0]), int(bbox[0][0][1])),
                             (255, 0, 0), 2)
                    print(id, max_width, max_height)
        cv2.imshow('aruco img', _aruco_img)

        # if key_handler[key.F]:
        #     action = pd_driver(observ, env.unwrapped)
        _observ, reward, done, info = _env.step(_action)

        # white_mask = cv2.inRange(cutted_image, (10, 29, 77), (101, 84, 171))
        # cv2.imshow("white mask", white_mask)

        if _key_handler[key.RETURN]:
            im = Image.fromarray(_observ)
            im.save("pic.png")

        if done:
            print("done!")
            _flag = 0
            _env.reset()
            _env.render()

        """if counter // 20 > max_dataset_count:
            dataset_done = True

        if dataset_done:
            print("dataset is done!")
            env.close()
            sys.exit(0)"""

        _env.render()


    pyglet.clock.schedule_interval(update, 1.0 / _env.unwrapped.frame_rate)

    # Enter main event loop
    pyglet.app.run()

    _env.close()
else:
    pass


def find_aruco_markers(img, markerSize=6, totalMarkers=250, draw=True):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    key = getattr(aruco, f'DICT_{markerSize}X{markerSize}_{totalMarkers}')
    aruco_dict = aruco.Dictionary_get(key)
    aruco_param = aruco.DetectorParameters_create()
    bboxs, ids, rejected = aruco.detectMarkers(gray, aruco_dict, parameters=aruco_param)
    # print(ids)
    if draw:
        aruco.drawDetectedMarkers(img, bboxs)
    return [bboxs, ids]


def filter_bboxs(aruco_marks, aruco_img, drawing=True, debug=False):
    ret_id = None
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
                cv2.line(aruco_img, (int(bbox[0][0][0]), int(bbox[0][0][1])), (int(bbox[0][1][0]), int(bbox[0][1][1])),
                         (255, 0, 0), 2)

                cv2.line(aruco_img, (int(bbox[0][1][0]), int(bbox[0][1][1])), (int(bbox[0][2][0]), int(bbox[0][2][1])),
                         (255, 0, 0), 2)

                cv2.line(aruco_img, (int(bbox[0][2][0]), int(bbox[0][2][1])), (int(bbox[0][3][0]), int(bbox[0][3][1])),
                         (255, 0, 0), 2)

                cv2.line(aruco_img, (int(bbox[0][3][0]), int(bbox[0][3][1])), (int(bbox[0][0][0]), int(bbox[0][0][1])),
                         (255, 0, 0), 2)
                if debug:
                    print("filtered", id, max_width, max_height)
                ret_id = id
    if drawing:
        cv2.imshow('aruco img', aruco_img)
    return ret_id
