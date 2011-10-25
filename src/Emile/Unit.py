# -*- coding: UTF-8 -*-
import Target as t
from Flag import *
import Helper as h
import math

#Classe representant une unit
class Unit(t.PlayerObject):
    def __init__(self, name, position, owner, foodcost=50, moveSpeed=1.0):
        t.PlayerObject.__init__(self, name, position, owner)
        self.FoodCost=foodcost
        self.moveSpeed=moveSpeed
        
    #La deplace d'un pas vers son flag et si elle est rendu, elle change arrete de bouger    
    def move(self):
        if h.Helper.calcDistance(self.position[0], self.position[1], self.flag.finalTarget.position[0], self.flag.finalTarget.position[1]) <= self.moveSpeed:
            endPos = [self.flag.finalTarget.position[0],self.flag.finalTarget.position[1]]
            self.position = endPos
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
    def __init__(self, name, position, owner, movespeed):
        Unit.__init__(self, name, position, owner, movespeed)

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
        
class SpaceAttackUnit(SpaceUnit):
    def __init__(self, name, position, owner, moveSpeed, attackspeed,attackdamage,range):
        SpaceUnit.__init__(self, name, position, owner, moveSpeed)
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

class TransportShip(SpaceUnit):
    def __init__(self, name, position, owner, moveSpeed):
        SpaceUnit.__init__(self, name, position, owner, moveSpeed)
        self.landed = False
        self.capacity = 10
        self.units = []

    def land(self, controller, playerId):
        planet = self.flag.finalTarget
        self.arrived = True
        if self.position[0] < planet.position[0] or self.position[0] > planet.position[0]:
            if self.position[1] < planet.position[1] or self.position[1] > planet.position[1]:
                self.arrived = False
                self.move()
        if self.arrived:
            player = controller.players[playerId]
            player.currentPlanet = planet
            alreadyLanded = False
            for i in planet.landingZones:
                if i.ownerId == playerId:
                    alreadyLanded = True
            if not alreadyLanded:
                planet.addLandingZone(playerId, self)
                self.landed = True
                if self in controller.players[controller.playerId].selectedObjects:
                    controller.players[controller.playerId].selectedObjects.pop(controller.players[controller.playerId].selectedObjects.index(self))
            if playerId == controller.playerId:
                controller.view.changeBackground('PLANET')
                controller.view.drawPlanetGround(planet)
            self.flag = Flag (self.position, self.position, FlagState.STANDBY)
        
