# -*- coding: UTF-8 -*-
from Flag import *
import Unit as u

#Represente une position dans l'espace  
class Target():
    def __init__(self, position=[0,0,0]):
        self.position = position

#Represente un objet pouvant appartenir a un joueur
class PlayerObject(Target):
    def __init__(self, type, position, owner):
        Target.__init__(self, position)
        self.type = type
        print (type)
        self.flag = Flag(Target([0,0,0]), Target([0,0,0]), FlagState.STANDBY)
        self.owner = owner
        self.isAlive = True
        self.constructionProgress = 0
        if isinstance(self, u.Unit):
            if type <= u.Unit.GROUND_BUILDER_UNIT:
                self.viewRange = self.VIEW_RANGE[type]
                self.hitpoints = u.Unit.MAX_HP[type]
                self.maxHP=self.hitpoints
                self.buildTime = u.Unit.BUILD_TIME[type]
                self.buildCost = u.Unit.BUILD_COST[type]
                self.name = u.Unit.NAME[type]
            else:
                self.viewRange = u.Unit.VIEW_RANGE[u.Unit.DEFAULT]
                self.hitpoints = u.Unit.MAX_HP[u.Unit.DEFAULT]
                self.maxHP=self.hitpoints
                self.buildTime = u.Unit.BUILD_TIME[u.Unit.DEFAULT]
                self.buildCost = u.Unit.BUILD_COST[u.Unit.DEFAULT]
            


    def getFlag(self):
        return self.flag
    
            
    #Change le flag pour une nouvelle destination et un nouvel etat
    def changeFlag(self, finalTarget, state):
        #On doit vérifier si l'unité est encore vivante
        if self.isAlive:
            self.flag.initialTarget = t.Target([self.position[0],self.position[1],0])
            self.flag.finalTarget = finalTarget
            self.flag.flagState = state
    
    
    def takeDammage(self, amount):
        self.hitpoints -= amount
        if self.hitpoints <= 0:
            return True
        else:
            return False

    def isInRange(self, position, range, onPlanet = False, planetId = -1, solarSystemId = -1):
        if self.position[0] > position[0]-range and self.position[0] < position[0]+range:
            if self.position[1] > position[1]-range and self.position[1] < position[1]+range:
                return self
        return None
    
    def kill(self):
        self.isAlive = False        
