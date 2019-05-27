import argparse
import threading
import time

import mavComm
import camera
import preprocessor_functions as preprocessor
import Location

import cv2

# ------------------------------------------------------------------------------
# Argument parsing
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description = 'Vision Processing System for IMechE UAS Challenge' )

    parser.add_argument( '--gcs', '-G',
                         type = str,
                         help = 'GCS Serial port',
                         metavar = ('PORT', 'BAUD'),
                         default = None,
                         nargs = 2 )

    args = parser.parse_args()

# ------------------------------------------------------------------------------
# Setup program
# ------------------------------------------------------------------------------
    # Pixhawk telemetry
    pix = mavComm.pixhawkTelemetry( shortHand = 'PIX',
                                    mavSystemID = 101,
                                    mavComponentID = 1,
                                    serialPortAddress = args.gcs[0],
                                    baudrate = int(args.gcs[1]))

    pixThread = threading.Thread( target = pix.loop, name = 'pixhawk telemetry' )
    pix.startRWLoop()
    pixThread.start()
    
    resolution = (1280, 960)

    # Image capture
    camera = camera.Camera(resolution = resolution)

    # Preprocessor
    pre = preprocessor.preprocessor()

    # Location
    loc = Location.letterLoc(Imres = resolution)

    try:
        while True:
            image = camera.getImage()
            sixdof = pix.get6DOF()
            # print(sixdof)
            
            time.sleep(0.5)
            
            rawData = (sixdof, image)

            success, croppedImage, center = pre.locateSquare(rawData[1])
            if not success:
                continue
            
            print( center )
            # print( croppedImage.shape )
            
            cv2.imshow( 'croppedImage', croppedImage )
            cv2.waitKey(1)

            # 6DOF, Cropped Image, Center Location
            croppedData = (rawData[0], croppedImage, center)

            
            coord = loc.Locate(croppedData[0], croppedData[2])
            print('Coords: ', coord)

            # Add classifier here

            # Add sorting code

            # Add transmission code here
            

    except KeyboardInterrupt:
        pass
    
    except Exception, e:
        print( str(e) )
    

    # Close port and finish
    pix.closeSerialPort()
    camera.close()

# ------------------------------------ EOF -------------------------------------