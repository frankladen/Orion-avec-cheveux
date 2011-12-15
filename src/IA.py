# -*- coding: UTF-8 -*-
from Unit import *
from Flag import *
from Client import *
from Player import *
import random
import socket
import time
from Building import*

class IA(Player):
    def __init__(self, name, game, id , colorId):
        Player.__init__(self, name, game, id , colorId)       
        self.frameAction = 60
        self.frameActuel = 0    
        self.priority = (4, 1, 1, 3, 11)
        self.maxUnits =(5,1,1,5,0,1)
        self.diplomacies = ['Ally','Ally','Ally','Ally','Ally','Ally','Ally','Ally']
        
    def requeteModele(self): #methode que controleur va appeler
        if self.frameActuel == self.frameAction:
            self.choixAction()
            self.frameActuel = 0
        else:
             self.frameActuel = self.frameActuel+1
        
    def action(self):
        Player.action(self)
        # si on est rendu pour faire une nouvelle action
        if self.frameActuel == self.frameAction:
            self.choixAction()
            self.frameActuel = 0
        else:
             self.frameActuel = self.frameActuel+1
             
    def trouverRessource(self):
        for i in self.game.galaxy.solarSystemList:
            for j in i.nebulas:
                if self.game.players[self.id].inViewRange(j.position) and j.gazQte > 0:
                    temp = True
                    for u in self.units:
                        if u.flag.finalTarget == j:
                            temp = False
                    if temp:
                        return j
            for j in i.asteroids:
                if self.game.players[self.id].inViewRange(j.position) and j.mineralQte > 0:
                    temp = True
                    for u in self.units:
                        if u.flag.finalTarget == j:
                            temp = False
                    if temp:
                        return j
        return None
                    
    def envoyerCargo(self,ressource):
        for i in self.units:
            if i.type == Unit.CARGO:
                if i.flag.flagState == FlagState.STANDBY:
                    i.changeFlag(ressource,FlagState.GATHER)
                    
    def explore(self):
        for i in self.units:
            if i.type == Unit.SCOUT:
                x = random.randint(1,800) - 400
                y = random.randint(1,800) - 400
                while (i.position[0]+x < (self.game.galaxy.width/2)*-1 or i.position[0]+x > self.game.galaxy.width/2):
                    x = random.randint(1,800) - 400
                while (i.position[1]+y < (self.game.galaxy.height/2)*-1 or i.position[1]+y > self.game.galaxy.height/2):
                    y = random.randint(1,800) - 400
                i.changeFlag(Target([i.position[0]+x,i.position[1]+y,0]), FlagState.MOVE)
                 
    def choixAction(self):
        r = random.randint(1,3)    
        if r == 1:
            self.explore()
        elif r == 2:
            ressource = self.trouverRessource()
            if ressource != None:
               self.envoyerCargo(ressource)
        elif r == 3:
            self.decisionBuildUnit()
        else:
            print("attaqueeeee")
          
    def decisionBuildUnit(self):
        for i in self.priority:
            if self.needBuild(i):
                if self.canAfford(Unit.BUILD_COST[i][0],Unit.BUILD_COST[i][1], Unit.BUILD_COST[i][2]):
                    b =self.getStandByBuilding(i)
                    if b != None:
                        b.addUnitToQueue(i)
    
    def haveBuilding(self, unitType):
        for i in self.buildings:
            if i.type == unitType:
                return True
        return False
    
    def needBuild(self, unitType):
        if self.nbrUnit(unitType) < self.maxUnits[self.priority.index(unitType)]:
            if unitType == Unit.TRANSPORT:
                if self.haveBuilding(Building.UTILITY):
                    return True
            if unitType == Unit.SCOUT or Unit.CARGO:
                return True #meme pour scout et les autres
        return False
            
    def getStandByBuilding(self, unitType):
        if unitType == 4 or unitType == 1:
            for i in self.motherships:
                if i.flag.flagState == FlagState.STANDBY:
                    return i 
        elif unitType == 3: #or repaire
            for i in self.buildings:
                if i.type == Building.UTILITY:
                    if i.flag.flagState  == FlagState.STANDBY:
                        return i 
            return None
    
    def nbrUnit(self,unitType):
        nbr = 0
        for i in self.units:
            if i.type == unitType:
                nbr = nbr+1  
        return nbr

    def inViewRange(self, position):
        x = position[0]
        y = position[1]
        for i in self.units:
            if i.isAlive and not isinstance(i, u.GroundUnit):
                if x > i.position[0]-i.viewRange and x < i.position[0]+i.viewRange:
                    if y > i.position[1]-i.viewRange and y < i.position[1]+i.viewRange:
                        if i.type == u.Unit.TRANSPORT:
                            if not i.landed:
                                return True
                        else:
                            return True
        for i in self.buildings:
            if i.isAlive and i.finished and not isinstance(i, b.GroundBuilding) and not isinstance(i, b.LandingZone):
                if x > i.position[0]-i.viewRange and x < i.position[0]+i.viewRange:
                    if y > i.position[1]-i.viewRange and y < i.position[1]+i.viewRange:
                        return True
        if x > self.motherShip.position[0]-self.motherShip.viewRange and x < self.motherShip.position[0]+self.motherShip.viewRange:
            if y > self.motherShip.position[1]-self.motherShip.viewRange and y < self.motherShip.position[1]+self.motherShip.viewRange:
                return True

        
        return False


# Joueur IA 1 (stupid)       
class IA1(IA): # hérite de la classe IA
    def __init__(self):
        IA.__init__(self, name, game, id , colorId)
 
 # Joueur IA 2 (smart) 
class IA1(IA): # hérite de la classe IA
    def __init__(self):
        IA.__init__(self, name, game, id , colorId)       
            
