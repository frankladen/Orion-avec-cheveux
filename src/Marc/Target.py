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
        if type <= u.Unit.GROUND_BUILDER_UNIT:
            self.viewRange = u.Unit.VIEW_RANGE[type]
            self.hitpoints = u.Unit.MAX_HP[type]
            self.maxHP=self.hitpoints
            self.buildTime = u.Unit.BUILD_TIME[type]
            self.buildCost = u.Unit.BUILD_COST[type]
        else:
            self.viewRange = u.Unit.VIEW_RANGE[u.Unit.DEFAULT]
            self.hitpoints = u.Unit.MAX_HP[u.Unit.DEFAULT]
            self.maxHP=self.hitpoints
            self.buildTime = u.Unit.BUILD_TIME[u.Unit.DEFAULT]
            self.buildCost = u.Unit.BUILD_COST[u.Unit.DEFAULT]

    def getFlag(self):
        return self.flag

    def takeDammage(self, amount, game):
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
           
class Notification(Target):
    ATTACKED_UNIT = 0
    ATTACKED_BUILDING = 1
    ALLIANCE_ALLY = 2
    ALLIANCE_ENNEMY = 3
    NAME = ("Un de vos vaisseaux se fait attaquer par ", "Un de vos bâtiments se fait attaquer par ", "Vous êtes maintenant l'allié de ", "Vous êtes maintenant l'allié de ")
    def __init__(self,position,type, actionPlayerName = None):
        self.position=position
        self.type=type
        self.refreshSeen = 60
        self.name = self.NAME[type]
        if actionPlayerName != None:
            self.name += actionPlayerName
                  
