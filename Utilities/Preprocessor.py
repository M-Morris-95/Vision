# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 10:53:41 2019

@author: Michael Morris
preprocessing functions
"""
import cv2
import numpy as np

def rot_crop(image, pts, box, x, y):
    width = int(pts[1][0])
    height = int(pts[1][1])
    src_pts = box.astype("float32")
    dst_pts = np.array([[0, height - 1],
                        [0, 0],
                        [width - 1, 0],
                        [width - 1, height - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    out = cv2.warpPerspective(image, M, (width, height))
    out = cv2.resize(out, (x, y))
    return out

def preprocess(frame):
    ## convert to HSV
    size = 28
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    ## mask of red
    # lower mask
    lower = np.array([0, 100, 100])
    upper = np.array([10, 255, 255])
    lower_red = cv2.inRange(hsv, lower, upper)

    ##upper mask
    lower = np.array([160, 100, 100])
    upper = np.array([180, 255, 255])
    upper_red = cv2.inRange(hsv, lower, upper)

    hsv_mask = cv2.add(lower_red, upper_red)

    _, contours, hierachy = cv2.findContours(hsv_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[0:4]
    flag = 0
    for cnt in contours:
        rect = cv2.minAreaRect(cnt)
        # abs((rect[1][0]/rect[1][1])-1)<0.15 and
        if min(rect[1]) > 10:
            box_pts = np.int0(cv2.boxPoints(rect))
            cv2.drawContours(frame, [box_pts], -1, (0, 255, 0), 2)
            image = rot_crop(frame, rect, box_pts, size, size)
            flag = 1
            break

    if flag:
        return image
    return np.zeros([size, size, 3])