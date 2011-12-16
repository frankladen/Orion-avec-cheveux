# -*- coding: UTF-8 -*-
from Unit import *
from Flag import *
from Client import *
from Player import *
import random
import socket
import time
from Building import*
from Helper import *

class IA(Player):
    def __init__(self, name, game, id , colorId):
        Player.__init__(self, name, game, id , colorId)       
        self.frameAction = 60
        self.frameActuel = 0    
        self.priority = (4, 1, 1, 3, 11)
        self.maxUnits =(5,1,1,5,0,1)
        self.buildingsPriority = (1,2,4,7)
        self.maxBuildings = (1,1,3,1)
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
        r = random.randint(1,4)    
        if r == 1:
            self.explore()
        elif r == 2:
            ressource = self.trouverRessource()
            if ressource != None:
               self.envoyerCargo(ressource)
        elif r == 3:
            self.decisionBuildUnit()
        else:
            self.checkIfEnemyInRange()
          
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
                else:
                    self.buildBuilding(Building.UTILITY)
            elif unitType == Unit.ATTACK_SHIP or Unit.SPACE_BUILDING_ATTACK:
                if self.haveBuilding(Building.BARRACK):
                    return True
                else:
                    self.buildBuilding(Building.BARRACK)
            elif unitType == Unit.SCOUT or Unit.CARGO:
                return True #meme pour scout et les autres
        return False

    def buildBuilding(self, buildingType):
        if self.canAfford(Building.COST[buildingType][0],Building.COST[buildingType][0],0):
            scout = self.getNearestScoutFromMothership()
            if scout != None:
                if Building.INSPACE[buildingType]:
                    positionBuilding = self.getPositionBuild(buildingType)
                    self.game.buildBuilding(self.id, positionBuilding, FlagState.BUILD, [str(self.units.index(scout))], buildingType)
                elif len(self.planets) > 0:
                    planet = self.planets[0]
                    positionBuilding = self.getGroundPositionBuild(buildingType, planet.id, planet.solarSystem.sunId)
                    self.game.buildBuilding(self.id, positionBuilding, FlagState.BUILD, [str(self.units.index(scout))], buildingType, planet.id, planet.solarSystem.sunId)

    def getNearestScoutFromMothership(self):
        distance = 89374
        scout = None
        for un in self.units:
            if un.type == Unit.SCOUT:
                if un.flag.flagState != FlagState.BUILD:
                    undist = Helper.calcDistance(un.position[0],un.position[1],self.motherships[0].position[0],self.motherships[0].position[1])
                    if undist < distance:
                        distance = undist
                        scout = un
        return scout

    def checkIfEnemyInRange(self):
        unit = self.getNearestScoutFromMothership()
        for pl in self.players:
            if pl.isAlive:
                if pl.id != unit.owner and self.players[unit.owner].isAlly(pl.id) == False:
                    enemyUnit = pl.hasUnitInRange(unit.position, unit.range, onPlanet, planetId, solarSystemId)
                    if enemyUnit != None:
                        attackShip = self.getFirstAttackShipStandBy(enemyUnit.position)
                        if attackShip != None:
                            self.game.makeUnitsAttack(self.id, [str(self.units.index(attackShip))],enemyUnit.owner,self.game.players[enemyUnit.owner].units.index(enemyUnit), "u")

    def getFirstAttackShipStandBy(self, enemyPosition):
        distance = 985943
        attack = None
        for un in self.units:
            if un.type in (un.ATTACK_SHIP,un.SPACE_ATTACK_BUILDING):
                if un.flag.flagState != FlagState.ATTACK:
                    atdist = Helper.calcDistance(un.position[0],un.position[1],enemyPosition[0],enemyPosition[1])
                    if atdist < distance:
                        distance = atdist
                        attack = un
        return attack
    
    def getPositionBuild(self, buildType):
        modoPoso = self.motherships[0].position
        x = random.randint(int(modoPoso[0])-500,int(modoPoso[0])+500)
        y = random.randint(int(modoPoso[1])-500,int(modoPoso[1])+500)
        if x < 0:
            x = Building.SIZE[buildType][0]
        elif x > self.game.galaxy.width:
            x = self.game.galaxy.width - Building.SIZE[buildType][0]
        if y < 0:
            y = Building.SIZE[buildType][1]
        elif y > self.game.galaxy.height:
            y = self.game.galaxy.height - Building.SIZE[buildType][1]
        return (x,y,0)
            
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
            
