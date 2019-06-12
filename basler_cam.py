import time
from pypylon import pylon
from PIL import Image

class Camera:
    def __init__(self, resolution=(1920, 1200), framerate=41):
        self._width = resolution[0]
        self._height = resolution[1]

        self._camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

        #self._camera.resolution = (self._width, self._height)
        #self._camera.framerate = framerate
        self._converter = pylon.ImageFormatConverter()
        self._converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        self._converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
        self._camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

       # self._camera.ExposureAuto = 'Continuous'
        self._camera.ExposureAuto = 'Off'
        self._camera.ExposureTime = 5000
        time.sleep(2)

    def getImage(self):
        flag = 0
        try:
            while not flag:
                result = self._camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
                if result.GrabSucceeded():
                    try:
                        image = self._converter.Convert(result)
                        img = image.GetArray()
                    finally:
                        result.Release()
                        flag = 1
        finally:
            return img

    def close(self):
        self._camera.StopGrabbing()
        print("Camera stopped grabbing")




