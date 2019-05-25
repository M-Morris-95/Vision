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
    captureQueue = queue.Queue()

    # Pixhawk telemetry
    pix = mavComm.pixhawkTelemetry( shortHand = 'PIX',
                                    mavSystemID = 101,
                                    mavComponentID = 1,
                                    serialPortAddress = args.gcs[0],
                                    baudrate = int(args.gcs[1]))

    serialReader = threading.Thread( target = pix.loop, name = 'pixhawk telemetry' )
    pix.startRWLoop()

    # Image capture
    captureObject = camera.CaptureLoop( captureQueue )
    captureThread = threading.Thread( target = captureObject.loop, name = 'camera capture' )

    # Start threads
    serialReader.start()
    captureThread.start()

    try:
        while True:
            try:
                newData = captureQueue.get_nowait()
                print(newData[0])

            except queue.Empty:
                time.sleep(0.5)

    except KeyboardInterrupt:
        pass

    # Close port and finish
    pix.closeSerialPort()

# ------------------------------------ EOF -------------------------------------