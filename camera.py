import time
import picamera
import numpy as np
import copy

class Camera:
    def __init__(self, resolution = (1280, 960), framerate = 24):
        self._width = resolution[0]
        self._height = resolution[1]

        self._camera = picamera.PiCamera()
        self._camera.resolution = (self._width, self._height)
        self._camera.framerate = framerate

        self._framebuf = np.empty((self._width, self._height, 3), dtype=np.uint8)
        time.sleep(2)

    def getImage( self ):
        self._camera.capture(self._framebuf, 'bgr')
        return copy.copy(self._framebuf)

