# -*- coding: UTF-8 -*-
import Target as t
import World as w
import Player as p

class Building(t.PlayerObject):
    WAYPOINT=10
    REFINERY=11
    BARRACK=12
    FARM=13
    TURRET=14
    SIZE =((30,30),(0,0),(0,0),(0,0),(0,0))
    TIME = (60,0,0,0,0)
    MAX_HP = (150,0,0,0,0)
    VIEW_RANGE=(150, 0, 0, 0, 0)
    
    def __init__(self, name,type, position, owner):
        t.PlayerObject.__init__(self, name,type, position, owner)
        self.buildingTimer = 0
        self.hitpoints = self.MAX_HP[type]
        self.finished = False

class Waypoint(Building):
    def __init__(self, name, type, position, owner):
        Building.__init__(self, name, type, position, owner)
        
        

    
    
        
        
        
        
