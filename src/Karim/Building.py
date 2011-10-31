# -*- coding: UTF-8 -*-
import Target as t
import World as w
import Player as p

class Building(t.PlayerObject):
    def __init__(self, name, position):
        t.PlayerObject.__init__(self, name, position)
    
class Builds():
    FACTORY=1
    REFINERY=2
    BARRACK=4
    FARM=8
    
        
        
        
        