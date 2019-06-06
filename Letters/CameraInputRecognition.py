import time
import picamera
import numpy as np
import cv2
from functions import rot_crop
import mainRecognition

camera = picamera.PiCamera()
size = 60
res = [size*16,size*12]
#camera.resolution = (320, 240)
camera.resolution = (res[0], res[1])
camera.framerate = 24
time.sleep(2)

try:
    while(1):       
        #image = np.empty((240, 320, 3), dtype=np.uint8)
        image = np.empty((res[1], res[0], 3), dtype=np.uint8)
        camera.capture(image, 'bgr')
        lineThickness = 2
        #cv2.line(image, (10, 10), (200,200), (0,255,0), lineThickness)
        #image = cv2.inRange(image, (100,90,90),(255,255,255));
        
        ## convert to HSV
        hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
        
        ## mask of red
        mask1 = cv2.inRange(hsv,(0,100,100),(10,255,255))
        mask2 = cv2.inRange(hsv,(160,100,100),(179,255,255))
        added = cv2.addWeighted(mask1,1.0,mask2,1,0)
        
        _, contours, hierachy = cv2.findContours(added, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours)!=0:
            contours = sorted(contours,key = cv2.contourArea,reverse = True)[0:1]
            pts = cv2.minAreaRect(contours[0])
            #pts = tuple([pts[0],tuple([pts[1][0]*1.5,pts[1][1]*1.5]),pts[2]]) ## show area around letter too
            box = np.int0(cv2.boxPoints(pts))
            
            cv2.drawContours(image,[box],-1,(0,255,0),2)
        
            img2 = rot_crop(image,pts,box,20,20)
            img2 = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
            
            cv2.drawContours(image,[box],-1,(0,255,0),2)
            ret,img2 = cv2.threshold(img2,127,255,cv2.ADAPTIVE_THRESH_MEAN_C)
            cv2.bitwise_not(img2,img2)
            cv2.imshow("image", image)
            #cv2.imwrite('pic.jpg',img2)
                           
            Letter = mainRecognition.Identify(img2)
            
            cv2.waitKey(1)
except (KeyboardInterrupt):
    pass
finally:
    camera.close()
