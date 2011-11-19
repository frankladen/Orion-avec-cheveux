# -*- coding: UTF-8 -*-
import Target as t
import World as w
import Player as p

class Building(t.PlayerObject):
    WAYPOINT=0
    REFINERY=1
    BARRACK=2
    FARM=3
    TURRET=4
    SIZE =((30,30),(0,0),(0,0),(0,0),(0,0))
    TIME = (60,0,0,0,0)
    MAX_HP = (150,0,0,0,0)
    VIEW_RANGE=(150, 0, 0, 0, 0)
    
    def __init__(self, name,type, position, owner):
        t.PlayerObject.__init__(self, name,type, position, owner)
        self.buildingTimer = 0
        self.hitpoints = self.MAX_HP[type]
        self.finished = False

    def select(self, position):
        if self.isAlive:
            if self.position[0] >= position[0] - self.SIZE[self.type][0]/2 and self.position[0] <= position[0] + self.SIZE[self.type][0]/2:
                if self.position[1] >= position[1] - self.SIZE[self.type][1]/2 and self.position[1] <= position[1] + self.SIZE[self.type][1]/2:
                    return self
        return None

class Waypoint(Building):
    def __init__(self, name, type, position, owner):
        Building.__init__(self, name, type, position, owner)
        
        

    
    
        
        
        
        
