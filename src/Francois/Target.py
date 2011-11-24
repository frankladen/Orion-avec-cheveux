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
        self.flag = Flag(Target([0,0,0]), Target([0,0,0]), FlagState.STANDBY)
        self.owner = owner
        self.hitpoints = 50
        self.maxHP = 50
        self.isAlive = True
        self.constructionProgress = 0
        if type <= u.Unit.GROUND_ATTACK:
            self.viewRange = u.Unit.VIEW_RANGE[type]
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
            self.name = u.Unit.NAME[u.Unit.DEFAULT]
        if type == u.Unit.LANDING_ZONE:
            self.name = u.Unit.NAME[u.Unit.DEFAULT]


    def getFlag(self):
        return self.flag

    def takeDammage(self, amount):
        self.hitpoints-=amount
        if self.hitpoints <= 0:
            return True
        else:
            return False
        
    
    def kill(self):
        self.isAlive = False        
