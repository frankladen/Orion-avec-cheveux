# -*- coding: UTF-8 -*-
import Building

class WayPoint(Building):
    def __init__(self, name, position):
        super(WayPoint, self)
        #Verifier plus tard si le nom du building entr� est "wayPoint"
        self.name = name
        self.position = position
        
    def checkSpaceVacant(self,x, y, z=0, players, galaxie):