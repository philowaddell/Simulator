import numpy as np

from config import _SCALE
from config import _SPEED
from config import _LANEWIDTH

from Geometry import *

class TrafficManager(object):
    def __init__(self):
        self.speed = 0
        self.lane = 0
        self.lanes = []
        self.vehicle = None
        
    def newScenario(self):
        # Reset camera lane
        self.resetLane()
        
        # Reset vehicle lane (0) and position (-1M)
        self.vehicle.laneChange = False
        self.vehicle.resetLane()
        self.vehicle.translate((0,0,-self.vehicle.getDistance()/_SCALE+1), True)
        
        # Set camera lane
        cam_pos = np.random.randint(-1,2)
        self.setLane(cam_pos)
        self.speed = 65 # Speed constant
        
        # Set overtaking vehicle start lane
        while True:
            car_pos = np.random.randint(-1,2)
            if cam_pos != car_pos:
                break
        self.vehicle.setLane(car_pos)
        
        # Set overtaking vehicle target lane
        car_dest = np.random.randint(-1,2)
        self.vehicle.targetLane = car_dest
        
        # Set overtaking distance
        dist_bracket = np.random.randint(3)
        # Bad:(5,15) | Medium: (20,30) | Good: (35, 45)
        dist = -((10 + dist_bracket * 15) + np.random.randint(-5,6))
        self.vehicle.setTargetDist(dist)
        
        return str(cam_pos+1) + str(car_pos+1) +  str(car_dest+1) + str(dist_bracket)
        
        
    def update(self):
        for lane in self.lanes:
            lane.translate((0,0,self.speed))
            

        # Relative speed
        zTransfrom = self.speed-self.vehicle.speed
        xTransform = 0
        
        if self.vehicle.lane != self.vehicle.targetLane:
            # When not changing lane
            if not self.vehicle.laneChange:
                # At the target distance from camera
                if self.vehicle.getDistance() < self.vehicle.targetDistance:
                    # Begin lane change
                    self.vehicle.laneChange = True
                # Otherwise stay in lane
                else:
                    xTransform = 0
            # When changing lanes
            else:
                # If within two units (arbitrary) of target lane centre
                if abs(self.vehicle.getRealLane() - self.vehicle.targetLane*_LANEWIDTH*_SCALE) < 2 * _SPEED:
                    # End lane change
                    self.vehicle.laneChange = False
                    self.vehicle.lane = self.vehicle.targetLane
                # Otherwise continue lane change
                else:
                    vec = (self.vehicle.targetLane - self.vehicle.lane)
                    xTransform = (vec / abs(vec)) * _SPEED
                
        
        self.vehicle.translate((xTransform,0,zTransfrom))
        
       
    def setLane(self, lane):
        # Inverted as is OpenGL translation
        glTranslatef(-lane*_LANEWIDTH*_SCALE, 0, 0)
        self.lane = -lane
        
    def resetLane(self):
        # Inverted as is OpenGL translation
        glTranslatef(-self.lane*_LANEWIDTH*_SCALE, 0, 0)
        self.lane = 0
        
    def setSpeed(self, speed):
        self.speed = speed
        


class Vehicle(object):
    def __init__(self, colour=(0,0,1)):
        self.speed = 75
        self.lane = 0
        self.targetLane = 1
        self.targetDistance = -40 * _SCALE
        self.laneChange = False
        self.geometry = Cube(origin=(self.lane,0.9,1),shape=(2,1.2,0), colour=colour, fill=True)

    def translate(self, transform, raw=False):
        self.geometry.translate(transform, raw)
        
    def getDistance(self):
        return self.geometry.origin[2]
        
    def getRealLane(self):
        return self.geometry.origin[0]
        
    def setLane(self, lane):
        self.geometry.translate((lane*_LANEWIDTH,0,0), True)
        self.lane = lane
        
    def resetLane(self):
        x_pos = self.geometry.origin[0]/_SCALE
        self.geometry.translate((-x_pos,0,0), True)
        self.lane = 0
        
    def setTargetDist(self, dist):
        self.targetDistance = dist * _SCALE
        
    def setSpeed(self, speed):
        self.speed = speed