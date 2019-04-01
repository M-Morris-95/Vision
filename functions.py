# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 10:53:41 2019

@author: Michael Morris
"""
import cv2
import numpy as np
def find_square(image):
    _, contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
    size = 0
    height, width = image.shape
    pts = 0
    for cnt in contours:
        rect = cv2.minAreaRect(cnt)
        temp = cv2.boxPoints(rect)
        temp = np.int0(temp)
        H = (max(temp[:,1])-min(temp[:,1]))
        W = (max(temp[:,0])-min(temp[:,0]))
        
        if H != 0 and W != 0:
            AR=abs(H/W)-1
        else: 
            AR = 10
        if max(temp[:,1]) < width*0.75 and max(temp[:,0])-min(temp[:,0]) > size and AR < 0.3: 
            box = temp
            pts = rect
            size = max(temp[:,0])-min(temp[:,0])
    if pts == 0:
        pts = rect
        box = temp
    return [pts,box]

def rot_crop(image,pts,box,x,y):
    width = int(pts[1][0])
    height = int(pts[1][1])
    src_pts = box.astype("float32")
    dst_pts = np.array([[0, height-1],
                        [0, 0],
                        [width-1, 0],
                        [width-1, height-1]], dtype="float32")
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    out = cv2.warpPerspective(image, M, (width, height))
    out = cv2.resize(out,(x,y))
    return out

def process(img):
    _, threshold = cv2.threshold(img, 240, 255, cv2.THRESH_BINARY)
    [pts,box] = find_square(threshold)
    posX = (min(box[:,0]))+((max(box[:,0]))-min(box[:,0]))/2
    posY = (min(box[:,1]))+((max(box[:,1]))-min(box[:,1]))/2
    pos = [posX,posY]
    warped = rot_crop(threshold,pts,box,280,280)
    [pts,box] = find_square(warped)
    img = rot_crop(warped,pts,box,28,28)
    return [img,pos]
