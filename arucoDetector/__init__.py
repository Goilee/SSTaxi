# !/usr/bin/env python
import cv2
import cv2.aruco as aruco


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
    if ret_id is None:
        ret_id = [255]
    return ret_id
