# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 10:53:41 2019

@author: Michael Morris
"""
import cv2
import numpy as np

def auto_canny(image, sigma=0.2):
	# compute the median of the single channel pixel intensities
	v = np.median(image)
 
	# apply automatic Canny edge detection using the computed median
	lower = int(max(0, (1.0 - sigma) * v))
	upper = int(min(255, (1.0 + sigma) * v))
	edged = cv2.Canny(image, lower, upper)
 
	# return the edged image
	return edged

def find_square(image):
    src_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    src_gray = cv2.blur(src_gray, (3,3))
    canny_output = auto_canny(src_gray)
    # Find contours
    _, contours, hierarchy = cv2.findContours(canny_output, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    size = pts = 0
    height, width, channels= image.shape
    flag = 0
    for cnt in contours:
        rect = cv2.minAreaRect(cnt)
        temp = np.int0(cv2.boxPoints(rect))
        
        if rect[1][0] != 0 and rect[1][1] != 0:
            AR=abs(rect[1][0]/rect[1][1])-1
        else: 
            AR = 10
        if max(temp[:,1]) < width*0.75 and max(temp[:,0])-min(temp[:,0]) > size and AR < 0.3: 
            box = temp
            pts = rect
            size = max(temp[:,0])-min(temp[:,0])
            flag = 1
    if flag!=0:
        return [pts,box]
    return [0,0]
    

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
    cv2.imshow("output", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()   
    [pts,box] = find_square(img)
    posX = (min(box[:,0]))+((max(box[:,0]))-min(box[:,0]))/2
    posY = (min(box[:,1]))+((max(box[:,1]))-min(box[:,1]))/2
    pos = [posX,posY]
    warped = rot_crop(img,pts,box,280,280)
    [pts,box] = find_square(warped)
    img = rot_crop(warped,pts,box,28,28)
    return [img,pos]

def preprocess(frame):
    ## convert to HSV
    size = 28
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    
    ## mask of red
    #lower mask
    lower = np.array([0  ,100,100])
    upper = np.array([10 ,255,255])
    lower_red = cv2.inRange(hsv,lower,upper)
    
    ##upper mask
    lower = np.array([160,100,100])
    upper = np.array([180,255,255])
    upper_red = cv2.inRange(hsv,lower,upper)
    
    hsv_mask = cv2.add(lower_red,upper_red)
    
    _, contours, hierachy = cv2.findContours(hsv_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours,key = cv2.contourArea,reverse = True)[0:4]
    flag = 0
    for cnt in contours:
        rect = cv2.minAreaRect(cnt)
        #abs((rect[1][0]/rect[1][1])-1)<0.15 and
        if  min(rect[1]) > 10:
            box_pts = np.int0(cv2.boxPoints(rect))
            cv2.drawContours(frame,[box_pts],-1,(0,255,0),2)
            image = rot_crop(frame,rect,box_pts,size,size)
            flag = 1
            break
    
    if flag:
        return image
    return np.zeros([size,size,3])
