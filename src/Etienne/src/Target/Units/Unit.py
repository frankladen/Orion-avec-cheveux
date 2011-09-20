# -*- coding: UTF-8 -*-
from Target.Target import PlayerObject,Target
from Target.Flag import  Flag
from Utilities.FlagState import FlagState

X = 0
#Y = 1
#Z = 2

class Unit(PlayerObject):
    def __init__(self, name, flag=Flag(Target([0,0,0]),Target([0,0,0]),FlagState.STANDBY), foodcost=50, movespeed=1.0, position=[0,0,0]):
        super(Unit,self).__init__(name, flag, position)
        self.FoodCost=foodcost
        self.MoveSpeed=movespeed
        
    def move(self):
        print("move")
        while self.flag.flagState == FlagState.MOVE and self.position != self.flag.finalTarget.position:
            if self.position[0] < self.flag.finalTarget.position[0] and self.position[1] < self.flag.finalTarget.position[1]:
                self.position[0] +=1
                self.position[1] +=1
                print(self.position[0]) 
            if self.position[1] < self.flag.finalTarget.position[1]:
                self.position[1] +=1
                print(self.position[1])
            if self.position[0] > self.flag.finalTarget.position[0]:
                self.position[0] -=1
                print(self.position[0])
            if self.position[1] > self.flag.finalTarget.position[1]:
                self.position[1] -=1
                print(self.position[1])
            print("avance")
            
            
        
class SpaceUnit(Unit):
    def __init__(self):
        super(SpaceUnit,self).__init__()

class GroundUnit(Unit):
    def __init__(self,planetid):
        super(GroundUnit,self).__init__()
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
        
unit = Unit("Bob")
unit.flag.finalTarget = Target([15,33,0])
unit.flag.flagState = FlagState.MOVE
unit.move()

        
        
    