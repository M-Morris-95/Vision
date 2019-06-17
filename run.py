import argparse
import threading
import time
import traceback
import sys
import csv

import numpy as np
import cv2

import Jetson.GPIO as GPIO

from load_tf_network import initialise_classifier, classify
from clustering import clustering
import mavComm
import basler_cam as camera
import preprocessor_functions as preprocessor
import Location


def heartBeatLoop():
    ledstate = False
    while True:
        gnd.sendHeartbeat()

        ledstate = not ledstate
        GPIO.output(15, ledstate)

        time.sleep(3)

savePath = '/home/tbd/Pictures/'

# ------------------------------------------------------------------------------
# Argument parsing
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description = 'Vision Processing System for IMechE UAS Challenge' )

    parser.add_argument( '--pix', '-P',
                         type = str,
                         help = 'Pixhawk Serial port',
                         metavar = ('PORT', 'BAUD'),
                         default = None,
                         nargs = 2,
                         required = True)

    parser.add_argument( '--gnd', '-G',
                         type = str,
                         help = 'Ground Station Serial port',
                         metavar = ('PORT', 'BAUD'),
                         default = None,
                         nargs = 2 )

    parser.add_argument( '--disp', '-V',
                         help = 'Enable displaying of camera image',
                         default = None,
                         action = "store_true" )

    parser.add_argument('--save', '-S',
                        help='Save images from the camera',
                        default=None,
                        action="store_true")

    args = parser.parse_args()

