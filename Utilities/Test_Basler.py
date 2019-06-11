from pypylon import pylon
import cv2

camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
converter = pylon.ImageFormatConverter()

converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        #access the image
        image = converter.Convert(grabResult)
        img = image.GetArray()
        cv2.namedWindow('title', cv2.WINDOW_NORMAL)
        cv2.imshow('title',img)
        k = cv2.waitKey(1)
        if k == 27:
            break
    grabResult.Release()

camera.StopGrabbing()

cv2.destroyAllWindows()
