import argparse
import threading
import time

import mavComm
import basler_cam as camera
import preprocessor_functions as preprocessor
import Location
from load_tf_network import initialise_classifier, classify
from PIL import Image
import csv
import numpy as np
import traceback
import sys
import cv2
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.preprocessing import StandardScaler

import Jetson.GPIO as GPIO



def heartBeatLoop():
    ledstate = False
    while True:
        gnd.sendHeartbeat()

        ledstate = not ledstate
        GPIO.output(15, ledstate)

        time.sleep(3)
    
pic_counter = 1
label = 1
path = '/home/tbd/Pictures/'

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
    except Exception as e:
        print("**Ground Error**")
        print(str( e ))
        #exit(1) # no idea what this is but it wont run with it

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
    except Exception as e:
        print("**Pixhawk Error**")
        gnd.sendTxtMsg( "Pixhawk has not initialised" )
        print( str(e) )

    # Setup Heartbeat LED and message
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(15, GPIO.OUT, initial=GPIO.LOW) # Heartbeat LED

    GPIO.setup(16, GPIO.OUT, initial=GPIO.LOW)
    ledstate = False

    heartBeatThread = threading.Thread(target=heartBeatLoop, name='heartBeatLoop', daemon=True).start()


    # Main Loop setup
    resolution = (1920, 1200)
    size = 28
    
    with open("recogntionData.csv", mode = "a") as file:
        fileWriter = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        fileWriter.writerow(['Date', 'Time', 'LatGPS', 'LonGPS', 'Alt', 'Roll', 'Pitch', 'Yaw', 'Letter', 'Conf.', 'Lat', 'Lon'])

        # Image capture
        cam = None
        try:
            cam = camera.Camera()
        except Exception as e:
            print("**Image Error**")
            print( str(e) )
            gnd.sendTxtMsg("Camera has not initialised")
            pix.sendTxtMsg( "Camera has not initialised" )
            time.sleep(2)

        # Preprocessor
        pre = None
        try:
            pre = preprocessor.preprocessor( size )
        except Exception as e:
            print("**Preprocessor Error**")
            print( str(e) )
            gnd.sendTxtMsg( "Preprocessor has not initialised" )
            pix.sendTxtMsg( "Preprocessor has not initialised" )

        # Location
        loc = None
        try:
            loc = Location.letterLoc(Imres = resolution)
        except Exception as e:
            print("**Location Error**")
            print( str(e) )
            gnd.sendTxtMsg( "Location has not initialised" )
            pix.sendTxtMsg( "Location has not initialised" )
        
        #Recognition
        classes = np.array(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                            'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'])

        try:
            tf_sess, input_tensor_name, output_tensor = initialise_classifier()

            classify(tf_sess, output_tensor, input_tensor_name, np.zeros([28, 28, 3], dtype=np.uint8))
        except Exception as e:
            print("**Recognition Error**")
            print( str(e) )
            gnd.sendTxtMsg( "Recognition has not initialised" )
            pix.sendTxtMsg( "Recognition has not initialised" )

        print("**Aircraft Systems Initialised**")
        gnd.sendTxtMsg( "Aircraft Systems Initialised" )
        pix.sendTxtMsg( "Aircraft Systems Initialised" )

        GPIO.output(16, GPIO.HIGH)
        ledstate = True

        if args.disp:
            cv2.namedWindow('title', cv2.WINDOW_NORMAL)

        label_arr = np.array([0])
        coord_arr = np.array([[0,0]])

        print("ready to start capturing")
        while True:
            try:

                sixdof = pix.get6DOF()
                image = cam.getImage()

                if image is None:
                    try:
                        cam.close()
                        cam = camera.Camera()
                    except:
                        raise Exception('Camera not connected')

                    raise Exception('Camera Connection Restored')

                #time.sleep(0.5)

                #sixdof.alt = 40
                #sixdof.lat = 1
                #sixdof.lon = 1

                rawData = (sixdof, image)
                success, croppedImage, rect = pre.locateSquare(rawData[1])

                if success:
                    # 6DOF, Cropped Image, Center Location
                    #rect = centre, lengths, angle
                    croppedData = (rawData[0], croppedImage, rect[0])

                    if args.disp:
                        box_pts = np.int0(cv2.boxPoints(rect))
                        cv2.drawContours(image, [box_pts], 0, (255, 0, 0), 3)
                        cv2.imshow('title', image)
                        cv2.waitKey(1)

                    if (croppedData[0].lat and croppedData[0].lon != 0) and (croppedData[0].alt > 0):
                        coord = loc.Locate(croppedData[0], croppedData[2])
                    else:
                        coord = (0, 0)
                        #continue

                    proba, idxs = classify(tf_sess, output_tensor, input_tensor_name, croppedImage)
                    guess = classes[idxs[0]]
                    confidence = proba[0][idxs[0]]
                    # Add sorting code
                    #if pic_counter >= 10:
                    #    cv2.imwrite(path + 'picture' + str(label) + '.jpg', image)
                    #    label = label + 1
                    #    pic_counter = 0
                    #pic_counter = pic_counter+1
                    # transmission code

                    GPSdate = sixdof.datetime.strftime("%Y-%m-%d")
                    GPStime = sixdof.datetime.strftime("%H-%M")

                    print("Seq: %.0f\tLetter: %s\tConfidence: %f\tLat: %f\tLon: %f\troll: %f\tpitch: %f\tyaw: %f\tGPSdate: %s\tGPStime: %s" % (gnd._seq, guess, confidence, coord[0], coord[1], sixdof.roll, sixdof.pitch, sixdof.yaw, GPSdate, GPStime))
                    try:
                        gnd.sendTelemMsg(guess, confidence, coord[0], coord[1])
                    except:
                        traceback.print_exc(file=sys.stdout)

                    # CLUSTERING CODE
                    #label_arr = np.append(idxs[0])
                    #db = DBSCAN(eps = 0.0001, min_samples=10).fit(coord_arr)

                    fileWriter.writerow([GPSdate, GPStime,sixdof.lat,sixdof.lon,sixdof.alt,sixdof.roll,sixdof.pitch,sixdof.yaw,guess,confidence,coord[0],coord[1]])

                    ledstate = not ledstate
                    GPIO.output(16, ledstate)

                elif args.disp:
                    cv2.imshow('title', image)
                    cv2.waitKey(1)

            except KeyboardInterrupt:
                break

            except Exception as e:
                gnd.sendTxtMsg(str(e))
                traceback.print_exc(file=sys.stdout)
                time.sleep(1)

        GPIO.cleanup()

        # Close port and finish
        pix.closeSerialPort()
        gnd.closeSerialPort()
        cam.close()

# ------------------------------------ EOF -------------------------------------
