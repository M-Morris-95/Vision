# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 10:53:41 2019

@author: Michael Morris
preprocessing functions
"""

import cv2
import numpy as np

class preprocessor:
    def __init__(self, size):
        self._size = size

    def rot_crop(self, image, pts, box, x, y):
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

    def locateSquare(self, frame):
        # convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # mask for red
        # lower mask
        lower = np.array([0, 100, 100])
        upper = np.array([10, 255, 255])
        lower_red = cv2.inRange(hsv, lower, upper)

        # upper mask
        lower = np.array([160, 100, 100])
        upper = np.array([180, 255, 255])
        upper_red = cv2.inRange(hsv, lower, upper)

        hsv_mask = cv2.add(lower_red, upper_red)

        contours, hierachy = cv2.findContours(hsv_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[0:4]
        success = False
        counter = 0
        for cnt in contours:
            rect = cv2.minAreaRect(cnt)
            if min(rect[1]) > 15:
                if abs(rect[1][0]/rect[1][1]-1)<0.2:
                    box_pts = np.int0(cv2.boxPoints(rect))
                    image = self.rot_crop(frame, rect, box_pts, self._size, self._size)
                    success = True

                    return success, image, rect
        return success, None, None

    def locate4Squares(self, frame):
        # convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # mask for red
        # lower mask
        lower = np.array([0, 100, 100])
        upper = np.array([10, 255, 255])
        lower_red = cv2.inRange(hsv, lower, upper)

        # upper mask
        lower = np.array([160, 100, 100])
        upper = np.array([180, 255, 255])
        upper_red = cv2.inRange(hsv, lower, upper)

        hsv_mask = cv2.add(lower_red, upper_red)

        contours, hierachy = cv2.findContours(hsv_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[0:10]
        success = [False,False,False,False]

        image = np.zeros([4,28,28,3], np.uint8)
        box_pts = np.zeros(4,4,2)
        counter = 0
        for cnt in contours:
            rect = cv2.minAreaRect(cnt)
            if min(rect[1]) > 15:
                if abs(rect[1][0] / rect[1][1] - 1) < 0.2:
                    collision = False
                    for k in range(counter):
                        if self.check_collision(box_pts[k,:,:], np.int0(cv2.boxPoints(rect))):
                            collision = True
                    if not collision:
                        box_pts[counter, :, :] = np.int0(cv2.boxPoints(rect))
                        image[counter, :, :, :] = self.rot_crop(frame, rect, box_pts, self._size, self._size)
                        success[counter] = True
                        counter = counter+1

                    if counter == 4:
                        break
        return success, image, box_pts

    def check_collision(self, A, B):
        if min(A[:, 1]) <= max(B[:, 1]):
            return False
        if max(A[:, 1]) >= min(B[:, 1]):
            return False
        if max(A[:, 0]) <= min(B[:, 0]):
            return False
        if min(A[:, 0]) >= max(B[:, 0]):
            return False
        return True

        
