import picamera
import numpy as np
import copy
import time

import mavComm

class Camera:
    def __init__(self, resolution = (1280, 960), framerate = 24):
        self._width = resolution[0]
        self._height = resolution[1]

        self._camera = picamera.PiCamera()
        self._camera.resolution = (self._width, self._height)
        self._camera.framerate = framerate

        time.sleep(2)

    def getImage( self ):
        framebuf = np.empty((self._height * self._width * 3), dtype=np.uint8)
        self._camera.capture(framebuf, 'bgr')
        
        return framebuf.reshape((self._height, self._width, 3));
    
    def close( self ):
        self._camera.close()
