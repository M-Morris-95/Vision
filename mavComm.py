# ------------------------------------------------------------------------------
# mavComm.py
# Generic MAVLink serial interface code, can be used to produce a threaded
# MAVLink handler. Read messages are stored in a specified read queue,
# write messages are added by other activities to a instance level queue.
# Once created the MAVAbstract instance registers itself in a class level
# dictionary for easy referencing. Unit tests for this file are contained in
# test_mavSerial.py and test_mavSocket.py.
#
# Author: Freddie Sherratt
# Created: 24.01.2017
# Last Modified: 25.05.2019
#
# Change List
# 03.01.2018 - Version 1 - FS
# 06.01.2018 - Addition of UDP socket communication class and named changed
#              to mavComm - FS
# 25.05.2019 - Adapted for UAS challenge - new object to fetch 6DOF data from
#              pixhawk
# ------------------------------------------------------------------------------
import serial
import time
import threading
import traceback
import abc
import sys
from datetime import datetime as dt
if sys.version_info.major == 3:
    import queue
else:
    import Queue as queue

import pymavlink.dialects.v10.ardupilotmega as pymavlink

# ------------------------------------------------------------------------------
# MAVAbstract
# Abstraction class for MAVLink serial communications, implements loop for
# threaded activity, write queue to allow multiple threads to push out
# mavlink data. The communication channel setup must be overloaded to set up
# a channel that inherits from commAbstract
# ------------------------------------------------------------------------------
class MAVAbstract:
    __metaclass__ = abc.ABCMeta
    # --------------------------------------------------------------------------
    # Class level variables
    # --------------------------------------------------------------------------
    portDict = {} #                                Dictionary of available ports
    _ser = None # Serial object inheriting from commAbstract, must be overridden
    # --------------------------------------------------------------------------
    # Public function definitions
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # __init__
    # MAVAbstract initializer, sets up all components required for MAVLink
    # communication except the communication channel. Once set up the serial
    # communication will only occur once the R/W loop is started using
    # startRWLoop
    # shortHand - Name to store port under in the portDict
    # param readQueue - queue object to write read messages to
    # param mavSystemID - MAVLink system ID default 78
    # param mavComponentID - MAVLink component ID
    # param noRWSleepTime - sleep time when nothing to read or write
    # param loopPauseSleepTime - sleep time when R/W loop is paused
    # return void
    # --------------------------------------------------------------------------
    @abc.abstractmethod
    def __init__( self, shortHand, mavSystemID, mavComponentID,
                  noRWSleepTime = 0.1, loopPauseSleepTime = 0.5 ):

        self._name = shortHand
        self.loopPauseSleepTime = loopPauseSleepTime
        self.noRWSleepTime = noRWSleepTime

        self._mavSystemID = mavSystemID
        self._mavComponentID = mavComponentID

        self._writeQueue = queue.Queue()

        self._loopRunning = False
        self._intentionallyExit = False

        if self._ser is None or not isinstance( self._ser, commAbstract ):
            raise NotImplementedError('_ser must be set to a object '
                                      'inheriting from `commAbstract` before '
                                      'super constructor is called')
        try:
            self._mavObj = pymavlink.MAVLink(
                    file = self._ser,
                    srcSystem = mavSystemID,
                    srcComponent = mavComponentID)
        except:
            raise Exception( 'Unable to create mavlink object' )

        # Add reference to port dictionary
        MAVAbstract.portDict[ self._name ] = self

    # --------------------------------------------------------------------------
    # srcSystem (getter)
    # Retrieve MAVLink system ID
    # param null
    # returns mavlink system id
    # --------------------------------------------------------------------------
    @property
    def srcSystem( self ):
        return self._mavObj.srcSystem

    # --------------------------------------------------------------------------
    # srcComponent (getter)
    # Retrieve MAVLink component ID
    # param null
    # returns mavlink component id
    # --------------------------------------------------------------------------
    @property
    def srcComponent( self ):
        return self._mavObj.srcComponent

    # --------------------------------------------------------------------------
    # startRWLoop
    # Starts the serial read/write loop by setting _loopRunning. When
    # starting the serial buffer is flushed and any data written to the
    # write queue is cleared. THe r/w loop can only be started if the serial
    # port is open
    # param null
    # return boolean True if successfully set loopRunning to True,
    # False otherwise
    # --------------------------------------------------------------------------
    def startRWLoop( self ):
        if self._loopRunning:
            return False

        if not self._ser.isOpen():
            return False

        self._ser.flush()

        try:
            while True:
                self._writeQueue.get_nowait()
        except queue.Empty:
            pass

        self._loopRunning = True

        return True

    # --------------------------------------------------------------------------
    # pauseRWLoop
    # Pauses the serial R/W loop by setting _loopRunning to False
    # param null
    # return void
    # --------------------------------------------------------------------------
    def pauseRWLoop( self ):
        self._loopRunning = False

    # --------------------------------------------------------------------------
    # stopRWLoop
    # Stops the serial R/W loop by setting _intentionallyExit to True and
    # _loopRunning to False. Stopping the serial loop does not close the
    # serial port
    # param null
    # return void
    # --------------------------------------------------------------------------
    def stopRWLoop( self ):
        self._intentionallyExit = True
        self._loopRunning = False

    # --------------------------------------------------------------------------
    # closeSerialPort
    # Close the serial port if open and also stop any associated serialRW loops.
    # param null
    # return void
    # --------------------------------------------------------------------------
    def closeSerialPort( self ):
        self.stopRWLoop()
        self._ser.closePort()

    # --------------------------------------------------------------------------
    # queueOutputMsg
    # Add mavlink messages to writing queue, does not accept messages when
    # RW loop is paused.
    # param: msg - mavlink message to add to the queue
    # return: boolean True if successful, false otherwise, exception if an error
    # --------------------------------------------------------------------------
    def queueOutputMsg( self, msg ):
        if not isinstance( msg, pymavlink.MAVLink_message ):
           return False

        if not self._loopRunning:
            return False

        self._writeQueue.put( msg )

        return True

    # --------------------------------------------------------------------------
    # loop
    # Mavlink serial reading and writing loop. The loop is controlled through
    # calls to startRWLoop, pauseRWLoop and stopRWLoop. by default the
    # loop starts in a paused state.
    # param null
    # return void
    # --------------------------------------------------------------------------
    def loop( self ):
        try:
            while not self._intentionallyExit:
                if self._loopRunning:

                    rMsg = self._readMsg()
                    wMsg = self._getWriteMsg()

                    if rMsg is None and wMsg is None:
                        time.sleep( self.noRWSleepTime )

                    else:
                        self._processReadMsg( rMsg )
                        self._writeMsg( wMsg )

                else:
                    time.sleep( self.loopPauseSleepTime )

        except Exception as e:
            traceback.print_exc(file=sys.stdout)

        self.closeSerialPort()

        print('Serial Thread %s Closed' % self._name )


    # --------------------------------------------------------------------------
    # Private function definitions
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # _processReadMsg
    # This function receives incoming mavlink messages once they are parsed
    # self and a timestamp
    # param msg - mavlink message object
    # return - void
    # --------------------------------------------------------------------------
    @abc.abstractmethod
    def _processReadMsg( self, msgList ):
        pass

    # --------------------------------------------------------------------------
    # _getWriteMsg
    # Returns the next item in the writing message queue
    # param null
    # return - MAVLink_message object from queue, None if queue empty,
    # Exception if an error occurs
    # --------------------------------------------------------------------------
    def _getWriteMsg(self):
        try:
            return self._writeQueue.get_nowait()

        except queue.Empty:
            return None

    # --------------------------------------------------------------------------
    # _writeMsg
    # Writes mavlink messages out as a bit stream on port associated with class
    # param msg - message to write out
    # return - True if msg written, Exception if an error occurs,
    # False otherwise
    # --------------------------------------------------------------------------
    def _writeMsg( self, msg ):
        if msg is None:
            return False

        try:
            msg.pack( self._mavObj )
            b = msg.get_msgbuf()

            self._ser.write( b )

            self._writeQueue.task_done()

            return True

        except queue.Empty:
            pass

        except pymavlink.MAVError as e:
            print('%s' % e)

        return False

    # --------------------------------------------------------------------------
    # _readMsg
    # read the next available mavlink message in the serial buffer
    # param null
    # return - List of MAVLink_message objects parsed from serial, None if
    # buffer empty, Exception if an error occurs
    # --------------------------------------------------------------------------
    def _readMsg( self ):
        mList = None

        try:
            while mList is None and self._ser.dataAvailable():
                x = self._ser.read()
                mList = self._mavObj.parse_buffer( x)

        except pymavlink.MAVError as e:
            print('%s' % e)

        return mList

