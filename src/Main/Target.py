# -*- coding: UTF-8 -*-
from Flag import *
import Unit as u

#Represente une position dans l'espace  
class Target():
    def __init__(self, position=[0,0,0]):
        self.position = position

#Represente un objet pouvant appartenir a un joueur
class PlayerObject(Target):
    def __init__(self, name, type, position, owner):
        Target.__init__(self, position)
        self.name = name
        self.type = type
        self.flag = Flag(Target([0,0,0]), Target([0,0,0]), FlagState.STANDBY)
        self.owner = owner
        self.hitpoints = 50
        self.maxHP = 50
        self.isAlive = True
        self.constructionProgress = 0
        if type <= u.Unit.CARGO:
            self.viewRange = u.Unit.VIEW_RANGE[type]
            self.hitpoints = u.Unit.MAX_HP[type]
            self.maxHP=self.hitpoints
            self.buildTime = u.Unit.BUILD_TIME[type]
            self.buildCost = u.Unit.BUILD_COST[type]
##        if type == u.Unit.SCOUT:
##            self.viewRange = u.Unit.VIEW_RANGE[type]
##            self.hitpoints = u.Unit.MAX_HP[type]
##            self.maxHP=self.hitpoints
##            self.buildTime = u.Unit.BUILD_TIME[type]
##            self.buildCost = u.Unit.BUILD_COST[type]
##        elif type == u.Unit.MOTHERSHIP:
##            self.viewRange = u.Unit.VIEW_RANGE[type]
##            self.hitpoints = u.Unit.MAX_HP[type]
##            self.maxHP=self.hitpoints
##            self.buildTime = u.Unit.BUILD_TIME[type]
##            self.buildCost = u.Unit.BUILD_COST[type]
##        elif type == u.Unit.ATTACK_SHIP:
##            self.hitpoints = u.Unit.MAX_HP[type]
##            self.maxHP=self.hitpoints
##            self.viewRange = u.Unit.VIEW_RANGE[type]
##            self.buildTime = u.Unit.BUILD_TIME[type]
##        elif type == u.Unit.CARGO:
##            self.viewRange = u.Unit.VIEW_RANGE[type]
##            self.buildTime = u.Unit.BUILD_TIME[type]
##            self.hitpoints = u.Unit.MAX_HP[type]
##            self.maxHP=self.hitpoints
##        elif type == u.Unit.TRANSPORT:
##            self.viewRange = u.Unit.VIEW_RANGE[type]
##            self.buildTime = u.Unit.BUILD_TIME[type]
##            self.hitpoints = u.Unit.MAX_HP[type]
##            self.maxHP=self.hitpoints
        else:
            self.viewRange = u.Unit.VIEW_RANGE[u.Unit.DEFAULT]
            self.hitpoints = u.Unit.MAX_HP[u.Unit.DEFAULT]
            self.maxHP=self.hitpoints
            self.buildTime = u.Unit.BUILD_TIME[u.Unit.DEFAULT]
            self.buildCost = u.Unit.BUILD_COST[u.Unit.DEFAULT]

    def getFlag(self):
        return self.flag
    
    def kill(self):
        self.isAlive = False        
