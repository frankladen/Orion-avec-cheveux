# -*- coding: UTF-8 -*-
import Target as t
from Flag import *
from Constants import *
import Helper as h
import math

#Classe representant une unit
class Unit(t.PlayerObject):
    def __init__(self, name, position, owner, foodcost=50, moveSpeed=1.0):
        t.PlayerObject.__init__(self, name, position, owner)
        self.FoodCost=foodcost
        if (name == UnitType.SCOUT):
            self.moveSpeed= MoveSpeed.SCOUT
        elif(name == UnitType.SPACE_ATTACK_UNIT):
            self.moveSpeed = MoveSpeed.SPACE_ATTACK_UNIT
        elif(name == UnitType.MOTHERSHIP):
            self.moveSpeed = MoveSpeed.MOTHERSHIP
        
    #La deplace d'un pas vers son flag et si elle est rendu, elle change arrete de bouger    
    def move(self):
        if h.Helper.calcDistance(self.position[0], self.position[1], self.flag.finalTarget.position[0], self.flag.finalTarget.position[1]) <= self.moveSpeed:
            self.position = self.flag.finalTarget.position
            if self.flag.flagState == FlagState.MOVE:
                self.flag.flagState = FlagState.STANDBY
            elif self.flag.flagState == FlagState.MOVE+FlagState.ATTACK:
                self.flag.flagState = FlagState.ATTACK
        else:
            angle = h.Helper.calcAngle(self.position[0], self.position[1], self.flag.finalTarget.position[0], self.flag.finalTarget.position[1])
            temp = h.Helper.getAngledPoint(angle, self.moveSpeed, self.position[0], self.position[1])
            self.position[0] = temp[0]
            self.position[1] = temp[1]
            
    #Efface la unit
    def eraseUnit(self):
        self.flag.flagState = 0
        self.position = [-1500,-1500,0]
        
    #Change le flag pour une nouvelle destination et un nouvel etat
    def changeFlag(self, finalTarget, state):
        #On doit vérifier si l'unité est encore vivante
        if self.isAlive:
            self.flag.initialTarget = t.Target(self.position)
            self.flag.finalTarget = finalTarget
            self.flag.flagState = state
            
    #Retourne le flag de la unit    
    def getFlag(self):
        return self.flag
              
class SpaceUnit(Unit):
    def __init__(self, name, position, owner):
        Unit.__init__(self, name, position, owner)

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

class Mothership(Unit):
    def __init__(self, name, position, owner):
        Unit.__init__(self, name, position, owner, foodcost=0, moveSpeed=0)
        self.flag.finalTarget = t.Target(position)
        self.unitBeingConstruct = []
        
    
    def progressUnitsConstruction(self):
        if len(self.unitBeingConstruct) > 0:
            self.unitBeingConstruct[0].constructionProgress = self.unitBeingConstruct[0].constructionProgress + 1

    def isUnitFinished(self):

        if len(self.unitBeingConstruct) > 0:
            return self.unitBeingConstruct[0].constructionProgress >= self.unitBeingConstruct[0].buildTime

            
        
        

        
class SpaceAttackUnit(SpaceUnit):
    def __init__(self, name, position, owner, attackspeed, attackdamage,range):
        SpaceUnit.__init__(self, name, position, owner)
        self.AttackSpeed=attackspeed
        self.AttackDamage=attackdamage
        self.range=range
        self.attackcount=self.AttackSpeed
        self.killCount = 0
        
    def attack(self, players):
        index = -1
        killedOwner = -1
        distance = h.Helper.calcDistance(self.position[0], self.position[1], self.flag.finalTarget.position[0], self.flag.finalTarget.position[1])
        if distance > self.range :
            self.attackcount=self.AttackSpeed
            self.move()
        else:
            self.attackcount = self.attackcount - 1
            if self.attackcount == 0:
                self.flag.finalTarget.hitpoints-=self.AttackDamage
                if self.flag.finalTarget.hitpoints <= 0:
                    index = players[self.flag.finalTarget.owner].units.index(self.flag.finalTarget)
                    killedOwner = self.flag.finalTarget.owner
                    self.flag = Flag(self.position, self.position, FlagState.STANDBY)
                    self.killCount +=1
                self.attackcount=self.AttackSpeed
        return (index, killedOwner)