# ------------------------------------------------------------------------------
# aircraft6DOF
# Storage object for mavlink 6 degree of freedom data
# ------------------------------------------------------------------------------
class aircraft6DOF:
    def __init__(self, lat, lon, alt, roll, pitch, yaw, datetime):
        self.lat = float(lat)/1e7
        self.lon = float(lon)/1e7
        self.alt = float(alt)/1e3
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw
        self.datetime = datetime

    def __str__(self):
        return "Lat %.3f, Lon %.3f, Alt %.3f, Roll %.3f, Pitch %.3f, Yaw %.3f, datetime %.3f" % \
               (self.lat, self.lon, self.alt, self.roll, self.pitch, self.yaw, self.datetime)

# ------------------------------------------------------------------------------
# serialMAVLink
# Abstraction layer for MAVLink communications over a serial connections
# ------------------------------------------------------------------------------
class pixhawkTelemetry( MAVAbstract ):
    # --------------------------------------------------------------------------
    # __init__
    # Creates and opens a serial communication channel then calls the super
    # initializer
    # shortHand - Name to store port under in the portDict
    # param readQueue - queue object to write read messages to
    # param mavSystemID - MAVLink system ID default 78
    # param mavComponentID - MAVLink component ID
    # param serialPortAddress - serial port address e.g. COM8
    # param baudrate - serial baudrate
    # param noRWSleepTime - sleep time when nothing to read or write
    # param loopPauseSleepTime - sleep time when R/W loop is paused
    # return void
    # --------------------------------------------------------------------------
    def __init__( self, shortHand, mavSystemID, mavComponentID,
                  serialPortAddress, baudrate = 57600, noRWSleepTime = 0.1,
                  loopPauseSleepTime = 0.5 ):
        self._roll = 0
        self._pitch = 0
        self._yaw = 0

        self._lat = 0
        self._lon = 0
        self._alt = 0

        self._datetime = dt.fromtimestamp(0)

        self._ser = serialConnect( serialPortAddress = serialPortAddress,
                                   baudrate = baudrate )
        self._ser.openPort()

        super( pixhawkTelemetry, self ).__init__(
                shortHand, mavSystemID, mavComponentID,
                noRWSleepTime,loopPauseSleepTime )

    # --------------------------------------------------------------------------
    # _processReadMsg
    # Overload of proccess read msg to extract telemetry information of interest
    # param null
    # return void
    # --------------------------------------------------------------------------
    def _processReadMsg( self, msgList ):
        if msgList is None:
            return False

        for msg in msgList:
            if isinstance( msg, pymavlink.MAVLink_message ):
                if msg.get_msgId() == pymavlink.MAVLINK_MSG_ID_ATTITUDE:
                    self._roll = msg.roll
                    self._pitch = msg.pitch
                    self._yaw = msg.yaw
                if msg.get_msgId() == pymavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT:
                    self._lat = msg.lat
                    self._lon = msg.lon
                    self._alt = msg.relative_alt
                if msg.get_msgId() == pymavlink.MAVLINK_MSG_ID_SYSTEM_TIME:
                    self._datetime = dt.fromtimestamp((int)(msg.time_unix_usec/1000000))

    # --------------------------------------------------------------------------
    # get6DOF (getter)
    # Retrieve aricraft 6 degree of freedom data
    # param null
    # returns 6 degree of freedom object
    # --------------------------------------------------------------------------
    def get6DOF(self):
        return aircraft6DOF(self._lat, self._lon, self._alt, self._roll, self._pitch, self._yaw, self._datetime)

    def sendTxtMsg( self, text ):
        text_byte = bytearray(text, encoding='utf8')
        msg = pymavlink.MAVLink_statustext_message( pymavlink.MAV_SEVERITY_ERROR, text_byte )
        self.queueOutputMsg(msg)


