from abc import ABC, abstractmethod

from OpenGL.GL import *
from OpenGL.GLU import *

from config import _SCALE
from config import _SPEED

class Geometry(ABC):
    def __init__(self, origin=(0,0,0), shape=(1,1,0), colour=(1,1,1), fill=False):
        self.origin = tuple([coord * _SCALE for coord in origin])
        self.shape = tuple([dim * _SCALE for dim in shape])
        self.colour = colour
        self.fill = fill
        
    def setShape(self, shape):
        self.shape = tuple([dim * _SCALE for dim in shape])
    
    # Abstract method
    def render(self):
        pass
    
    # Abstract method
    def translate(self):
        pass
    
    
class Cube(Geometry):
    def __init__(self, origin=(0,0,0), shape=(1,1,0), colour=(1,0,0), fill=False):
        super().__init__(origin, shape, colour, fill)
        self.edges = (
                        (0,1),(0,3),(0,4),
                        (2,1),(2,3),(2,7),
                        (6,3),(6,4),(6,7),
                        (5,1),(5,4),(5,7)
                    )
        self.surfaces = (
                            (0,1,2,3),
                            (3,2,7,6),
                            (6,7,5,4),
                            (4,5,1,0),
                            (1,5,7,2),
                            (4,0,3,6)
                        )
        
    def render(self):
        self.updateModel()
        glBegin(GL_LINES)
        glColor3fv(self.colour)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.vertices[vertex])
        glEnd()
        
        if self.fill:
            glBegin(GL_QUADS)
            for surface in self.surfaces:
                x = 0
                for vertex in surface:
                    x+=1
                    glVertex3fv(self.vertices[vertex])
            glEnd()
    
    # Raw translation is by real distance, not speed
    def translate(self, transform, raw=False):
        if not raw:
            transform = tuple([coord * _SPEED for coord in transform])
        else:
            transform = tuple([coord * _SCALE for coord in transform])
            
        self.origin = (
                        self.origin[0] + transform[0],
                        self.origin[1] + transform[1],
                        self.origin[2] + transform[2]
                    )
        
    def updateModel(self):
        self.vertices = (
                        (self.origin[0] + self.shape[0]/2, self.origin[1] - self.shape[1]/2, self.origin[2] - self.shape[2]/2),
                        (self.origin[0] + self.shape[0]/2, self.origin[1] + self.shape[1]/2, self.origin[2] - self.shape[2]/2),
                        (self.origin[0] - self.shape[0]/2, self.origin[1] + self.shape[1]/2, self.origin[2] - self.shape[2]/2),
                        (self.origin[0] - self.shape[0]/2, self.origin[1] - self.shape[1]/2, self.origin[2] - self.shape[2]/2),
                        (self.origin[0] + self.shape[0]/2, self.origin[1] - self.shape[1]/2, self.origin[2] + self.shape[2]/2),
                        (self.origin[0] + self.shape[0]/2, self.origin[1] + self.shape[1]/2, self.origin[2] + self.shape[2]/2),
                        (self.origin[0] - self.shape[0]/2, self.origin[1] - self.shape[1]/2, self.origin[2] + self.shape[2]/2),
                        (self.origin[0] - self.shape[0]/2, self.origin[1] + self.shape[1]/2, self.origin[2] + self.shape[2]/2)
                        )

class DashedLine(Geometry):
    def __init__(self, origin=(0,0,0), shape=(0.15,0,2), colour=(0,1,0), fill=False):
        super().__init__(origin, shape, colour, fill)
        self.dashes = []
        for z_origin in range(-1,-240,-9):
            self.dashes.append(Cube(origin=(origin[0], origin[1], z_origin), shape=shape, colour=colour))
        
    def render(self):
        for dash in self.dashes:
            dash.render()
        
    def translate(self, transform, raw=False):
        for dash in self.dashes:
            dash.translate(transform, raw)
        
        if self.dashes[0].origin[2] > 1*_SCALE:
            dash = self.dashes.pop(0)
            # Had to convert from distance to _SPEED
            #dash.translate((0,0,-15099.32))
            dash.translate((0,0,-240), True)
            self.dashes.append(dash)