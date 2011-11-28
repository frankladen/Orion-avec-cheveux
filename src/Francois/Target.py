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
        self.isAlive = True
        self.constructionProgress = 0
    def getFlag(self):
        return self.flag
    
            
    #Change le flag pour une nouvelle destination et un nouvel etat
    def changeFlag(self, finalTarget, state):
        #On doit vérifier si l'unité est encore vivante
        if self.isAlive:
            self.flag.initialTarget = t.Target([self.position[0],self.position[1],0])
            self.flag.finalTarget = finalTarget
            self.flag.flagState = state
    
    
    def takeDammage(self, amount, players):
        self.hitpoints -= amount
        if self.hitpoints <= 0:
            return True
        else:
            return False

    def isInRange(self, position, range, onPlanet = False, planetId = -1, solarSystemId = -1):
        if onPlanet == False:
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
    ALLIANCE_DEMAND_ALLY = 3
    ALLIANCE_ENNEMY = 4
    NAME = ("Un de vos vaisseaux se fait attaquer par ", "Un de vos bâtiments se fait attaquer par ", "Vous êtes maintenant allié avec ", "Vous avez reçu une demande d'alliance de ", "Vous êtes maintenant l'ennemi de ")
    COLOR = ("RED", "RED", "GREEN", "YELLOW", "RED")
    def __init__(self,position,type, actionPlayerName = None):
        self.position=position
        self.type=type
        self.refreshSeen = 60
        self.color = self.COLOR[type]
        self.name = self.NAME[type]
        if actionPlayerName != None:
            self.actionPlayerName = actionPlayerName
            self.name += actionPlayerName
                  
