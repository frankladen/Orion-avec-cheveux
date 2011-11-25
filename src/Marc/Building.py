# -*- coding: UTF-8 -*-
import Target as t
import World as w
import Player as p
import Flag as fl
from Helper import *

class Building(t.PlayerObject):
    WAYPOINT=0
    REFINERY=1
    BARRACK=2
    FARM=3
    TURRET=4
    NAME = ("Point ralliement", "Raffinerie", "Barraque", "Ferme", "Tourette")
    SIZE =((30,30),(0,0),(0,0),(75,59),(32,32))
    INSPACE = (True,False,False,False,True)
    COST = ((50,50),(0,0),(0,0),(50,50),(50,50))
    TIME = (60,0,0,75,75)
    MAX_HP = (150,0,0,200,200)
    VIEW_RANGE=(200, 0, 0, 100, 250)
    MAX_SHIELD=(0,0,0,0,0)
    
    def __init__(self,type, position, owner):
        t.PlayerObject.__init__(self, self.NAME[type], type, position, owner)
        self.buildingTimer = 0
        self.hitpoints = self.MAX_HP[type]
        self.finished = False
        self.shield = self.MAX_SHIELD[type]

    def action(self, parent):
        i=1

    def select(self, position):
        if self.isAlive:
            if self.position[0] >= position[0] - self.SIZE[self.type][0]/2 and self.position[0] <= position[0] + self.SIZE[self.type][0]/2:
                if self.position[1] >= position[1] - self.SIZE[self.type][1]/2 and self.position[1] <= position[1] + self.SIZE[self.type][1]/2:
                    return self
        return None

    def selectIcon(self, startPos, endPos):
        if self.isAlive:
            if self.position[0] > startPos[0] - self.SIZE[self.type][0]/2 and self.position[0] < endPos[0] + self.SIZE[self.type][0]/2:
                if self.position[1] > startPos[1] - self.SIZE[self.type][1]/2 and  self.position[1] < endPos[1] + self.SIZE[self.type][1]/2:
                    return self
        return None

class SpaceBuilding(Building):
    def __init__(self, type, position, owner):
        Building.__init__(self, type, position, owner)

class Waypoint(Building):
    def __init__(self, type, position, owner):
        SpaceBuilding.__init__(self, type, position, owner)
        
class Turret(Building):
    def __init__(self, type, position, owner):
        SpaceBuilding.__init__(self, type, position, owner)
        self.range=200
        self.AttackSpeed=12
        self.AttackDamage=6
        self.attackcount=self.AttackSpeed
        self.killCount = 0

    def action(self, parent):
        if self.finished:
            if self.flag.flagState == fl.FlagState.ATTACK:
                killedIndexes = self.attack(parent.game.players)
                if killedIndexes[0] > -1:
                    parent.killUnit(killedIndexes)
            else:
                parent.game.checkIfEnemyInRange(self)

    def attack(self, players, unitToAttack=None):
        if unitToAttack == None:
            unitToAttack = self.flag.finalTarget
        index = -1
        killedOwner = -1
        isBuilding = False
        distance = Helper.calcDistance(self.position[0], self.position[1], unitToAttack.position[0], unitToAttack.position[1])
        try:
            if distance <= self.range:
                self.attackcount = self.attackcount - 1
                if self.attackcount == 0:
                    if unitToAttack.takeDammage(self.AttackDamage, players):
                        if isinstance(unitToAttack, Building) == False:
                            index = players[unitToAttack.owner].units.index(unitToAttack)
                        else:
                            index = players[unitToAttack.owner].buildings.index(unitToAttack)
                            isBuilding = True
                        killedOwner = unitToAttack.owner
                        for i in players[self.owner].units:
                            if i.isAlive:
                                if i.flag.finalTarget == unitToAttack:
                                    i.flag = fl.Flag(t.Target(i.position), t.Target(i.position), fl.FlagState.STANDBY)
                                    i.attackcount=i.AttackSpeed
                        self.killCount +=1
                    self.attackcount=self.AttackSpeed
            else:
                self.flag = fl.Flag(t.Target(self.position), t.Target(self.position), fl.FlagState.STANDBY)
            return (index, killedOwner, isBuilding)
        except ValueError:
            self.flag = fl.Flag(t.Target(self.position), t.Target(self.position), fl.FlagState.STANDBY)
            return (-1, -1, isBuilding)

    #Change le flag pour une nouvelle destination et un nouvel etat
    def changeFlag(self, finalTarget, state):
        #On doit vérifier si l'unité est encore vivante
        if self.isAlive:
            self.flag.initialTarget = t.Target([self.position[0],self.position[1],0])
            self.flag.finalTarget = finalTarget
            self.flag.flagState = state

class GroundBuilding(Building):
    def __init__(self, type, position, owner, sunId, planetId):
        Building.__init__(self, type, position, owner)
        self.sunId = sunId
        self.planetId = planetId

class Farm(Building):
    def __init__(self, type, position, owner, sunId, planetId):
        GroundBuilding.__init__(self, type, position, owner, sunId, planetId)
        
        
        
