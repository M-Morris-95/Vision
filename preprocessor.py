# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 13:26:53 2019

@author: Michael Morris
"""

# Standard imports
import os
import cv2
from functions import process

# change directory
path = os.getcwd()
path = path +'\\Training_Data\\Folders\\F'
os.chdir(path)

img = cv2.imread("20190329_112926.jpg", cv2.IMREAD_GRAYSCALE)

output,pos = process(img)
print(pos)
cv2.imshow("output", output)
cv2.waitKey(0)
cv2.destroyAllWindows()   