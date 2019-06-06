import argparse
import threading
import sys
import time
if sys.version_info.major == 3:
    import queue
else:
    import Queue as queue

import mavComm

# ------------------------------------------------------------------------------
# Argument parsing
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description = 'Graphical User Interface for the 868 Emergency '
                          'Override Connection' )

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

    try:
        while True:
            sixDOF = pix.get6DOF()
            print(sixDOF)
            time.sleep(0.1)

    except KeyboardInterrupt:
        pass

    # Close port and finish
    pix.closeSerialPort()

# ------------------------------------ EOF -------------------------------------