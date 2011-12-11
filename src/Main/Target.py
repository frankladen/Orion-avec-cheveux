# -*- coding: UTF-8 -*-
from Flag import *
import Unit as u
from Helper import *

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

class Bullet(PlayerObject):
    def __init__(self, position, owner, unitId):
        PlayerObject.__init__(self, 666, position, owner)
        self.range = 100
        self.moveSpeed = 7.0
        self.AttackDamage = 50.0
        self.unitId = unitId
        self.arrived = False
        self.toShow = 10

    def action(self, player):
        distance = Helper.calcDistance(self.position[0], self.position[1], self.flag.finalTarget.position[0], self.flag.finalTarget.position[1])
        if not self.arrived:
            if distance > 1:
                self.move()
            else:
                isBuilding = False
                players = player.game.players
                unitsToAttack = player.game.hasUnitInRange(self)
                for un in unitsToAttack:
                    damageToTake = self.AttackDamage-(Helper.calcDistance(self.position[0], self.position[1], un.position[0], un.position[1])/2)
                    if damageToTake < 0:
                        damageToTake = 0
                    if un.takeDammage(damageToTake, players):
                        if isinstance(un, u.Unit):
                            index = players[un.owner].units.index(un)
                        else:
                            index = players[un.owner].buildings.index(un)
                            isBuilding = True
                        killedOwner = un.owner
                        player.units[self.unitId].killCount +=1
                        if player.units[self.unitId].killCount % 4 == 1:
                            self.AttackDamage += 1
                        player.killUnit((index,killedOwner,isBuilding))
                self.arrived = True


    #La deplace d'un pas vers son flag et si elle est rendu, elle change arrete de bouger    
    def move(self):
        if Helper.calcDistance(self.position[0], self.position[1], self.flag.finalTarget.position[0], self.flag.finalTarget.position[1]) <= self.moveSpeed:
            endPos = [self.flag.finalTarget.position[0],self.flag.finalTarget.position[1]]
            self.position = endPos
        else:
            angle = Helper.calcAngle(self.position[0], self.position[1], self.flag.finalTarget.position[0], self.flag.finalTarget.position[1])
            temp = Helper.getAngledPoint(angle, self.moveSpeed, self.position[0], self.position[1])
            self.position[0] = temp[0]
            self.position[1] = temp[1]
        
           
class Notification(Target):
    ATTACKED_UNIT = 0
    ATTACKED_BUILDING = 1
    ALLIANCE_ALLY = 2
    ALLIANCE_DEMAND_ALLY = 3
    ALLIANCE_ENNEMY = 4
    MESSAGE_ALLIES = 5
    MESSAGE_ALL = 6
    LAND_PLANET = 7
    FINISHED_BUILD = 8
    FINISH_GATHER = 9
    FINISH_TECH = 10
    NOT_ENOUGH_RESSOURCES = 11
    PING = 12
    NOT_ENOUGH_POPULATION = 13
    NAME = ("Un de vos vaisseaux se fait attaquer par ", "Un de vos bâtiments se fait attaquer par ", "Vous êtes maintenant allié avec ", "Vous avez reçu une demande d'alliance de ", "Vous êtes maintenant l'ennemi de ","","", "Votre planète est maintenant aussi habitée par ", "Une nouvelle unité a été créée: ", "Une de vos unités a fini de collecter", "Une nouvelle technologie vient d'être terminée : ", "Vous manquez de ressources.", "Vous êtes demandé à cet endroit par : ", "La population maximale a été atteinte.")
    COLOR = ("RED", "RED", "GREEN", "YELLOW", "RED","GREEN","CYAN", "GRAY", "WHITE","WHITE","WHITE","WHITE", "YELLOW", "WHITE")
    def __init__(self,position,type, actionPlayerName = None):
        Target.__init__(self, position)
        self.type=type
        self.refreshSeen = 0
        self.color = self.COLOR[type]
        self.name = self.NAME[type]
        if actionPlayerName != None:
            self.actionPlayerName = actionPlayerName
            self.name += actionPlayerName
                  
