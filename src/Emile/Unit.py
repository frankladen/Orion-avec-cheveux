# -*- coding: UTF-8 -*-
import Target as t
import  Flag
import FlagState as fs
import Helper as h
from time import sleep

class Unit(t.PlayerObject):
    def __init__(self, name, position, flag=Flag.Flag(t.Target([0,0,0]),t.Target([0,0,0]),fs.FlagState.STANDBY), foodcost=50, movespeed=1.0):
        t.PlayerObject.__init__(self, name, flag, position)
        self.FoodCost=foodcost
        self.MoveSpeed=movespeed
        
    def move(self):
        #while self.flag.flagState != fs.FlagState.STANDBY:
        if h.Helper.calcDistance(self.position[0], self.position[1], self.flag.finalTarget.position[0], self.flag.finalTarget.position[1]) <= self.MoveSpeed:
            self.position = self.flag.finalTarget.position
            self.flag.flagState = fs.FlagState.STANDBY
            print(self.position)
        else:
            angle = h.Helper.calcAngle(self.position[0], self.position[1], self.flag.finalTarget.position[0], self.flag.finalTarget.position[1])
            temp = h.Helper.getAngledPoint(angle, self.MoveSpeed, self.position[0], self.position[1])
            self.position[0] = temp[0]
            self.position[1] = temp[1]
            #print (self.position)
    
    def changeFlag(self, finalTarget, state):
        self.flag.initialTarget = self.position
        self.flag.finalTarget = finalTarget
        self.flag.flagState = state
        
#        if self.flag.flagState == fs.FlagState.STANDBY:
#            self.flag.finalTarget = self.flag.initialTarget
#        elif self.flag.flagState == fs.FlagState.MOVE:
#            self.move()
#        elif self.flag.flagState == fs.FlagState.PATROL:
#            print("Patrol")
#        elif self.flag.flagState == fs.FlagState.ATTACK:
#            print("Attack")
#        elif self.flag.flagState == fs.FlagState.ATTACK + FlagState.MOVE:
#            print("Attack + move")
#        elif self.flag.flagState == fs.FlagState.GATHER:
#            print("Gather")
#        elif self.flag.flagState == fs.FlagState.BUILD:
#            print("Build")
#        elif self.flag.flagState == fs.FlagState.REPAIR:
#            print("Repair")
#        elif self.flag.flagState == fs.FlagState.RESEARCH:
#            print("Research")
              
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

        
        
    