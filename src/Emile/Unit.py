# -*- coding: UTF-8 -*-
import Target as t
import  Flag
import FlagState as fs
import Helper as h
from time import sleep

class Unit(t.PlayerObject):
    def __init__(self, name, position, foodcost=50, moveSpeed=1.0):
        t.PlayerObject.__init__(self, name, position)
        self.FoodCost=foodcost
        self.moveSpeed=moveSpeed
        
    def move(self):
        if h.Helper.calcDistance(self.position[0], self.position[1], self.flag.finalTarget.position[0], self.flag.finalTarget.position[1]) <= self.moveSpeed:
            self.position = self.flag.finalTarget.position
            self.flag.flagState = fs.FlagState.STANDBY
            print(self.position)
        else:
            angle = h.Helper.calcAngle(self.position[0], self.position[1], self.flag.finalTarget.position[0], self.flag.finalTarget.position[1])
            temp = h.Helper.getAngledPoint(angle, self.moveSpeed, self.position[0], self.position[1])
            self.position[0] = temp[0]
            self.position[1] = temp[1]
    
    def changeFlag(self, finalTarget, state):
        self.flag.initialTarget = self.position
        self.flag.finalTarget = finalTarget
        self.flag.flagState = state
              
class SpaceUnit(Unit):
    def __init__(self):
        Unit.__init__(self)

class GroundUnit(Unit):
    def __init__(self,planetid):
        Unit.__init__(self, planetid)
        self.Planetid=planetid
        
    
class GroundAttackUnit(GroundUnit):
    def __init__(self,attackspeed,attackdamage):
        super(GroundAttackUnit,self).__init__()
        self.AttackSpeed=attackspeed
        self.AttackDamage=attackdamage
    
        
class GroundBuildUnit(GroundUnit):
    def __init__(self):
        super(GroundBuildUnit,self).__init__()
    
    def build(self,building):
        print("build")

        
        
    