import argparse
import threading
# import sys
# if sys.version_info.major == 3:
#     import queue
# else:
#     import Queue as queue

import mavComm
import camera
import preprocessor_functions as preprocessor
import Location

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

    # Image capture
    camera = camera.Camera()

    # Preprocessor
    pre = preprocessor.preprocessor()

    # Location
    loc = Location.letterLoc()

    try:
        while True:
            image = camera.getImage()
            sixdof = pix.get6DOF()

            rawData = (sixdof, image)

            success, croppedImage, center = pre.locateSquare(rawData[1])
            if not success:
                continue

            # 6DOF, Cropped Image, Center Location
            croppedData = (rawData[0], croppedImage, center)

            coord = loc.Locate(croppedData[0], croppedData[2])

            # Add classifier here

            # Add sorting code

            # Add transmission code here
            print(coord)

    except KeyboardInterrupt:
        pass

    # Close port and finish
    pix.closeSerialPort()

# ------------------------------------ EOF -------------------------------------