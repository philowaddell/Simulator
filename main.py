from os import environ 
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '0'

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

from config import _FPS
from config import _SCALE
from config import _SPEED
from config import _LANEWIDTH

from Geometry import *
from TrafficManagement import *
from Utilities import *

import matplotlib.pyplot as plt
from PIL import Image 

import time



 #    7 Z-axis (Towards -ve Z)
 #   /
 #  /
 # +--------> X-axis (Towards +ve X)
 # |
 # |
 # |
 # V Y-axis (Towards -ve Y)
 
class Simulator(object):
    def __init__(self, fovy=78, resolution=(1280,720)):
        self.resolution = resolution
        # 78 fovy gives ~140fovx at 720p resolution (average for many dashcams)
        self.fovy = fovy
        self.geometry = []
        self.tm = TrafficManager()
        #self.fm = FileManager()
        self.recorder = Recorder(resolution)
        self.running = True
        
        # Start pygame window and configure perspective
        pygame.init()
        self.window = pygame.display.set_mode(self.resolution, DOUBLEBUF|OPENGL|NOFRAME)
        gluPerspective(fovy, (self.resolution[0]/self.resolution[1]), 0.1*_SCALE, 200*_SCALE)
        glTranslatef(0, -1.2*_SCALE, 0)
        
        
    def run(self):
        while self.running:
            scenario = self.tm.newScenario()
            self.recorder.openNew(scenario)
            print('INFO: Simulating scenario type: %s' % scenario)
            for frame in range(25 * _FPS + 1):
                glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
                
                self.tm.update()
                
                for geometry in self.geometry:
                    geometry.render()
                    
                pygame.display.flip()

                self.recorder.add(pygame.image.tostring(self.window, "RGB"))
                self.checkExit()
            
            self.recorder.stop() 
            
        
    def exit(self):
        pygame.quit()
        print('WARNING: Please wait! Render in progress..')
        while self.recorder.isRecording():
            time.sleep(5)
        print('INFO: Simulation terminated.')
        quit()
                  
    def checkExit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print('INFO: Preparing to quit... ')
                self.running = False
                
                
    def addStaticGeometry(self, geometry):
        self.geometry.append(geometry)
        
    def addLane(self, lane):
        self.tm.lanes.append(lane)
        self.geometry.append(lane)
        
    def addVehicle(self, vehicle):
        self.tm.vehicle = vehicle
        self.geometry.append(vehicle.geometry)
    
        

if __name__ == '__main__':  

    simulator = Simulator()
    
    # Add edges of motorway
    simulator.addStaticGeometry(Cube(origin=(-1.5*_LANEWIDTH,0,-100), shape=(0.15,0,200)))
    simulator.addStaticGeometry(Cube(origin=(1.5*_LANEWIDTH,0,-100), shape=(0.15,0,200)))
    
    # Add broken lines between lanes
    simulator.addLane(DashedLine(origin=(-0.5*_LANEWIDTH, 0, 0)))
    simulator.addLane(DashedLine(origin=(0.5*_LANEWIDTH, 0, 0)))
    
    # Add horizon
    simulator.addStaticGeometry(Cube(origin=(0,0,-200),shape=(3*_LANEWIDTH,0,0)))
    
    # Add vehicles
    simulator.addVehicle(Vehicle())
    
    simulator.run()
    simulator.exit()
    
    