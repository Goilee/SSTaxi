'''This script is for generating data
1. Provide desired path to store images.
2. Press 'c' to capture image and display it.
3. Press any button to continue.
4. Press 'q' to quit.
'''

import cv2
from cv2 import aruco
import numpy as np


def resize_with_aspect_ratio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]
    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))
    return cv2.resize(image, dim, interpolation=inter)


DISPLAY_IMG_HEIGHT = 700
dict_main_aruco = aruco.Dictionary_get(aruco.DICT_6X6_1000)
parameters = aruco.DetectorParameters_create()
camera = cv2.VideoCapture(1, apiPreference=cv2.CAP_ANY, params=[
    cv2.CAP_PROP_FRAME_WIDTH, 1920,
    cv2.CAP_PROP_FRAME_HEIGHT, 1080])


path = "/robotarium tasks/robot pos estimation/imgs/"
count = 0
while camera.isOpened():
    name = path + str(count)+".png"
    ret, img = camera.read()
    cv2.imshow("img", resize_with_aspect_ratio(img, height=DISPLAY_IMG_HEIGHT))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, dict_main_aruco, parameters=parameters)
    list_ids = np.ravel(ids)
    draw_frame = img.copy()
    if len(corners) > 0:
        for i in range(len(corners)):
            draw_frame = cv2.polylines(draw_frame, [corners[i].astype(int)], True, (0, 255, 0), 1)
            draw_frame = cv2.rectangle(draw_frame, corners[i][0][0].astype(int) - 3, corners[i][0][0].astype(int) + 3,
                                    (0, 0, 255), 1)
    cv2.imshow("tags", resize_with_aspect_ratio(draw_frame, height=DISPLAY_IMG_HEIGHT))
    
    q = cv2.waitKey(1)
    if q == ord('c'):
        cv2.imshow("tags", resize_with_aspect_ratio(draw_frame, height=DISPLAY_IMG_HEIGHT))
        conf = cv2.waitKey(0)
        if conf == ord("y"):
            cv2.imwrite(name, img)
            count += 1
    elif q == 27:
        break

camera.release()
cv2.destroyAllWindows()