# ------------------------------------------------------------------------------
# serialMAVLink
# Abstraction layer for MAVLink communications over a serial connections
# ------------------------------------------------------------------------------
class groundTelemetry( MAVAbstract ):
    # --------------------------------------------------------------------------
    # __init__
    # Creates and opens a serial communication channel then calls the super
    # initializer
    # shortHand - Name to store port under in the portDict
    # param readQueue - queue object to write read messages to
    # param mavSystemID - MAVLink system ID default 78
    # param mavComponentID - MAVLink component ID
    # param serialPortAddress - serial port address e.g. COM8
    # param baudrate - serial baudrate
    # param noRWSleepTime - sleep time when nothing to read or write
    # param loopPauseSleepTime - sleep time when R/W loop is paused
    # return void
    # --------------------------------------------------------------------------
    def __init__( self, shortHand, mavSystemID, mavComponentID,
                  serialPortAddress, baudrate = 57600, noRWSleepTime = 0.1,
                  loopPauseSleepTime = 0.5 ):

        self._seq = 0.0
        self._seqHB = 0

        self._ser = serialConnect( serialPortAddress = serialPortAddress,
                                   baudrate = baudrate )
        self._ser.openPort()

        super( groundTelemetry, self).__init__(
            shortHand, mavSystemID, mavComponentID,
            noRWSleepTime, loopPauseSleepTime )

    # --------------------------------------------------------------------------
    # _processReadMsg
    # Overload of proccess read msg to extract telemetry information of interest
    # param null
    # return void
    # --------------------------------------------------------------------------
    def _processReadMsg(self, msgList):
        if msgList is None:
            return

        for msg in msgList:
            if isinstance(msg, pymavlink.MAVLink_message):
                if msg.get_msgId() == pymavlink.MAVLINK_MSG_ID_COMMAND_LONG:
                    print("Confidence: %f%%, Letter: %s, Lat: %f, Lon: %f " % (msg.param3*100, chr( msg.confirmation ),
                                                             msg.param2, msg.param1))
                elif msg.get_msgId() == pymavlink.MAVLINK_MSG_ID_STATUSTEXT:
                    print( msg )

    def sendTelemMsg(self, letter, confidence, lat, lon):
        letter_byte = bytearray(letter, encoding='utf8')
        msg = pymavlink.MAVLink_command_long_message( 0, 0,
                                                      pymavlink.MAV_CMD_USER_1,
                                                      letter_byte[0],
                                                      lon,
                                                      lat,
                                                      confidence, self._seq, 0, 0, 0)
        self.queueOutputMsg(msg)
        self._seq += 1.0

    def sendHeartbeat( self ):
        msg = pymavlink.MAVLink_heartbeat_message(self._seqHB, 0, 0, 0, 0, 0)
        self.queueOutputMsg(msg)

        self._seqHB += 1
        if self._seqHB > 255:
            self._seqHB = 0

    def sendTxtMsg( self, text ):
        text_byte = bytearray(text, encoding='utf8')
        msg = pymavlink.MAVLink_statustext_message( pymavlink.MAV_SEVERITY_ERROR, text_byte )
        self.queueOutputMsg(msg)

