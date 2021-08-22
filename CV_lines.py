import cv2
import numpy as np


def glue(mat):
    return np.append(np.append(mat[:, :, 0], mat[:, :, 1], 0), mat[:, :, 2], 0)


def get_ct_color(contour, image):
    mask = np.zeros([image.shape[0], image.shape[1]], dtype='uint8')
    cv2.fillPoly(mask, contour.reshape([1, contour.shape[0], 2]), 255)
    mask = image[np.where(mask)]
    return mask.mean(axis=0).astype('uint8')


def get_distances(ct):
    return np.sqrt((ct**2).sum(axis=2))


def something(obs):
    mask_down_clear = obs[obs.shape[0] - 300:obs.shape[0] - 50, :, :].copy()
    mask_down = cv2.morphologyEx(mask_down_clear.astype('float32'), cv2.MORPH_GRADIENT, np.ones([3, 3]))
    mask_down = ((mask_down[:, :, 0] + mask_down[:, :, 1] + mask_down[:, :, 2]) / 3).astype('uint8')
    _, mask_down = cv2.threshold(mask_down, 20, 255, cv2.THRESH_BINARY_INV)
    contours, hierarchy = cv2.findContours(mask_down.astype('uint8'), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    drawing = np.zeros((mask_down.shape[0] * 1, mask_down.shape[1], 3), dtype=np.uint8)
    yellows = []
    white_lines = []
    for i in range(len(contours)):
        if not (250 < cv2.contourArea(contours[i]) < 30000):
            continue
        approx = cv2.approxPolyDP(contours[i], 0.01 * cv2.arcLength(contours[i], True), True)
        if not (250 < cv2.contourArea(approx) < 30000):
            continue
        M = cv2.moments(contours[i])
        pos = [int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])]

        color_rgb = get_ct_color(approx, mask_down_clear)
        color_hsv = cv2.cvtColor(np.array([[color_rgb]]), cv2.COLOR_RGB2HSV)[0][0]
        if color_hsv[2] < 150:
            continue
        if (color_hsv[0] < 15 or color_hsv[0] > 165) and color_hsv[1] > 150:
            # RED !!!!!
            cv2.putText(drawing, "R", [pos[0], pos[1]], cv2.FONT_HERSHEY_PLAIN, 2, tuple([255, 255, 0]), thickness=4)
            pass
        else:
            dst = get_distances(approx)
            k = dst.max() / dst.min()
            _, radius = cv2.minEnclosingCircle(approx)
            if k > 0 and radius > 80:
                # WHITE !!!!!
                rows, cols = mask_down_clear.shape[:2]
                [vx, vy, x, y] = cv2.fitLine(approx, cv2.DIST_L2, 0, 0.01, 0.01)
                lefty = int((-x * vy / vx) + y)
                righty = int(((cols - x) * vy / vx) + y)
                cv2.line(drawing, (cols - 1, righty), (0, lefty), (255, 255, 255), 2)
                white_lines.append(np.array([(cols - 1, righty), (0, lefty)]))
            else:
                # YELLOW
                yellows.append(np.array(pos))
                cv2.circle(drawing, pos, 4, [255, 0, 0], -1)
                cv2.putText(drawing, "Y", [pos[0], pos[1]], cv2.FONT_HERSHEY_PLAIN, 1, tuple([255, 255, 0]))
        cv2.drawContours(drawing, [approx], 0, tuple([int(i) for i in color_rgb[::-1]]), 3)
    for i in range(len(yellows)-1, -1, -1):
        for line in white_lines:
            if np.linalg.norm(np.cross(line[1] - line[0], line[0] - yellows[i])) /\
                    np.linalg.norm(line[1] - line[0]) < 100:
                yellows.pop(i)
                break
    if len(yellows) > 1:
        yellows = np.array(yellows).swapaxes(0, 1)
        f = np.poly1d(np.polyfit(yellows[0], yellows[1], 1))
        cv2.line(drawing, (drawing.shape[1], int(f(drawing.shape[1]))), (0, int(f(0))), (0, 255, 255), 2)
    cv2.imshow('path', drawing)
    cv2.waitKey(1)