from math import sin, cos, tan, sqrt, atan2, radians
import utm

class letterLoc:

    def __init__(self, fov = [radians(67.4), radians(45.5)], Imres = (1280, 960)):
        self.letterCoor = [0, 0]
        self.UTM = [0, 0]
        self.fov = fov
        self.Imres = Imres
        self.y = 0
        self.x = 0

    #Find distance, m, of target from roll axis of aircraft
    def rollAdj(self, sixdof, SqLoc):
        dist = sixdof.alt / cos(sixdof.roll)
        Imwidth = 2 * dist * tan(self.fov[0] / 2)
        d = SqLoc[0] * Imwidth / self.Imres[0]
        self.y = ((sixdof.alt * sin(sixdof.roll) + d) / cos(sixdof.roll)) - Imwidth/2

        pass

    #Find distance, m, of target from pitch axis of aircraft
    def pitAdj(self, sixdof, SqLoc):
        dist = sixdof.alt / cos(sixdof.pitch)
        Imheight = 2 * dist * tan(self.fov[1] / 2)
        d = SqLoc[1] * Imheight / self.Imres[1]
        self.x = -(((sixdof.alt * sin(sixdof.pitch) + d) / cos(sixdof.pitch)) - Imheight/2)

        pass

    #Find lat/long of target
    def findLatLon(self, sixdof):
        planeUTM = utm.from_latlon(sixdof.lat, sixdof.lon)

        h = sqrt((self.x**2) + (self.y**2))
        alpha = atan2(self.y, self.x)
        A = h*sin(sixdof.yaw + alpha)
        B = h*cos(sixdof.yaw + alpha)

        self.letterCoor = utm.to_latlon(planeUTM[0]+A, planeUTM[1]+B, planeUTM[2], planeUTM[3])

        pass


    def Locate(self, sixdof, SqLoc):
        sixdof.roll = -sixdof.roll
        sixdof.pitch = -sixdof.pitch
        self.rollAdj(sixdof, SqLoc)
        self.pitAdj(sixdof, SqLoc)

        self.findLatLon(sixdof)

        return self.letterCoor
