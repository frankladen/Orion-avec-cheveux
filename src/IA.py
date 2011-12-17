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
        self.priority = (1,4,3,2,11)
        self.maxUnits =(1,5,1,4,2)
        self.enemyDiscovered = []
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
        sentOne = False
        for i in self.units:
            if i.isAlive:
                if i.type == Unit.CARGO:
                    if i.flag.flagState == FlagState.STANDBY:
                        i.changeFlag(ressource,FlagState.GATHER)
                        sentOne = True
        return sentOne
                    
    def explore(self, moveRange):
        for i in self.units:
            if i.isAlive:
                if i.type == Unit.SCOUT:
                    if i.flag.flagState != FlagState.BUILD:
                        x = random.randint(-1*(moveRange),moveRange)
                        y = random.randint(-1*(moveRange),moveRange)
                        while (i.position[0]+x < (self.game.galaxy.width/2)*-1 or i.position[0]+x > self.game.galaxy.width/2):
                            x = random.randint(-1*(moveRange),moveRange)
                        while (i.position[1]+y < (self.game.galaxy.height/2)*-1 or i.position[1]+y > self.game.galaxy.height/2):
                            y = random.randint(-1*(moveRange),moveRange)
                        i.changeFlag(Target([i.position[0]+x,i.position[1]+y,0]), FlagState.MOVE)

                 
    def choixAction(self):
        self.decisionBuildUnit()
        if self.nbrUnit(Unit.ATTACK_SHIP)+self.nbrUnit(Unit.SPACE_BUILDING_ATTACK) > 3:
            moveRange = 800
            if len(self.enemyDiscovered) > 0:
                self.sendToAttackEnemy()
        else:
            moveRange = 400
        self.explore(moveRange)
        self.checkIfSawEnemy()
        self.checkIfEnemyInRange()
        self.checkRessources()

    def checkIfSawEnemy(self):
        unit = self.getNearestScoutFromMothership()
        if unit != None:
            for pl in self.game.players:
                if pl != self:
                    for modo in pl.motherships:
                        if modo.isAlive:
                            if modo.isInRange(unit.position, unit.viewRange):
                                self.enemyDiscovered.append(modo)

    def checkRessources(self):
        ressource = self.trouverRessource()
        if ressource != None:
            if self.envoyerCargo(ressource):
                if Helper.calcDistance(ressource.position[0],ressource.position[1],self.motherships[0].position[0], self.motherships[0].position[1]) > 200:
                    self.buildBuilding(Building.WAYPOINT, ressource)
            
    def decisionBuildUnit(self):
        for i in self.priority:
            if self.needBuild(i):
                if self.canAfford(Unit.BUILD_COST[i][0],Unit.BUILD_COST[i][1], Unit.BUILD_COST[i][2]):
                    b =self.getStandByBuilding(i)
                    if b != None:
                        self.ressources[0] -= Unit.BUILD_COST[i][0]
                        self.ressources[1] -= Unit.BUILD_COST[i][1]
                        self.ressources[2] += Unit.BUILD_COST[i][2]
                        b.addUnitToQueue(i)
                        return None
    
    def haveBuilding(self, unitType):
        for i in self.buildings:
            if i.type == unitType:
                return True
        return False
    
    def needBuild(self, unitType):
        if self.nbrUnit(unitType) < self.maxUnits[self.priority.index(unitType)]:
            if unitType in (Unit.SCOUT, Unit.CARGO):
                return True #meme pour scout et les autres
            elif unitType == Unit.TRANSPORT:
                if self.haveBuilding(Building.UTILITY):
                    return True
                else:
                    self.buildBuilding(Building.UTILITY)
                    return False
            elif unitType in (Unit.ATTACK_SHIP, Unit.SPACE_BUILDING_ATTACK):
                if self.haveBuilding(Building.BARRACK):
                    return True
                else:
                    self.buildBuilding(Building.BARRACK)
                    return False
        return False

    def buildBuilding(self, buildingType, ressource=None):
        if self.canAfford(Building.COST[buildingType][0],Building.COST[buildingType][0],0):
            scout = self.getNearestScoutFromMothership()
            if scout != None:
                self.ressources[0] -= Building.COST[buildingType][0]
                self.ressources[1] -= Building.COST[buildingType][1]
                if Building.INSPACE[buildingType]:
                    positionBuilding = self.getPositionBuild(buildingType, ressource)
                    self.game.buildBuilding(self.id, positionBuilding, FlagState.BUILD, [str(self.units.index(scout))], buildingType)
                elif len(self.planets) > 0:
                    planet = self.planets[0]
                    positionBuilding = self.getGroundPositionBuild(buildingType, planet.id, planet.solarSystem.sunId)
                    self.game.buildBuilding(self.id, positionBuilding, FlagState.BUILD, [str(self.units.index(scout))], buildingType, planet.id, planet.solarSystem.sunId)

    def getNearestScoutFromMothership(self):
        distance = 89374
        scout = None
        for un in self.units:
            if un.isAlive:
                if un.type == Unit.SCOUT:
                    if un.flag.flagState != FlagState.BUILD:
                        undist = Helper.calcDistance(un.position[0],un.position[1],self.motherships[0].position[0],self.motherships[0].position[1])
                        if undist < distance:
                            distance = undist
                            scout = un
        return scout

    def checkIfEnemyInRange(self):
        unit = self.getNearestScoutFromMothership()
        if unit != None:
            for pl in self.game.players:
                if pl.isAlive:
                    if pl.id != unit.owner and (self.game.players[unit.owner].isAlly(pl.id) == False or isinstance(pl, IA)):
                        enemyUnit = pl.hasUnitInRange(unit.position, unit.viewRange)
                        if enemyUnit != None:
                            attackShip = self.getFirstAttackShipStandBy(enemyUnit.position)
                            if attackShip != None:
                                if attackShip.type == Unit.ATTACK_SHIP:
                                    attackShip.changeFlag(enemyUnit, FlagState.ATTACK)
                                else:
                                    attackShip.changeFlag(enemyUnit, FlagState.ATTACK_BUILDING)

    def getFirstAttackShipStandBy(self, enemyPosition):
        distance = 985943
        attack = None
        for un in self.units:
            if un.isAlive:
                if un.type in (un.ATTACK_SHIP,un.SPACE_BUILDING_ATTACK):
                    if un.flag.flagState != FlagState.ATTACK:
                        atdist = Helper.calcDistance(un.position[0],un.position[1],enemyPosition[0],enemyPosition[1])
                        if atdist < distance:
                            distance = atdist
                            attack = un
        return attack

    def sendToAttackEnemy(self):
        sendToAttack = []
        for attacks in self.units:
            if i.isAlive:
                if attacks.type in (Unit.ATTACK_SHIP,Unit.SPACE_BUILDING_ATTACK):
                    sendToAttack.append(un)
        sendToAttack.pop(len(sendToAttack)-1)
        sendToAttack.pop(len(sendToAttack)-1)
        for att in sendToAttack:
            if att.type == Unit.ATTACK_SHIP:
                att.changeFlag(self.enemyDiscovered[0], FlagState.ATTACK)
            else:
                att.changeFlag(self.enemyDiscovered[0], FlagState.ATTACK_BUILDING)
    
    def getPositionBuild(self, buildType, ressource = None):
        if buildType != Building.WAYPOINT:
            modoPoso = self.motherships[0].position
            x = random.randint(int(modoPoso[0])-250,int(modoPoso[0])+250)
            y = random.randint(int(modoPoso[1])-250,int(modoPoso[1])+250)
        else:
            ress = ressource.position
            x = random.randint(int(ress[0])-30,int(ress[0])+30)
            y = random.randint(int(ress[1])-30,int(ress[1])+30)
        if x < -1*(self.game.galaxy.width/2):
            x = -1*(self.game.galaxy.width/2) + Building.SIZE[buildType][0]
        elif x > (self.game.galaxy.width/2):
            x = -1*(self.game.galaxy.width/2) - Building.SIZE[buildType][0]
        if y < -1*(self.game.galaxy.height/2):
            y = -1*(self.game.galaxy.height/2) + Building.SIZE[buildType][1]
        elif y > (self.game.galaxy.height/2):
            y = (self.game.galaxy.height/2) - Building.SIZE[buildType][1]
        return (x,y,0)
            
    def getStandByBuilding(self, unitType):
        if unitType == Unit.CARGO or unitType == Unit.SCOUT:
            for i in self.motherships:
                if i.isAlive:
                    if i.flag.flagState == FlagState.STANDBY:
                        return i 
        else:
            for i in self.buildings:
                if i.isAlive:
                    if (i.type == Building.UTILITY and unitType == Unit.TRANSPORT) or (i.type == Building.BARRACK and unitType in (Unit.ATTACK_SHIP, Unit.SPACE_BUILDING_ATTACK)):
                        if i.flag.flagState  == FlagState.STANDBY:
                            return i
            return None
    
    def nbrUnit(self,unitType):
        nbr = 0
        for i in self.units:
            if i.isAlive:
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
            
