import argparse
import threading
import time

import mavComm
import camera
import preprocessor_functions as preprocessor
import Location
import mainRecognition1
from PIL import Image
import csv

import cv2

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
                         nargs = 2 )

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
        gndThread = threading.Thread( target = gnd.loop, name = 'pixhawk telemetry' )
        gnd.startRWLoop()
        gndThread.start()
    except Exception, e:
        print("**Ground Error**")
        print(str( e ))
        exit(1)

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
    except Exception, e:
        print("**Pixhawk Error**")
        gnd.sendTxtMsg( "Pixhawk has not initialised" )
        print( str(e) )
        exit(2)

    resolution = (1280, 960)
    size = 20
    with open("recogntionData.csv", mode = "a") as file:
        fileWriter = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        fileWriter.writerow(['LatGPS', 'LonGPS', 'Alt', 'Roll', 'Pitch', 'Yaw', 'Letter', 'Conf.', 'Lat', 'Lon'])

        # Image capture
        cam = None
        try:
            cam = camera.Camera(resolution = resolution)
        except Exception, e:
            print("**Image Error**")
            print( str(e) )
            gnd.sendTxtMsg("Camera has not initialised")
            pix.sendTxtMsg( "Camera has not initialised" )
            time.sleep(2)

        # Preprocessor
        pre = None
        try:
            pre = preprocessor.preprocessor( size )
        except Exception, e:
            print("**Preprocessor Error**")
            print( str(e) )
            gnd.sendTxtMsg( "Preprocessor has not initialised" )
            pix.sendTxtMsg( "Preprocessor has not initialised" )

        # Location
        loc = None
        try:
            loc = Location.letterLoc(Imres = resolution)
        except Exception, e:
            print("**Location Error**")
            print( str(e) )
            gnd.sendTxtMsg( "Location has not initialised" )
            pix.sendTxtMsg( "Location has not initialised" )
        
        #Recognition
        Recognition = None
        try:
            Recognition = mainRecognition1.Recognition(size)
        except Exception, e:
            print("**Recognition Error**")
            print( str(e) )
            gnd.sendTxtMsg( "Recognition has not initialised" )
            pix.sendTxtMsg( "Recognition has not initialised" )

        try:
            while True:
                image = cam.getImage()
                sixdof = pix.get6DOF()
                # print(sixdof)
                
                time.sleep(0.5)
#                
#                sixdof.alt = 5 #########################
#                sixdof.lat = 51.3 #########################
#                sixdof.lon = -2.3 ####################
                
                rawData = (sixdof, image)

                success, croppedImage, center = pre.locateSquare(rawData[1])
                if not success:
                    continue

                # 6DOF, Cropped Image, Center Location
                croppedData = (rawData[0], croppedImage, center)

                coord = loc.Locate(croppedData[0], croppedData[2])
                #print('Coords: ', coord)

                # Add classifier here
                BW = cv2.cvtColor(croppedData[1], cv2.COLOR_BGR2GRAY)

                Thresh = 175
                BW[BW < Thresh] = 0
                BW[BW >= Thresh] = 255
                
                #cv2.imshow('BW', BW)
                #cv2.waitKey(1)
                
                Guess, confidence = Recognition.Identify(BW, size)            

                # Add sorting code

                # Add transmission code here
                gnd.sendTelemMsg(Guess, confidence, coord[0], coord[1])
                print("Letter: %s\tConfidence: %f\tLat: %f\tLon: %f" % (Guess, confidence, coord[0], coord[1]) )
            
                fileWriter.writerow([sixdof.lat,sixdof.lon,sixdof.alt,sixdof.roll,sixdof.pitch,sixdof.yaw,Guess,confidence,coord[0],coord[1]])

        except KeyboardInterrupt:
            pass
        
        except Exception, e:
            print( str(e) )
        

        # Close port and finish
        pix.closeSerialPort()
        gnd.closeSerialPort()
        cam.close()

# ------------------------------------ EOF -------------------------------------