import numpy as np
import cv2

ACTION_STOP = 'stop'
ACTION_MOVE_TO_CR = 'crossroad'
ACTION_MOVE_RIGHT = 'right'
ACTION_MOVE_LEFT = 'left'
ACTION_MOVE_TURNOVER = 'turnover'

class MoveController:
    def __init__(self, kp=20, kd=25):
        self.speed = 0.3
        self.pid_ld = 0
        self.kp, self.kd, self.ki = kp, kd, 0
        self.__state = ACTION_STOP
        self.__tmpdata = None
        self.see_red = False
        self.__tflu = 0

    def pid(self, err):
        p = self.kp * err
        d = self.kd * (self.pid_ld - err)
        i = self.ki
        self.pid_ld = err
        return p + i + d

    def get_action(self):
        return self.__state

    def new_action(self, info):
        self.__state = info

    def get_move_values(self, env, camera, dt):
        action = np.array([0, 0])
        err_dir = env.get_lane_pos2(env.cur_pos, env.cur_angle).dist
        err_angle = env.get_lane_pos2(env.cur_pos, env.cur_angle).angle_rad
        mask_down = cv2.cvtColor(camera[camera.shape[0] - 100:,
                                 100:camera.shape[1] - 100, :], cv2.COLOR_RGB2HSV)
        self.see_red = (((10 > mask_down[:, :, 0]) | (mask_down[:, :, 0] > 165)) &
                        (mask_down[:, :, 2] > 100)).sum() > 5000
        if self.__state == ACTION_MOVE_TO_CR:
            if (not self.see_red) or self.__tflu < 1:
                x = self.pid((err_dir-0.03) + err_angle/3)
                action = np.array([self.speed - abs(x) / 30, x])
            else:
                self.__tmpdata = None
                self.__state = ACTION_STOP
        elif ACTION_MOVE_LEFT == self.__state:
            if self.__tmpdata is None:
                self.__tmpdata = env.cur_angle + np.pi / 2
                self.__tmpdata = self.__tmpdata if self.__tmpdata < np.pi else self.__tmpdata - np.pi * 2
            if abs(self.__tmpdata - env.cur_angle) > 0.07:
                action = np.array([self.speed, 0.9])
            else:
                self.__tmpdata = None
                self.__state = ACTION_STOP
        elif ACTION_MOVE_RIGHT == self.__state:
            if self.__tmpdata is None:
                self.__tmpdata = env.cur_angle - np.pi / 2
                self.__tmpdata = self.__tmpdata if self.__tmpdata > -np.pi else self.__tmpdata + np.pi * 2
            if abs(self.__tmpdata - env.cur_angle) > 0.07:
                action = np.array([self.speed, -1.8])
            else:
                self.__tmpdata = None
                self.__state = ACTION_STOP
        elif ACTION_MOVE_TURNOVER == self.__state:
            if self.__tmpdata is None:
                self.__tmpdata = env.cur_angle + 2.5
                self.__tmpdata = self.__tmpdata if self.__tmpdata < np.pi else self.__tmpdata - np.pi * 2
            if abs(self.__tmpdata - env.cur_angle) > 0.07:
                action = np.array([self.speed, 3.5])
            else:
                self.__tmpdata = None
                self.__state = ACTION_STOP

        if self.__state == ACTION_STOP:
            self.__tflu = 0
        else:
            self.__tflu += dt

        return action