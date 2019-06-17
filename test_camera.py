
import time
import numpy as np
import basler_cam as camera
import preprocessor_functions as preprocessor
import cv2

# Image capture
cam = camera.Camera()
time.sleep(2)
pre = preprocessor.preprocessor(28)
cv2.namedWindow('title', cv2.WINDOW_NORMAL)

while True:
    start = time.time()
    image = cam.getImage()
    success, frame, rect = pre.locateSquare(image)
    if success:
        box_pts = np.int0(cv2.boxPoints(rect))
        cv2.drawContours(image,[box_pts],0,(255,0,0),3)
    cv2.imshow('title', image)
    cv2.waitKey(1)
