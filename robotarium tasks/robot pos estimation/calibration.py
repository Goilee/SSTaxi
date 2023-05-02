import cv2
from cv2 import aruco
import yaml
import numpy as np
from pathlib import Path
from tqdm import tqdm
from glob import glob


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


# root directory of repo for relative path specification.
root = "./"

# Set path to the images
calib_imgs_path = root + "imgs/"

# For validating results, show aruco board to camera.
aruco_dict = aruco.getPredefinedDictionary( aruco.DICT_6X6_1000 )

#Provide length of the marker's side
markerLength = 3.75  # Here, measurement unit is centimetre.

# Provide separation between markers
markerSeparation = 0.5   # Here, measurement unit is centimetre.

# create arUco board
board = aruco.GridBoard_create(4, 5, markerLength, markerSeparation, aruco_dict)

'''uncomment following block to draw and show the board'''
# img = board.draw((1500,1500))
# cv2.imshow("aruco", img)
# cv2.imwrite("C:/Users/serg4/Downloads/qr code orientation test/cb.png", img)
# import sys
# sys.exit(0)

arucoParams = aruco.DetectorParameters_create()

img_list = []
calib_fnms = glob(calib_imgs_path + "*.png")
print('Using ...', end='')
for idx, fn in enumerate(calib_fnms):
    print(idx, '', end='')
    img = cv2.imread(fn)
    img_list.append( img )
    h, w, c = img.shape
print('Calibration images')

counter, corners_list, id_list = [], [], []
first = True
for im in tqdm(img_list):
    img_gray = cv2.cvtColor(im,cv2.COLOR_RGB2GRAY)
    corners, ids, rejectedImgPoints = aruco.detectMarkers(img_gray, aruco_dict, parameters=arucoParams)
    if first == True:
        corners_list = corners
        id_list = ids
        first = False
    else:
        corners_list = np.vstack((corners_list, corners))
        id_list = np.vstack((id_list,ids))
    counter.append(len(ids))
print('Found {} unique markers'.format(np.unique(ids)))

counter = np.array(counter)
print ("Calibrating camera .... Please wait...")
ret, mtx, dist, rvecs, tvecs = aruco.calibrateCameraAruco(corners_list, id_list, counter, board, img_gray.shape, None, None )

print("Camera matrix is \n", mtx, "\n And is stored in calibration.yaml file along with distortion coefficients : \n", dist)
data = {'camera_matrix': np.asarray(mtx).tolist(), 'dist_coeff': np.asarray(dist).tolist()}
with open("/robotarium tasks/robot pos estimation/calibration.yaml", "w") as f:
    yaml.dump(data, f)
