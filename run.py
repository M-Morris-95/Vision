import argparse
import threading
import sys
import time
if sys.version_info.major == 3:
    import queue
else:
    import Queue as queue

import mavComm
import camera

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
    pix = mavComm.pixhawkTelemetry( shortHand = 'PIX',
                                    mavSystemID = 101,
                                    mavComponentID = 1,
                                    serialPortAddress = args.gcs[0],
                                    baudrate = int(args.gcs[1]))

    # Start threads
    serialReader = threading.Thread( target = pix.loop, name = 'serial_loop' )
    serialReader.start()
    pix.startRWLoop()

    camObj = camera.Camera()

    try:
        while True:
            image = camObj.getImage()
            sixDOF = pix.get6DOF()
            time.sleep(1)

    except KeyboardInterrupt:
        pass

    # Close port and finish
    pix.closeSerialPort()

# ------------------------------------ EOF -------------------------------------