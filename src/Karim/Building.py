# -*- coding: UTF-8 -*-
import Target as t

class Building(t.PlayerObject):
    def __init__(self, name, position):
        t.PlayerObject.__init__(self, name, position)
        
    