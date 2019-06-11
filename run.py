import argparse
import threading
import time

import mavComm
import basler_cam as camera
import preprocessor_functions as preprocessor
import Location
#import mainRecognition1
from load_tf_network import initialise_classifier, classify
from PIL import Image
import csv
import numpy as np
import traceback
import cv2
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.preprocessing import StandardScaler



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

    resolution = (1920, 1200)
    size = 28
    
    with open("recogntionData.csv", mode = "a") as file:
        fileWriter = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        fileWriter.writerow(['LatGPS', 'LonGPS', 'Alt', 'Roll', 'Pitch', 'Yaw', 'Letter', 'Conf.', 'Lat', 'Lon'])

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
        Recognition = None
        try:
            tf_sess, input_tensor_name, output_tensor = initialise_classifier()
            #Recognition = mainRecognition1.Recognition(size)
        except Exception as e:
            print("**Recognition Error**")
            print( str(e) )
            gnd.sendTxtMsg( "Recognition has not initialised" )
            pix.sendTxtMsg( "Recognition has not initialised" )


        try:
            label_arr = np.array([0])
            coord_arr = np.array([[0,0]])

            print("ready to start capturing")
            while True:

                sixdof = pix.get6DOF()
                image = cam.getImage()
                #time.sleep(0.5)
                
#                sixdof.alt = 5 #########################
#                sixdof.lat = 51.3 #########################
#                sixdof.lon = -2.3 ####################
                
                rawData = (sixdof, image)
                success, croppedImage, center = pre.locateSquare(rawData[1])

                if success:
                    # 6DOF, Cropped Image, Center Location
                    croppedData = (rawData[0], croppedImage, center)

                    if (croppedData[0].lat and croppedData[0].lon != 0) and (croppedData[0].alt > 0):
                        coord = loc.Locate(croppedData[0], croppedData[2])
                    else:
                        coord = (0, 0)

                    classes = np.array(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                               'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'])
                    proba, idxs = classify(tf_sess, output_tensor, input_tensor_name, croppedImage)
                    guess = classes[idxs[0]]
                    confidence = proba[0][idxs[0]]
                    # Add sorting code

                    # transmission code
                    print("Letter: %s\tConfidence: %f\tLat: %f\tLon: %f" % (guess, confidence, coord[0], coord[1]))
                    gnd.sendTelemMsg(guess, confidence, coord[0], coord[1])


                    # CLUSTERING CODE
                    #label_arr = np.append(idxs[0])
                    #db = DBSCAN(eps = 0.0001, min_samples=10).fit(coord_arr)


                    fileWriter.writerow([sixdof.lat,sixdof.lon,sixdof.alt,sixdof.roll,sixdof.pitch,sixdof.yaw,guess,confidence,coord[0],coord[1]])

        except KeyboardInterrupt:
            pass
        
        except Exception as e:
            traceback.print_exc()
        

        # Close port and finish
        pix.closeSerialPort()
        gnd.closeSerialPort()
        cam.close()

# ------------------------------------ EOF -------------------------------------