# -*- coding: UTF-8 -*-
import Target as t
from Flag import *
from World import *
import Helper as h
import math

#Classe representant une unit
class Unit(t.PlayerObject):
    def __init__(self, name, position, owner, foodcost=50, moveSpeed=1.0):
        t.PlayerObject.__init__(self, name, position, owner)
        self.FoodCost=foodcost
        self.mineralCost = 30
        self.gazCost = 30
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
        self.flag.finalTarget = t.Target(position)
        self.unitBeingConstruct = []
        self.rallyPoint = [0,0,0]
        self.ownerId = owner

    def action(self):
        p = [self.position[0], self.position[1], 0]
        if (self.flag.flagState == FlagState.CREATE):
            if self.flag.finalTarget == UnitType.SCOUT:
                self.unitBeingConstruct.append(Unit(self.flag.finalTarget,p,self.ownerId, moveSpeed = MoveSpeed.SCOUT))
            elif self.flag.finalTarget == UnitType.SPACE_ATTACK_UNIT:
                self.unitBeingConstruct.append(SpaceAttackUnit(self.flag.finalTarget, p, self.ownerId, moveSpeed = 2.0, attackspeed = 10.0, attackdamage = 5.0, range = 150.0))
            elif self.flag.finalTarget == UnitType.GATHER:
                self.unitBeingConstruct.append(GatherShip(self.flag.finalTarget,p, self.ownerId, moveSpeed=3.0))
            elif self.flag.finalTarget == UnitType.TRANSPORT:
                self.unitBeingConstruct.append(TransportShip(self.flag.finalTarget,p,self.ownerId, moveSpeed=3.0))
        
        
        elif self.flag.flagState == FlagState.BUILD_UNIT:
            self.progressUnitsConstruction()
        
        elif self.flag.flagState == FlagState.CANCEL_UNIT:
            self.unitBeingConstruct.pop(int(self.flag.finalTarget))
            self.flag.flagState = FlagState.BUILD_UNIT
        
        elif self.flag.flagState == FlagState.CHANGE_RALLY_POINT:
            target = self.flag.finalTarget
            target = target.strip("[")
            target = target.strip("]")
            target = target.split(",")
            for i in range(0, len(target)):
                target[i]=math.trunc(float(target[i])) 
            self.rallyPoint = target

    def progressUnitsConstruction(self):
        if len(self.unitBeingConstruct) > 0:
            self.flag.flagState = FlagState.BUILD_UNIT
            self.unitBeingConstruct[0].constructionProgress = self.unitBeingConstruct[0].constructionProgress + 1
        else:
            self.flag.flagState = FlagState.STANDBY


    def isUnitFinished(self):
        if len(self.unitBeingConstruct) > 0:
            return self.unitBeingConstruct[0].constructionProgress >= self.unitBeingConstruct[0].buildTime
class SpaceAttackUnit(SpaceUnit):
    def __init__(self, name, position, owner, moveSpeed, attackspeed,attackdamage,range):
        SpaceUnit.__init__(self, name, position, owner, moveSpeed)
        self.AttackSpeed=attackspeed
        self.AttackDamage=attackdamage
        self.range=range
        self.attackcount=self.AttackSpeed
        self.mineralCost = 50
        self.gazCost = 50
        self.killCount = 0
        
    def attack(self, players):
        index = -1
        killedOwner = -1
        distance = h.Helper.calcDistance(self.position[0], self.position[1], self.flag.finalTarget.position[0], self.flag.finalTarget.position[1])
        try:
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
        except ValueError:
            self.flag = Flag(self.position, self.position, FlagState.STANDBY)
            return (-1, -1)

class TransportShip(SpaceUnit):
    def __init__(self, name, position, owner, moveSpeed):
        SpaceUnit.__init__(self, name, position, owner, moveSpeed)
        self.landed = False
        self.capacity = 10
        self.mineralCost = 75
        self.gazCost = 25
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
        
class GatherShip(SpaceUnit):
    GATHERTIME=20
    def __init__(self, name, position, owner, moveSpeed):
        SpaceUnit.__init__(self, name, position, owner, moveSpeed)
        self.maxGather = 50
        self.gatherSpeed = 20
        self.mineralCost = 25
        self.gazCost = 75 
        self.container = [0,0]
        self.returning = False

    def gather(self, player):
        ressource = self.flag.finalTarget
        arrived = True
        if isinstance(self.flag.finalTarget, AstronomicalObject):
            if self.position[0] < ressource.position[0] or self.position[0] > ressource.position[0]:
                if self.position[1] < ressource.position[1] or self.position[1] > ressource.position[1]:
                    arrived = False
                    self.move()
            if arrived:
                if self.gatherSpeed==0:
                    if ressource.type=='asteroid':
                        if self.container[0] < self.maxGather:
                            if ressource.mineralQte >= 5:
                                self.container[0]+=5
                                ressource.mineralQte-=5
                            else:
                                self.container[0]+=ressource.mineralQte
                                ressource.mineralQte = 0
                                self.flag.intialTarget = self.flag.finalTarget
                                self.flag.finalTarget = player.motherShip
                            self.gatherSpeed = 20
                        else:
                            self.flag.intialTarget = self.flag.finalTarget
                            self.flag.finalTarget = player.motherShip
                    else:
                        if self.container[1]<self.maxGather:
                            if ressource.gazQte >= 5:
                                self.container[1]+=5
                                ressource.gazQte-=5
                            else:
                                self.container[1]+=ressource.gazQte
                                ressource.gazQte = 0
                                self.flag.intialTarget = self.flag.finalTarget
                                self.flag.finalTarget = player.motherShip
                            self.gatherSpeed = 20
                        else:
                            self.flag.intialTarget = self.flag.finalTarget
                            self.flag.finalTarget = player.motherShip
                else:
                    self.gatherSpeed-=1
        else:
            if self.position[0] < ressource.position[0] or self.position[0] > ressource.position[0]:
                if self.position[1] < ressource.position[1] or self.position[1] > ressource.position[1]:
                    arrived = False
                    self.move()
            if arrived:
                player.mineral += self.container[0]
                player.gaz += self.container[1]
                self.container[0] = 0
                self.container[1] = 0
                self.flag.finalTarget = self.flag.intialTarget
                if self.flag.finalTarget.type == 'asteroid':
                    if self.flag.finalTarget.mineralQte == 0:
                        self.flag.flagState = FlagState.STANDBY
                else:
                    if self.flag.finalTarget.gazQte == 0:
                        self.flag.flagState = FlagState.STANDBY
 
