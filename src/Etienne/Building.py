# -*- coding: UTF-8 -*-
import Target as t
import World as w
import Player as p

class Building(t.PlayerObject):
    WAYPOINT=0
    REFINERY=1
    BARRACK=2
    FARM=3
    
    def __init__(self, name,type, position, owner):
        t.PlayerObject.__init__(self, name,type, position, owner)
        self.buildingTimer = 0
        self.finished = False

class Waypoint(Building):
    SIZE =(30,30)
    TIME = 60
    def __init__(self, name, type, position, owner):
        Building.__init__(self, name, type, position, owner)
        
        

    
    
        
        
        
        