# ------------------------------------------------------------------------------
# commAbstract
# Abstract class for communication methods that are called by a object
# inheriting from the MAVAbstract object
# ------------------------------------------------------------------------------
class commAbstract:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def openPort( self ):
        pass

    @abc.abstractmethod
    def closePort( self ):
        pass

    @abc.abstractmethod
    def read( self ):
        pass

    @abc.abstractmethod
    def write( self, b ):
        pass

    @abc.abstractmethod
    def isOpen( self ):
        pass

    @abc.abstractmethod
    def dataAvailable( self ):
        pass

    @abc.abstractmethod
    def flush( self ):
        pass


# ------------------------------------------------------------------------------
# serialClass
# Abstraction layer for serial communications, implements operations in a
# thread safe manner
# ------------------------------------------------------------------------------
class serialConnect( commAbstract ):
    # --------------------------------------------------------------------------
    # Public function definitions
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # __init__
    # initialise serialClass object, does not start the serial port. Call
    # openPort once object is initialised to start serial communication.
    # param serialPortName serial port address e.g. COM8
    # param baudrate - serial baudrate
    # param timeout - serial read timeout
    # param writeTimeout - serial write timeout
    # return void
    # --------------------------------------------------------------------------
    def __init__( self, serialPortAddress, baudrate = 57600, readtimeout = 0.01,
                  writeTimeout = 3 ):

        self._readTimeout = readtimeout

        self._serialObj = serial.Serial()

        self._serialObj.port = serialPortAddress
        self._serialObj.baudrate = baudrate
        self._serialObj.timeout = readtimeout
        self._serialObj.write_timeout = writeTimeout

        self._writeLock = threading.Lock()
        self._readLock = threading.Lock()

    # --------------------------------------------------------------------------
    # openPort
    # Open the serial port specified during __init__
    # param null
    # return raises an exception if there is an error
    # --------------------------------------------------------------------------
    def openPort( self ):
        if self.isOpen():
            raise Exception('Port already open')

        try:
            self._serialObj.open()
        except Exception as e:
            raise e

    # --------------------------------------------------------------------------
    # closePort
    # Close the serial port if it is open
    # param null
    # return void
    # --------------------------------------------------------------------------
    def closePort( self ):
        try:
            if self._serialObj.isOpen:
                self._serialObj.close()
        except serial.SerialException:
            pass

    # --------------------------------------------------------------------------
    # read
    # Thread safe operation, it reads data in from the serial FIFO buffer
    # param numBytes - number of bytes to read
    # return raises an Exception if there is an error
    # --------------------------------------------------------------------------
    def read( self, numBytes = 1 ):
        self._readLock.acquire()

        try:
            b = self._serialObj.read( numBytes )

        except Exception as e:
            raise e

        finally:
            self._readLock.release()

        return b

    # --------------------------------------------------------------------------
    # write
    # Thread safe operation, it writes byte array data out the serial port
    # param b - byte array to write
    # return raises an Exception if there is an error
    # --------------------------------------------------------------------------
    def write( self, b ):
        self._writeLock.acquire()

        try:
            self._serialObj.write( b )

        except Exception as e:
            raise e

        finally:
            self._writeLock.release()

    # --------------------------------------------------------------------------
    # isOpen
    # Check is serial port has been closed
    # param null
    # return void
    # --------------------------------------------------------------------------
    def isOpen( self ):
        try:
            return self._serialObj.isOpen()
        except serial.SerialException:
            return False

    # --------------------------------------------------------------------------
    # dataAvailable
    # Check is serial input FIFO has data waiting to be read
    # param null
    # return True if data available to read, False otherwise
    # --------------------------------------------------------------------------
    def dataAvailable( self ):
        try:
            if self._serialObj.inWaiting() > 0:
                return True
        except:
            pass

        return False

    # --------------------------------------------------------------------------
    # flush
    # Clear the serial input buffer
    # param null
    # return void
    # --------------------------------------------------------------------------
    def flush( self ):
        try:
            pass
            # self._serialObj.reset_input_buffer()
        except serial.SerialException:
            pass

# ------------------------------------ EOF -------------------------------------
