import cv2
import yaml
import numpy as np
from cv2 import aruco


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


root = "./"

calibrate_camera = False
calib_imgs_path = root + "imgs/"
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_1000)
markerLength = 3.75
markerSeparation = 0.5
DISPLAY_IMG_HEIGHT = 700
camera = cv2.VideoCapture(1, apiPreference=cv2.CAP_ANY, params=[
    cv2.CAP_PROP_FRAME_WIDTH, 1280,
    cv2.CAP_PROP_FRAME_HEIGHT, 720])
ret, img = camera.read()

with open('/robotarium tasks/robot pos estimation/calibration.yaml') as f:
    loadeddict = yaml.safe_load(f)
mtx = loadeddict.get('camera_matrix')
dist = loadeddict.get('dist_coeff')
mtx = np.array(mtx)
dist = np.array(dist)
# print(dist)

ret, img = camera.read()
img_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
h,  w = img_gray.shape[:2]
newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))

pose_r, pose_t = [], []
rvec = None
tvec = None
while True:
    ret, img = camera.read()
    img_aruco = img
    im_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    h, w = im_gray.shape[:2]
    dst = cv2.undistort(im_gray, mtx, dist, None, newcameramtx)
    # cv2.imshow("undistorted", dst)
    corners, ids, rejectedImgPoints = aruco.detectMarkers(im_gray, aruco_dict, parameters=arucoParams)
    #cv2.imshow("original", img_gray)
    if len(corners) == 0:
        pass
        # print("pass")
    else:
        img_aruco = aruco.drawDetectedMarkers(img, corners, ids, (0,255,0))
        for i in range(len(ids)):
            rvec, tvec, markerPoints = aruco.estimatePoseSingleMarkers(corners, markerLength, newcameramtx, dist) # For a board
            # print("Rotation ", rvec, "Translation", tvec)
            # if ret != 0:
            img_aruco = cv2.drawFrameAxes(img_aruco, newcameramtx, dist, rvec, tvec, 5)    # axis length 100 can be changed according to your requirement
    q = cv2.waitKey(1)
    if q == 27:
        break
    cv2.imshow("World co-ordinate frame axes", resize_with_aspect_ratio(img_aruco, height=DISPLAY_IMG_HEIGHT))

cv2.destroyAllWindows()