import argparse
import threading
import time
import sys
import mavComm

if sys.version_info.major == 3:
    import queue
else:
    import Queue as queue



# ------------------------------------------------------------------------------
# Argument parsing
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = 'Vision Processing System for IMechE UAS Challenge' )

    parser.add_argument( '--gnd', '-G',
                         type = str,
                         help = 'Ground Station Serial port',
                         metavar = ('PORT', 'BAUD'),
                         default = None,
                         nargs = 2 )

    args = parser.parse_args()

    # ------------------------------------------------------------------------------
    # Setup program
    # ------------------------------------------------------------------------------
    # Ground Telemetry
    gnd = mavComm.groundTelemetry( shortHand = 'GND',
                                   mavSystemID = 102,
                                   mavComponentID = 1,
                                   serialPortAddress = args.gnd[0],
                                   baudrate = int( args.gnd[1] ) )
    gndThread = threading.Thread( target = gnd.loop, name = 'pixhawk telemetry' )
    gnd.startRWLoop()
    gndThread.start()

    print('**Running**')

    try:
        while True:
            gnd.sendHeartbeat()
            time.sleep( 1 )

    except KeyboardInterrupt:
        pass

    except Exception as e:
        print(str( e ))

    # Close port and finish
    gnd.closeSerialPort()

# ------------------------------------ EOF -------------------------------------
