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
        self.priority = (1,4,3,2)
        self.maxUnits =(2,5,1,40)
        self.enemyDiscovered = []
        self.diplomacies = ['Enemy','Enemy','Enemy','Enemy','Enemy','Enemy','Enemy','Enemy']
        
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
            for j in i.asteroids:
                if self.game.players[self.id].inViewRange(j.position) and j.mineralQte > 0:
                    return j
            for j in i.nebulas:
                if self.game.players[self.id].inViewRange(j.position) and j.gazQte > 0:
                    return j
        return None
                    
    def envoyerCargo(self,ressource):
        sentOne = False
        for i in self.units:
            if i.isAlive:
                if i.type == Unit.CARGO:
                    if i.flag.flagState != FlagState.GATHER:
                        i.changeFlag(ressource,FlagState.GATHER)
                        sentOne = True
        return sentOne
                    
    def explore(self, moveRange):
        for i in self.units:
            if i.isAlive:
                if i.type == Unit.SCOUT or (i.type == Unit.CARGO and i.flag.flagState != FlagState.GATHER) or (i.type == Unit.ATTACK_SHIP and i.flag.flagState != FlagState.ATTACK):
                    if i.flag.flagState != FlagState.BUILD or i.flag.flagState != FlagState.MOVE:
                        x = random.randint(-1*(moveRange),moveRange)
                        y = random.randint(-1*(moveRange),moveRange)
                        while (i.position[0]+x < (self.game.galaxy.width/2)*-1 or i.position[0]+x > self.game.galaxy.width/2):
                            x = random.randint(-1*(moveRange),moveRange)
                        while (i.position[1]+y < (self.game.galaxy.height/2)*-1 or i.position[1]+y > self.game.galaxy.height/2):
                            y = random.randint(-1*(moveRange),moveRange)
                        i.changeFlag(Target([i.position[0]+x,i.position[1]+y,0]), FlagState.MOVE)

                 
    def choixAction(self):
        self.doYourStuffOnPlanets()
        self.decisionBuildUnit()
        self.sendUnitsToAttackDiscovered()
        self.explore(1200)
        self.checkIfSawEnemy()
        self.checkIfBuildingAreNotFinished()
        self.checkIfEnemyInRange()
        self.checkRessources()

    def doYourStuffOnPlanets(self):
        if len(self.planets) == 0:
            self.sendTransportToPlanet()
        for p in self.planets:
            self.checkRessourcesPlanets(p)
            if self.getGroundBuilders(p) == 0:
                if len(self.units) > 9:
                    self.units[9].kill()
                self.build(Unit.GROUND_BUILDER_UNIT)
            if self.numberOfStacks(p) >  self.getGroundGathers(p):
                for i in range(self.getGroundGathers(p),self.numberOfStacks(p)):
                    self.build(Unit.GROUND_GATHER)

    def numberOfStacks(self, planet):
        stacks = 0
        for st in planet.minerals:
            if st.nbMinerals > 0:
                stacks += 1
        for gaz in planet.gaz:
            if gaz.nbGaz > 0:
                stacks += 1
        return stacks

    def sendUnitsToAttackDiscovered(self):
        if self.nbrUnit(Unit.ATTACK_SHIP) > 2:
            if self.nbrUnit(Unit.ATTACK_SHIP) % 5 == 2:
                self.build(Unit.SPACE_BUILDING_ATTACK)
            if len(self.enemyDiscovered) > 0:
                self.sendToAttackEnemy()            

    def checkIfBuildingAreNotFinished(self):
        scout = self.getNearestScoutFromMothership()
        if scout != None:
            if scout.flag.flagState != FlagState.BUILD:
                for bl in self.buildings:
                    if not bl.finished:
                        scout.changeFlag(bl,FlagState.BUILD)

    def checkIfSawEnemy(self):
        for unit in self.units:
            for pl in self.game.players:
                if pl != self:
                    for bl in pl.buildings:
                        if bl.isAlive:
                            if isinstance(bl, SpaceBuilding) or isinstance(bl, Mothership):
                                if bl.type != Building.WAYPOINT:
                                    if bl.isInRange(unit.position, unit.viewRange):
                                        if not self.isNotAlreadyInEnemiesDiscovered(bl):
                                            self.enemyDiscovered.append(bl)

    def isNotAlreadyInEnemiesDiscovered(self, building):
        for bl in self.enemyDiscovered:
            if bl == building:
                return True
        return False

    def checkRessources(self):
        ressource = self.trouverRessource()
        if ressource != None:
            if self.envoyerCargo(ressource):
                nearestBuild = self.getNearestReturnRessourceCenter(ressource.position)
                if  Helper.calcDistance(ressource.position[0], ressource.position[1], nearestBuild.position[0], nearestBuild.position[1]) > 300:
                    self.buildBuilding(Building.WAYPOINT, ressource)

    def checkRessourcesPlanets(self, planet):
        ressource = self.findRessourcePlanet(planet)
        if ressource != None:
            self.sendGroundGather(ressource)
            return True
        else:
            if planet.getLandingSpot(self.id).LandedShip != None:
                landingZone = planet.getLandingSpot(self.id)
                toRange = len(planet.units)
                if toRange > 10:
                    toRange = 10
                for unit in range(0,toRange):
                    if planet.units[unit].owner == self.id:
                        if planet.units[unit].flag.flagState != FlagState.LOAD:
                            planet.units[unit].changeFlag(landingZone, FlagState.LOAD)
                units = 0
                for unit in planet.units:
                    if unit.owner == self.id:
                        units += 1
                if units == 0 or len(landingZone.LandedShip.units) == 10:
                    self.game.takeOff(landingZone.LandedShip, planet, self.id)
                    self.sendTransportToPlanet()
            return False

    def getGroundGathers(self, planet):
        gatherers = 0
        for un in planet.units:
            if un.owner == self.id:
                if un.type == Unit.GROUND_GATHER:
                    gatherers += 1
        for un in planet.getLandingSpot(self.id).unitBeingConstruct:
            if un.type == Unit.GROUND_GATHER:
                gatherers += 1
            
        return gatherers

    def sendGroundGather(self, ressource):
        sentOne = False
        for un in self.units:
            if un.isAlive:
                if un.type == Unit.GROUND_GATHER:
                    if un.flag.flagState != FlagState.GROUND_GATHER:
                        un.changeFlag(ressource, FlagState.GROUND_GATHER)
                        sentOne = True
        return sentOne
                        

    def findRessourcePlanet(self, planet):
        for st in planet.minerals:
            if st.nbMinerals > 0:
                return st
        for gaz in planet.gaz:
            if gaz.nbGaz > 0:
                return gaz
        return None

    def sendTransportToPlanet(self):
        for u in self.units:
            if u.isAlive:
                if u.type == Unit.TRANSPORT:
                    if u.flag.flagState != FlagState.LAND:
                        planet = self.getNearestPlanet(u.position)
                        u.changeFlag(planet, FlagState.LAND)

    def getNearestPlanet(self, position):
        distance = 9999999
        planet = None
        for i in self.game.galaxy.solarSystemList:
            for j in i.planets:
                if j.getLandingSpot(self.id) == None:
                    distancePlan = Helper.calcDistance(position[0],position[1],j.position[0],j.position[1])
                    if distancePlan < distance:
                        distance = distancePlan
                        planet = j
        return planet
            
    def decisionBuildUnit(self):
        haveBuilt = False
        for i in self.priority:
            if (self.priority.index(i) > 1 and haveBuilt == False) or self.priority.index(i) <= 1:
                if self.needBuild(i):
                    haveBuilt = True
                    self.build(i)

    def build(self, unitType):
        if self.canAfford(Unit.BUILD_COST[unitType][self.MINERAL],Unit.BUILD_COST[unitType][self.GAS], Unit.BUILD_COST[unitType][self.FOOD]):
            b =self.getStandByBuilding(unitType)
            if b != None:
                self.ressources[self.MINERAL] -= u.Unit.BUILD_COST[unitType][Unit.MINERAL]
                self.ressources[self.GAS] -= u.Unit.BUILD_COST[unitType][Unit.GAS]
                self.ressources[self.FOOD] += u.Unit.BUILD_COST[unitType][Unit.FOOD]
                b.addUnitToQueue(unitType, self.game.galaxy)
                return 0
        elif self.ressources[self.FOOD]+Unit.BUILD_COST[unitType][self.FOOD] > self.MAX_FOOD:
            if len(self.planets) == 0:
                self.sendTransportToPlanet()
            else:
                if not self.haveIAFarmInConstruction(self.planets[0]):
                    self.buildBuilding(Building.FARM, self.planets[0])

    def haveIAFarmInConstruction(self, planet):
        for i in self.buildings:
            if i.isAlive:
                if i.type == Building.FARM:
                    if not i.finished:
                        return True
        return False
    
    def haveBuilding(self, unitType):
        for i in self.buildings:
            if i.isAlive:
                if i.type == unitType:
                    return True
        return False
    
    def needBuild(self, unitType):
        if self.nbrUnit(unitType) < self.maxUnits[self.priority.index(unitType)]:
            if unitType in (Unit.SCOUT, Unit.CARGO):
                return True
            elif unitType == Unit.TRANSPORT:
                if self.haveBuilding(Building.UTILITY):
                    return True
                else:
                    self.buildBuilding(Building.UTILITY)
            elif unitType in (Unit.ATTACK_SHIP, Unit.SPACE_BUILDING_ATTACK):
                if self.haveBuilding(Building.BARRACK):
                    return True
                else:
                    self.buildBuilding(Building.BARRACK)
            elif unitType in (Unit.GROUND_ATTACK, Unit.SPECIAL_GATHER):
                if self.haveBuilding(Building.LANDING_ZONE):
                    return True
                else:
                    self.sendTransportToPlanet()
        return False

    def buildBuilding(self, buildingType, ressource=None):
        if self.canAfford(Building.COST[buildingType][self.MINERAL],Building.COST[buildingType][self.GAS],0):
            if Building.INSPACE[buildingType]:
                scout = self.getNearestScoutFromMothership()
                if scout != None:
                    positionBuilding = self.getPositionBuild(buildingType, ressource)
                    self.game.buildBuilding(self.id, positionBuilding, FlagState.BUILD, [str(self.units.index(scout))], buildingType)
            elif len(self.planets) > 0:
                planet = ressource
                builder = self.getNearestBuilderFromLandingZone(planet)
                if builder != None:
                    sunId = self.game.galaxy.solarSystemList.index(planet.solarSystem)
                    planetId = self.game.galaxy.solarSystemList[sunId].planets.index(planet)
                    positionBuilding = self.getGroundPositionBuild(buildingType, planet)
                    if positionBuilding != None:
                        self.game.buildBuilding(self.id, positionBuilding, FlagState.BUILD, [str(self.units.index(builder))], buildingType, sunId, planetId)

    def getGroundBuilders(self, planet):
        builders = 0
        for un in planet.units:
            if un.owner == self.id:
                if un.isAlive:
                    if un.type == Unit.GROUND_BUILDER_UNIT:
                        builders += 1
        for un in planet.getLandingSpot(self.id).unitBeingConstruct:
            if un.type == Unit.GROUND_BUILDER_UNIT:
                builders += 1
        return builders

    def getNearestBuilderFromLandingZone(self, planet):
        landingPos = planet.getLandingSpot(self.id).position
        distance = 9999999
        unit = None
        for un in self.units:
            if un.isAlive:
                if un.type == Unit.GROUND_BUILDER_UNIT:
                    if un.planet == planet:
                        if un.flag.flagState != FlagState.BUILD:
                            undist = Helper.calcDistance(un.position[0], un.position[1], landingPos[0], landingPos[1])
                            if undist < distance:
                                distance = undist
                                unit = un
        return unit

    def getNearestScoutFromMothership(self):
        distance = 99999999
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
        for un in self.units:
            if un.type in (Unit.ATTACK_SHIP, Unit.SCOUT, Unit.SPACE_BUILDING_ATTACK):
                for pl in self.game.players:
                    if pl.isAlive:
                        if pl.id != self.id and (self.game.players[self.id].isAlly(pl.id) == False or isinstance(pl, IA)):
                            enemyUnit = pl.hasUnitInRange(un.position, un.viewRange)
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
            if attacks.isAlive:
                if attacks.type in (Unit.ATTACK_SHIP, Unit.SPACE_BUILDING_ATTACK):
                    sendToAttack.append(attacks)
        if sendToAttack[len(sendToAttack)-1].type != Unit.SPACE_BUILDING_ATTACK:
            sendToAttack.pop(len(sendToAttack)-1)
        if not self.enemyDiscovered[0].isAlive:
            self.enemyDiscovered.pop(0)
        if len(self.enemyDiscovered) > 0:
            for att in sendToAttack:
                if att.type == Unit.ATTACK_SHIP:
                    att.changeFlag(self.enemyDiscovered[0], FlagState.ATTACK)
                else:
                    att.changeFlag(self.enemyDiscovered[0], FlagState.ATTACK_BUILDING)
        
    
    def getPositionBuild(self, buildType, ressource = None):
        self.currentPlanet = None
        if buildType != Building.WAYPOINT and Building.INSPACE[buildType]:
            modoPoso = self.motherships[0].position
            x = random.randint(int(modoPoso[0])-250,int(modoPoso[0])+250)
            y = random.randint(int(modoPoso[1])-250,int(modoPoso[1])+250)
            while not self.game.checkIfCanBuild([x,y,0],buildType,0,self.id):
                x = random.randint(int(modoPoso[0])-250,int(modoPoso[0])+250)
                y = random.randint(int(modoPoso[1])-250,int(modoPoso[1])+250)
        else:
            ress = ressource.position
            x = random.randint(int(ress[0])-50,int(ress[0])+50)
            y = random.randint(int(ress[1])-50,int(ress[1])+50)
            while not self.game.checkIfCanBuild([x,y,0],buildType,0,self.id):
                x = random.randint(int(ress[0])-50,int(ress[0])+50)
                y = random.randint(int(ress[1])-50,int(ress[1])+50)
        if x < -1*(self.game.galaxy.width/2):
            x = -1*(self.game.galaxy.width/2) + Building.SIZE[buildType][0]
        elif x > (self.game.galaxy.width/2):
            x = -1*(self.game.galaxy.width/2) - Building.SIZE[buildType][0]
        if y < -1*(self.game.galaxy.height/2):
            y = -1*(self.game.galaxy.height/2) + Building.SIZE[buildType][1]
        elif y > (self.game.galaxy.height/2):
            y = (self.game.galaxy.height/2) - Building.SIZE[buildType][1]
        return (x,y,0)

    def getGroundPositionBuild(self, buildType, planet):
        if len(planet.units) > 0:
            self.currentPlanet = planet
            unit = self.getNearestBuilderFromLandingZone(planet)
            x = random.randint(int(unit.position[0])-250,int(unit.position[0])+250)
            y = random.randint(int(unit.position[1])-250,int(unit.position[1])+250)
            while not self.game.checkIfCanBuild([x,y,0],buildType,self.units.index(unit),self.id):
                x = random.randint(int(unit.position[0])-250,int(unit.position[0])+250)
                y = random.randint(int(unit.position[1])-250,int(unit.position[1])+250)
            if x < 0:
                x = Building.SIZE[buildType][0]
            elif x > planet.WIDTH:
                x = planet.WIDTH - Building.SIZE[buildType][0]
            if y < 0:
                y = Building.SIZE[buildType][1]
            elif y > planet.HEIGHT:
                y = planet.HEIGHT - Building.SIZE[buildType][1]
            return (x,y,0)
        return None
            
    def getStandByBuilding(self, unitType):
        if unitType == Unit.CARGO or unitType == Unit.SCOUT:
            for i in self.motherships:
                if i.isAlive:
                    if i.finished:
                        return i 
        else:
            for i in self.buildings:
                if i.isAlive:
                    if i.finished:
                        if (i.type == Building.UTILITY and unitType == Unit.TRANSPORT) or (i.type == Building.BARRACK and unitType in (Unit.ATTACK_SHIP, Unit.SPACE_BUILDING_ATTACK)) or (i.type == Building.LANDING_ZONE and unitType in (Unit.GROUND_GATHER, Unit.GROUND_BUILDER_UNIT, Unit.GROUND_ATTACK, Unit.SPECIAL_GATHER)):
                            return i
            return None
    
    def nbrUnit(self,unitType):
        nbr = 0
        for i in self.units:
            if i.isAlive:
                if i.type == unitType:
                    nbr = nbr+1
        for i in self.buildings:
            if i.isAlive:
                if isinstance(i, ConstructionBuilding):
                    for un in i.unitBeingConstruct:
                        if un.isAlive:
                            if un.type == unitType:
                                nbr+=1
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
            