# ------------------------------------------------------------------------------
# Setup program
# ------------------------------------------------------------------------------
    # Ground Telemetry
    gnd = None
    try:
        gnd = mavComm.groundTelemetry( shortHand = 'GND',
                                       mavSystemID = 102,
                                       mavComponentID = 1,
                                       serialPortAddress = args.gnd[0],
                                       baudrate = int( args.gnd[1] ) )
        gndThread = threading.Thread( target = gnd.loop, name = 'gcs telemetry' )
        gnd.startRWLoop()
        gndThread.start()
    except Exception:
        print("**Ground Error**")
        traceback.print_exc(file=sys.stdout)

    # Pixhawk telemetry
    pix = None
    try:
        pix = mavComm.pixhawkTelemetry( shortHand = 'PIX',
                                        mavSystemID = 101,
                                        mavComponentID = 1,
                                        serialPortAddress = args.pix[0],
                                        baudrate = int(args.pix[1]))

        pixThread = threading.Thread( target = pix.loop, name = 'pixhawk telemetry' )
        pix.startRWLoop()
        pixThread.start()
    except Exception:
        print("**Pixhawk Error**")
        gnd.sendTxtMsg( "Pixhawk has not initialised" )
        traceback.print_exc(file=sys.stdout)

    # Setup Heartbeat LED and message
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(15, GPIO.OUT, initial=GPIO.LOW) # Heartbeat LED
    GPIO.setup(16, GPIO.OUT, initial=GPIO.LOW) # Image LED
    ledstate = False

    heartBeatThread = threading.Thread(target=heartBeatLoop, name='heartBeatLoop', daemon=True).start()

    # Image setup
    resolution = (1920, 1200) # Camera image resolution
    size = 28 # Cropped image size (28x28) pixels

    # Camera
    cam = None
    try:
        cam = camera.Camera(resolution=resolution)
    except Exception:
        print("**Image Error**")
        traceback.print_exc(file=sys.stdout)
        gnd.sendTxtMsg("Camera has not initialised")

    # Red square detector
    try:
        pre = preprocessor.preprocessor(size=size)
    except Exception:
        print("**Preprocessor Error**")
        traceback.print_exc(file=sys.stdout)
        gnd.sendTxtMsg( "Preprocessor has not initialised" )

    # Geo-Locator
    try:
        loc = Location.letterLoc(Imres=resolution)
    except Exception:
        print("**Location Error**")
        traceback.print_exc(file=sys.stdout)
        gnd.sendTxtMsg( "Location has not initialised" )

    # Recognition classes
    classes = np.array(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                        'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'])

    # Setup tensor flow
    try:
        tf_sess, input_tensor_name, output_tensor = initialise_classifier()

        classify(tf_sess, output_tensor, input_tensor_name, np.zeros([28, 28, 3], dtype=np.uint8))
    except Exception as e:
        print("**Recognition Error**")
        print( str(e) )
        gnd.sendTxtMsg( "Recognition has not initialised" )

    # Ready to go
    print("**Aircraft Systems Initialised**")
    # gnd.sendTxtMsg( "Aircraft Systems Initialised" )

    GPIO.output(16, GPIO.HIGH)
    ledstate = True

    if args.disp:
        cv2.namedWindow('title', cv2.WINDOW_NORMAL)


    with open("recogntionData.csv", mode = "a") as file:
        fileWriter = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        fileWriter.writerow(['Seq', 'Date', 'Time',
                             'LatGPS', 'LonGPS', 'Alt',
                             'Roll', 'Pitch', 'Yaw',
                             'Pixel x', 'Pixel y',
                             'Letter', 'Conf.', 'Lat', 'Lon'])
        unscaled_data = np.array([[0, 0, 0, 0]])
        start = time.time()
        while True:
            try:

                image = cam.getImage()
                sixdof = pix.get6DOF()

                gnd.setSatCount(sixdof.satcount)

                rawData = (sixdof, image)

                # Check if camera is still operating correctly, if not restart it
                if image is None:
                    try:
                        cam.close()
                        cam = camera.Camera()

                    except KeyboardInterrupt:
                        raise KeyboardInterrupt

                    except Exception:
                        raise Exception('Camera not connected')

                    raise Exception('Camera Connection Restored')

                # Identify red squares in the image
                success, croppedImage, rect = pre.locateSquare(rawData[1])

                # Red square identified
                if success:
                    # 6DOF, Cropped Image, Center Location
                    croppedData = (rawData[0], croppedImage, rect[0])

                    coord = (0, 0)
                    if (croppedData[0].lat and croppedData[0].lon != 0):# and (croppedData[0].alt > 0):
                        try:
                            coord = loc.Locate(croppedData[0], croppedData[2])
                        except Exception:
                            traceback.print_exc(file=sys.stdout)
                            raise Exception('James Fucked It!!!')

                    try:
                        proba, idxs = classify(tf_sess, output_tensor, input_tensor_name, croppedImage)
                    except Exception:
                        traceback.print_exc(file=sys.stdout)
                        raise Exception('Michael Fucked It!!!')

                    guess = classes[idxs[0]]
                    confidence = proba[0][idxs[0]]

                    GPSdate = sixdof.datetime.strftime("%Y-%m-%d")
                    GPStime = sixdof.datetime.strftime("%H-%M-%S")

                    # Data logging
                    fileWriter.writerow([gnd._seq, GPSdate, GPStime,
                                         croppedData[0].lat, croppedData[0].lon, croppedData[0].alt, # Aircraft location
                                         croppedData[0].roll, croppedData[0].pitch, croppedData[0].yaw, # Aircraft attitude
                                         croppedData[2][0], croppedData[2][1], # Pixel location in image
                                         guess, confidence, coord[0], coord[1]]) # Geo-located letter
                    file.flush()

                    # If --save argument save images
                    if args.save:
                       cv2.imwrite(savePath + 'pic_%3.0f_%s.jpg' % (gnd._seq, guess), image)

                    # If --disp argument display image
                    if args.disp:
                        box_pts = np.int0(cv2.boxPoints(rect))
                        cv2.drawContours(image, [box_pts], 0, (255, 0, 0), 3)
                        cv2.imshow('title', image)
                        cv2.waitKey(1)

                    print("Seq: %.0f\tLetter: %s\tConfidence: %f\tLat: %f\tLon: %f\troll: %f\tpitch: %f\tyaw: %f\tGPSdate: %s\tGPStime: %s\tSatCount: %.0f" %
                           (gnd._seq, guess, confidence, coord[0], coord[1], sixdof.roll, sixdof.pitch, sixdof.yaw, GPSdate, GPStime, sixdof.satcount))

                    # Report to ground
                    gnd.sendTelemMsg(guess, confidence, coord[0], coord[1])

                    # Heartbeat LED
                    ledstate = not ledstate
                    GPIO.output(16, ledstate)

                    unscaled_data = np.append(unscaled_data,
                                      [[croppedData[0].lat, croppedData[0].lon, idxs[0], confidence]],
                                      axis=0)

                    cluster_guesses = clustering(unscaled_data)
                    gnd.updateClusters(cluster_guesses)


                elif args.disp:
                    cv2.imshow('title', image)
                    cv2.waitKey(1)

                if time.time() - start >= 3:
                    gnd.printClusters()
                    start = time.time()
                    print(gnd._clusters)

            except KeyboardInterrupt:
                break

            except Exception as e:
                gnd.sendTxtMsg(str(e))
                traceback.print_exc(file=sys.stdout)
                time.sleep(1)

        # Cleanup
        GPIO.cleanup()
        pix.closeSerialPort()
        gnd.closeSerialPort()
        cam.close()

# ------------------------------------ EOF -------------------------------------
