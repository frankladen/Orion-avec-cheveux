# -*- coding: UTF-8 -*-
import Unit as u
import Building as b
import World as w
from Target import *
from Flag import *
from Target import *
from Helper import *
from TechTree import *
import math
import socket

#Represente un joueur
class Player():
    MINERAL = 0
    GAS = 1
    FOOD = 2
    NUCLEAR = 3
    ATTACK_DAMAGE_BONUS = 0
    ATTACK_SPEED_BONUS = 1
    MOVE_SPEED_BONUS = 2
    ATTACK_RANGE_BONUS = 3
    VIEW_RANGE_BONUS = 4
    BUILDING_SHIELD_BONUS = 5
    BUILDING_MOTHERSHIELD_BONUS = 6
    ATTACK_DAMAGE_MOTHERSHIP = 7
    ATTACK_DAMAGE_BUILDING_BONUS = 8
    ABILITY_WORM_HOLE = 9
    ABILITY_WALLS = 10
    #[AttaqueDamage,AttaqueSpeed,MoveSpeed,AttackRange]
    BONUS = [0,0,0,0,0,0,0,0,0,0,0]
    MAX_FOOD = 10
    FORCE_BUILD_ACTIVATED = False
    SQUARE_FORMATION = 0
    TRIANGLE_FORMATION = 1
    
    def __init__(self, name, game, id , colorId):
        self.name = name
        self.game = game
        self.colorId = colorId
        self.techTree = TechTree()
        self.selectedObjects = [] #Liste des unites selectionnes
        self.listMemory = [[],[],[],[],[],[],[],[],[]]
        self.units = [] #Liste de toute les unites
        self.buildings = [] #Liste de tous les buildings
        self.notifications = [] #Liste de toutes les notifications
        self.planets = [] #Liste des planètes que nous avons atterit
        self.planetCurrent = 0
        self.bullets = []
        self.id = id #Numero du joueur dans la liste de joueur
        self.diplomacies=[]
        for i in range(8):
            self.diplomacies.append('Enemy')
        self.diplomacies[self.id] = 'Ally'
        self.startPos = [0,0,0] #Position de depart du joueur (pour le mothership)
        self.motherShip = None
        self.motherships = []
        self.walls = []
        self.motherCurrent = 0
        self.formation = self.SQUARE_FORMATION
        self.currentPlanet = None
        self.ressources = [350,350,2,0]
        self.isAlive = True
        self.camera = None
        self.actionHealUnit = None
    
    def getSelectedHealUnitIndex(self):
        if self.selectedObjects[0].type == u.Unit.HEALING_UNIT:
            return  self.units.index(self.selectedObjects[0])
        return None

    def selectUnitToHeal(self, position):
        for i in self.units:
            if not isinstance(i, u.GroundUnit):
                unit = i.select(position)
                if unit != None:
                    return unit
        for i in self.buildings:
            if not isinstance(i, b.GroundBuilding):
                building = i.select(position)
                if building != None:
                    return building
        return None
    
    def getSelectedBuildingIndex(self):
        return self.buildings.index(self.selectedObjects[0])
    
    def action(self):
        for i in self.units:
            if i.isAlive:
                i.action(self)
        for i in self.buildings:
            if i.isAlive:
                i.action(self)
        for i in self.walls:
            i.action(self)
        for i in self.bullets:
            i.action(self)

    def linkWaypoints(self, wayId1, wayId2, cost):
        way1 = self.buildings[wayId1]
        way2 = self.buildings[wayId2]
        if way1.hasFreeWall and way2.hasFreeWall:
            self.ressources[self.GAS] -= cost
            wall = b.Wall(way1, way2)
            if way1.addWall(wall, way2):
                if way2.addWall(wall, way1):
                    self.walls.append(wall)
                else:
                    way1.destroyWall(wall)
            
    def selectUnitsByType(self, unitType):
        units = []
        for i in self.selectedObjects:
            if i.type == unitType:
                units.append(i)
        self.selectedObjects = units
            
    def addBaseUnits(self, startPos):
        self.buildings.append(b.Mothership( b.Building.MOTHERSHIP,startPos, self.id))
        self.motherShip = self.buildings[0]
        self.motherships.append(self.motherShip)
        self.motherShip.finished = True
        self.motherShip.buildingTimer = b.Building.TIME[b.Building.MOTHERSHIP]
        self.motherShip.hitpoints = self.motherShip.maxHP
        self.motherShip.armor = self.motherShip.MAX_ARMOR
        self.units.append(u.Unit(u.Unit.SCOUT,[startPos[0] + 20, startPos[1] + 20 ,0], self.id))
        self.units.append(u.GatherShip(u.Unit.CARGO,[startPos[0] + 40, startPos[1]+40], self.id))
        
    #Ajoute une camera au joueur seulement quand la partie commence    
    def addCamera(self, galaxy, width, height):
        pos = self.motherShip.position
        default = [pos[0],pos[1]]
        self.camera = Camera(default, galaxy, self, width, height)

    def moveCamera(self):
        self.camera.move()

    def changeDiplomacy(self, playerToChange, newStatus):
        self.diplomacies[playerToChange] = newStatus

    def selectUnit(self, position):
        for i in self.units:
            if not isinstance(i, u.GroundUnit):
                unit = i.select(position)
                if unit != None:
                    self.selectedObjects = [unit]
                    return
        for i in self.buildings:
            if not isinstance(i, b.GroundBuilding) and not isinstance(i, b.LandingZone):
                building = i.select(position)
                if building != None:
                    self.selectedObjects = [building]
                    return

    def multiSelectUnit(self, position):
        for i in self.units:
            unit = i.select(position)
            if unit != None and unit not in self.selectedObjects:
                self.selectedObjects.append(unit)

    def selectObject(self, playerObj, multi):
        if playerObj != None:
            #Si on selectionne une unitÃ©
            if isinstance(playerObj, u.Unit):
                if playerObj.owner == self.id:
                    if not multi:
                        self.selectedObjects = [playerObj]
                    else:
                        self.selectedObjects.append(playerObj)
            elif isinstance(playerObj, b.LandingZone):
                if playerObj.owner == self.id:
                    self.selectedObjects = [playerObj]
            #Sinon, si on selectionne autre chose
            else:
                if not multi:
                    self.selectedObjects = [playerObj]
                else:
                    self.selectedObjects.append(playerObj)
    
    def selectObjectFromMenu(self, unitId):
        self.selectedObjects = [self.selectedObjects[unitId]]
    
    def boxSelect(self, selectStart, selectEnd):
        first = True
        if self.currentPlanet == None:
            for i in self.units:
                if not isinstance(i, u.GroundUnit):
                    unit = i.boxSelect(selectStart, selectEnd)
                    if first:
                        self.selectedObjects = []
                        first = False
                    self.selectObject(unit, True)
        else:
            for i in self.currentPlanet.units:
                unit = i.boxSelect(selectStart, selectEnd)
                if first:
                    self.selectedObjects = []
                    first = False
                self.selectObject(unit, True)
    
    def selectAll(self, position):
        if self.currentPlanet == None:
            self.selectUnit(position)
            firstUnit = self.selectedObjects[0]
            if len(self.selectedObjects) > 0:
                for i in self.units:
                    if self.camera.inGameArea(i.position):
                        unit = i.select(position)
                        if unit.type == firstUnit.type:
                            self.selectObject(unit, True)
                            
    def getFirstUnit(self):
        if len(self.selectedObjects) > 0:
            if isinstance(self.selectedObjects[0], u.Unit) or isinstance(self.selectedObjects[0], b.ConstructionBuilding):
                return self.selectedObjects[0]
        return None

    def getShipToUnload (self):
        planet = self.currentPlanet
        if planet != None:
            zone = planet.getLandingSpot(self.id)
            if zone != None:
                if zone in self.selectedObjects:
                    ship = zone.LandedShip
                    if ship != None:
                        return zone
        return None
        
    def rightClic(self, pos, playerId):
        if self.isAlive:
            if self.isAlly(playerId) == False or playerId == self.id:
                for i in self.units:
                    unit = i.select(pos)
                    if unit != None:
                        return unit
                unit = self.motherShip.select(pos)
                if unit != None:
                    return unit
                for b in self.buildings:
                    building = b.select(pos)
                    if building != None:
                        return building                
        return None

    def selectPlanet(self, planet):
        if len(self.selectedObjects) > 0:
            if self.selectedObjects[0] == planet:
                self.lookPlanet(planet)
            else:
                self.selectedObjects = [planet]
        else:
            self.selectedObjects = [planet]
            
    def lookPlanet(self, planet):
        if planet.alreadyLanded(self.id):
            self.currentPlanet = planet
            self.camera.placeOnLanding(planet.getLandingSpot(self.id))
        
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
                    
        for i in range(len(self.diplomacies)):
            if self.isAlly(i) and i != self.id:
                for un in self.game.players[i].units:
                    if un.isAlive and not isinstance(un, u.GroundUnit):
                        if x > un.position[0]-un.viewRange and x < un.position[0]+un.viewRange:
                            if y > un.position[1]-un.viewRange and y < un.position[1]+un.viewRange:
                                if un.type == u.Unit.TRANSPORT:
                                    if not un.landed:
                                        return True
                                else:
                                    return True
                for bu in self.game.players[i].buildings:
                    if bu.isAlive and bu.finished and not isinstance(bu, b.GroundBuilding) and not isinstance(bu, b.LandingZone):
                        if x > bu.position[0]-bu.viewRange and x < bu.position[0]+bu.viewRange:
                            if y > bu.position[1]-bu.viewRange and y < bu.position[1]+bu.viewRange:
                                return True
        if x > self.motherShip.position[0]-self.motherShip.viewRange and x < self.motherShip.position[0]+self.motherShip.viewRange:
            if y > self.motherShip.position[1]-self.motherShip.viewRange and y < self.motherShip.position[1]+self.motherShip.viewRange:
                return True

        
        return False
    
    def isAlly(self, playerId):
        if self.diplomacies[playerId] == "Ally":
            return self.game.isAllied(playerId, self.id)
        return False

    def getNearestReturnRessourceCenter(self, position):
        motherShipPosition = self.motherships[0].position
        nearestDistance = Helper.calcDistance(position[0],position[1],motherShipPosition[0],motherShipPosition[1])
        nearestBuilding = self.motherships[0]
        for b in self.buildings:
            if b.type == b.WAYPOINT or b.type == b.MOTHERSHIP:
                if b.finished:
                    buildingPosition = b.position
                    distance = Helper.calcDistance(position[0],position[1],buildingPosition[0],buildingPosition[1])
                    if distance < nearestDistance:
                        nearestDistance = distance
                        nearestBuilding = b
        return nearestBuilding

    def getNearestReturnRessourceCenterOnSpace(self, position, unit):
        sunId = unit.sunId
        planetId = unit.planetId
        if unit.planet.getLandingSpot(unit.owner) != None:
            landingSpotPosition = unit.planet.getLandingSpot(unit.owner).position
            nearestDistance = Helper.calcDistance(position[0],position[1],landingSpotPosition[0],landingSpotPosition[1])
            nearestBuilding = unit.planet.getLandingSpot(unit.owner)
        else:
            nearestDistance = 894382740932748
            nearestBuilding = unit.flag.finalTarget.position
        for b in self.buildings:
            if b.type == b.FARM:
                if b.finished:
                    if b.sunId == sunId:
                        if b.planetId == planetId:
                            buildingPosition = b.position
                            distance = Helper.calcDistance(position[0],position[1],buildingPosition[0],buildingPosition[1])
                            if distance < nearestDistance:
                                nearestDistance = distance
                                nearestBuilding = b
        return nearestBuilding

    def checkIfIsAttacking(self, killedIndexes):
        if killedIndexes[2] == True:
            unitToAttack = self.game.players[killedIndexes[1]].buildings[killedIndexes[0]]
        else:
            unitToAttack = self.game.players[killedIndexes[1]].units[killedIndexes[0]]
        for i in self.units:
            if i.isAlive:
                if i.flag.finalTarget == unitToAttack and i.flag.flagState == FlagState.ATTACK:
                    i.flag = Flag(t.Target(i.position), t.Target(i.position), FlagState.STANDBY)
                    i.attackcount=i.AttackSpeed
        for b in self.buildings:
            if b.isAlive:
                if b.flag.finalTarget == unitToAttack:
                    b.flag = Flag(t.Target(i.position), t.Target(i.position), FlagState.STANDBY)
                    b.attackcount=b.AttackSpeed

    def checkIfCanAddNotif(self, type):
        for n in self.notifications:
            if n.type == type:
                return False
        return True

    def killUnit(self, killedIndexes):
        if killedIndexes[1] == self.id:
            if killedIndexes[2] == False:
                if self.units[killedIndexes[0]] in self.selectedObjects:
                    self.selectedObjects.remove(self.units[killedIndexes[0]])
                self.units[killedIndexes[0]].kill()
                self.ressources[self.FOOD] -= u.Unit.BUILD_COST[self.units[killedIndexes[0]].type][self.FOOD]
            else:
                if self.buildings[killedIndexes[0]] in self.selectedObjects:
                    self.selectedObjects.remove(self.buildings[killedIndexes[0]])
                if self.buildings[killedIndexes[0]].type == b.Building.WAYPOINT:
                    self.buildings[killedIndexes[0]].kill(self)
                else:
                    self.buildings[killedIndexes[0]].kill()
                    if self.buildings[killedIndexes[0]].type == b.Building.FARM:
                        self.MAX_FOOD -= 5
                    elif self.buildings[killedIndexes[0]].type == b.Building.LANDING_ZONE:
                        self.game.removeLandingZoneFromPlanet(self.buildings[killedIndexes[0]])
            self.game.killUnit(killedIndexes, False)
        else:
            self.game.killUnit(killedIndexes, True)


    def hasUnitInRange(self, position, range, onPlanet = False, planetId = -1, solarSystemId = -1):
        unitInRange = None
        for un in self.units:
            if un.isAlive:
                unitInRange = un.isInRange(position, range, onPlanet, planetId, solarSystemId)
                if unitInRange != None:
                    return unitInRange
        for bd in self.buildings:
            if bd.isAlive:
                buildingInRange = bd.isInRange(position, range, onPlanet, planetId, solarSystemId)
                if buildingInRange != None:
                    return buildingInRange
        return None

    def buildUnit(self, constructionUnit):
        unit = constructionUnit.unitBeingConstruct.pop(0)
        unit.applyBonuses(self.BONUS)
        unit.changeFlag(t.Target(constructionUnit.rallyPoint), FlagState.MOVE)
        self.units.append(unit)

        if self.game.playerId == unit.owner:
            if not self.camera.inGameArea(constructionUnit.position):
                if isinstance(constructionUnit, b.Mothership) or isinstance(constructionUnit, b.Barrack) or isinstance(constructionUnit, b.Utility):
                    self.notifications.append(Notification(constructionUnit.position, Notification.FINISHED_BUILD, u.Unit.NAME[unit.type]))
                else:
                    self.notifications.append(Notification(constructionUnit.planet.position, Notification.FINISHED_BUILD, u.Unit.NAME[unit.type]))
        
        if isinstance(unit, u.GroundUnit):
            self.game.galaxy.solarSystemList[unit.sunId].planets[unit.planetId].units.append(unit)

    def sendKill(self):
        self.parent.sendKillPlayer(self.id)

    def kill(self):
        self.isAlive = False
        for i in self.units:
            i.kill()
        for b in self.buildings:
            b.kill()

    def changeBonuses(self):
        for unit in self.units:
            unit.applyBonuses(self.BONUS)
        for building in self.buildings:
            building.applyBonuses(self.BONUS)
            
    def adjustRessources(self, ressourceType, amount):
        self.ressources[ressourceType] += amount

    def cancelUnit(self, unitId, constructionBuilding):
        if constructionBuilding < len(self.buildings):
            if unitId < len(self.buildings[constructionBuilding].unitBeingConstruct):
                unit = self.buildings[constructionBuilding].getUnitBeingConstructAt(unitId)
                self.adjustRessources(self.MINERAL, unit.buildCost[0])
                self.adjustRessources(self.GAS, unit.buildCost[1])
                self.ressources[self.FOOD] -= unit.buildCost[2]
                self.buildings[constructionBuilding].unitBeingConstruct.pop(unitId)

    def cancelTech(self, techId, constructionBuilding):
        if constructionBuilding < len(self.buildings):
            if techId < len(self.buildings[constructionBuilding].techsToResearch):
                tech = self.buildings[constructionBuilding].techsToResearch[techId][0]
                self.adjustRessources(self.MINERAL, tech.costMine)
                self.adjustRessources(self.GAS, tech.costGaz)
                tech.isAvailable = True
                if tech.child != None:
                    tech.child.isAvailable = False
                self.buildings[constructionBuilding].techsToResearch.pop(techId)

    def canAfford(self, minerals, gas, food, nuke=0):
        return self.ressources[self.MINERAL] >= minerals and self.ressources[self.GAS] >= gas and self.ressources[self.FOOD]+food <= self.MAX_FOOD and self.ressources[self.NUCLEAR] >= nuke

    def createUnit(self, unitType, constructionBuilding):
        if self.ressources[self.MINERAL] >= u.Unit.BUILD_COST[unitType][u.Unit.MINERAL] and self.ressources[self.GAS] >= u.Unit.BUILD_COST[unitType][u.Unit.GAS]:
            self.buildings[constructionBuilding].addUnitToQueue(unitType, self.game.galaxy, self.FORCE_BUILD_ACTIVATED)
            self.ressources[self.MINERAL] -= u.Unit.BUILD_COST[unitType][u.Unit.MINERAL]
            self.ressources[self.GAS] -= u.Unit.BUILD_COST[unitType][u.Unit.GAS]
            self.ressources[self.FOOD] += u.Unit.BUILD_COST[unitType][u.Unit.FOOD]
            self.buildings[constructionBuilding].flag.flagState = FlagState.BUILD_UNIT

    def makeGroundUnitsMove(self, units, position, action):
        print('makeGroundUnitMove dans player')
        for i in units:
            if i != '':
                self.units[int(i)].changeFlag(t.Target(position), action)

    def makeUnitsAttack(self, units, targetPlayer, targetUnit, type):
        for i in units:
            if i != '':
                if int(i) < len(self.units):
                    if type == "u":
                        self.units[int(i)].changeFlag(targetPlayer.units[targetUnit], FlagState.ATTACK)
                    else:
                        self.units[int(i)].changeFlag(targetPlayer.buildings[targetUnit], FlagState.ATTACK)

    def makeUnitLand(self, unitId, planet):
        self.units[unitId].changeFlag(planet, FlagState.LAND)

    def makeUnitLoad(self, units, landingZone):
        for i in units:
            if i != '':
                if int(i) < len(self.units):
                    self.units[int(i)].changeFlag(landingZone, FlagState.LOAD)
    
    def makeUnitsGather(self, units, astroObject):
        for i in units:
            if i != '':
                if int(i) < len(self.units):
                    self.units[int(i)].changeFlag(astroObject, FlagState.GATHER)
                
    def makeGroundUnitsGather(self, units, ressource):
        for i in units:
            if i != '':
                if int(i) < len(self.units):
                    self.units[int(i)].changeFlag(ressource, FlagState.GROUND_GATHER)

    def makeUnitGoToWormhole(self, units, wormhole):
        for i in units:
            if i != '':
                if int(i) < len(self.units):
                    self.units[int(i)].changeFlag(wormhole, FlagState.WORMHOLE)

    def selectMemory(self, selected):
        self.selectedObjects = []
        for i in self.listMemory[selected]:
            if i.isAlive:
                if isinstance(i, u.GroundUnit) or isinstance(i, b.GroundBuilding) or isinstance(i, b.LandingZone):
                    self.currentPlanet = self.game.galaxy.solarSystemList[i.sunId].planets[i.planetId]
                    self.selectedObjects.append(i)
                elif isinstance(i, u.SpaceUnit) or i.type == u.Unit.SCOUT or isinstance(i, b.SpaceBuilding) or isinstance(i, b.Mothership) or i.type == b.Building.UTILITY or i.type == b.Building.BARRACK:
                    if self.currentPlanet != None:
                        self.currentPlanet = None
                        self.game.parent.view.changeBackground('GALAXY')
                        self.game.parent.view.redrawMinimap()
                    self.selectedObjects.append(i)
            else:
                self.listMemory[selected].pop(self.listMemory[selected].index(i))
        if len(self.selectedObjects) > 0:
            if self.currentPlanet == None:
                self.camera.position = self.camera.ensurePositionIsInWorld([self.selectedObjects[0].position[0], self.selectedObjects[0].position[1]])
            else:
                self.camera.position = self.camera.ensurePositionIsOnPlanet([self.selectedObjects[0].position[0], self.selectedObjects[0].position[1]])
            

    def newMemory(self, selected):
        self.listMemory[selected] = []
        for i in self.selectedObjects:
            if isinstance(i, PlayerObject):
                self.listMemory[selected].append(i)

    def calculateFinalBuildingsScore(self):
        score = 0
        for b in self.buildings:
            score += b.SCORE_VALUE[b.type]
        return score

    def calculateFinalUnitsScore(self):
        score = 0
        for u in self.units:
            score += u.SCORE_VALUE[u.type]
        return score

    def calculateFinalDiplomacyScore(self):
        score = 0
        for i in self.diplomacies:
            if i == 'Ally':
                score += 100
        return score

    def calculateFinalRessourcesScore(self):
        score = self.ressources[self.MINERAL] + self.ressources[self.GAS]
        score += self.ressources[self.FOOD]*3
        score += self.ressources[self.NUCLEAR]*50
        return score

    def calculateFinalKilledScore(self):
        score = 0
        for u in self.units:
            score += u.getKilledCount()
        return score*50
    
    def makeFormation(self, units, galaxy, target = None, action = FlagState.MOVE):
        if len(units) > 2:
            #S'il n'y a pas de target de spÃ©cifiÃ©e comme lors du changement de formation
            if target == None:
                if int(units[0]) < len(self.units):
                    target = self.units[int(units[0])].flag.finalTarget.position
            #tuple qui contient les lignes qui peut contenir par ligne
            lineTaken=[]
            line=0
            #CoordonnÃ©es avant modification
            targetorig=[0,0]
            targetorig[0]=target[0]
            targetorig[1]=target[1]
            #Permet de savoir combien en x et en y je dois les sÃ©parer selon la grosseur
            #du plus gros unit dans les selectedObjects
            if int(units[0]) < len(self.units):
                unit =  self.units[int(units[0])]
                widths = [unit.SIZE[unit.type][0]]
                heights = [unit.SIZE[unit.type][1]]
                for i in range(0,len(units)-1):
                    if int(units[i]) < len(self.units):
                        unit = self.units[int(units[i])]
                        widths.append(unit.SIZE[unit.type][0])
                        heights.append(unit.SIZE[unit.type][1])
                width = max(widths)
                height = max(heights)
                #Formation en carrÃ© selon le nombre de unit qui se dÃ©place, OH YEAH
                if self.formation == self.SQUARE_FORMATION:
                    #tuple qui contient les units qui peut contenir par ligne
                    thatLine = []
                    lineTaken = []
                    #Nombre de ligne nÃ©cessaires pour faire la formation carrÃ©
                    numberOfLines = math.sqrt(len(units)-1)
                    if str(numberOfLines).split('.')[1] != '0':
                        numberOfLines+=1
                    math.trunc(float(numberOfLines))
                    numberOfLines = int(numberOfLines)
                    #Remplissage du tuple de chaque ligne pour crÃ©er la formation par des False
                    for l in range(0,numberOfLines):
                        thatLine = []
                        for k in range(0,numberOfLines):
                            thatLine.append(False)
                        lineTaken.append(thatLine)
                    #Maintenant on fait la vÃ©rification de chaque Unit pour les placer dans le carrÃ©
                    for i in range(0,len(units)-1):
                        goodPlace=False
                        line=0
                        while goodPlace==False:
                            for p in range(0,len(lineTaken[line])):
                                #Si la place n'est pas prise
                                if lineTaken[line][p]==False:
                                    lineTaken[line][p]=True
                                    target[0]=targetorig[0]+(p*width*1.2)
                                    if target[0] < -1*(galaxy.width/2)+(width):
                                        target[0] = -1*(galaxy.width/2)+width
                                    elif target[0] > (galaxy.width/2)-(width):
                                        target[0] = (galaxy.width/2)-width
                                    target[1]=targetorig[1]-(line*height*1.2)
                                    if target[1] < -1*(galaxy.height/2)+(height):
                                        target[1] = -1*(galaxy.height/2)+height
                                    goodPlace=True
                                    break
                            #Si le Unit n'a pas trouvÃ© sa place, on avance d'une ligne
                            if goodPlace==False:
                                line+=1
                        #Lorsqu'il a trouvÃ© sa place, on le fait bouger vers sa nouvelle target
                        if int(units[i]) < len(self.units):
                            self.units[int(units[i])].changeFlag(t.Target([target[0],target[1],0]),int(action))
                #Formation en triangle, FUCK YEAH
                elif self.formation == self.TRIANGLE_FORMATION:
                    #tuple qui contient le nombre de Unit par ligne
                    thatLine=[]
                    #tuple qui contient les X de la ligne prÃ©cÃ©dente
                    xLineBefore=[0,0,0,0,0,0,0,0,0,0,0,0]
                    #On initialise directement la premiÃ¨re ligne et on l'ajoute dans le tableau des lignes par
                    #la suite
                    thatLine.append([False])
                    lineTaken.append(thatLine[False])
                    xLineBefore[0] = target[0]
                    #AprÃ¨s, on fait chercher un endroit dans la formation pour chaque Unit
                    for i in range(0,len(units)-1):
                        goodPlace=False
                        line=0
                        while goodPlace==False:
                            for p in range(0,len(lineTaken[line])):
                                #S'il a trouvÃ© une place vide
                                if lineTaken[line][p]==False:
                                    lineTaken[line][p]=True
                                    if line != 0:
                                        if p==len(lineTaken[line-1]):
                                            target[0]=targetorig[0]+(p*width)
                                            #jerome ajoute ca ici la largeur du vaisseau
                                            if target[0] > (galaxy.width/2)-width:
                                                target[0] = target[0]-(target[0]-(galaxy.width/2)+width)
                                            xLineBefore[p] = target[0]
                                        else:
                                            target[0]=xLineBefore[p]-width
                                            if target[0] < -1*(galaxy.width/2)+(width/2):
                                                target[0] = xLineBefore[p]
                                            elif target[0] > (galaxy.width/2)-(width/2):
                                                target[0] = target[0]-(target[0]-(galaxy.width/2)+width)
                                            xLineBefore[p] = target[0]
                                    target[1]=targetorig[1]-(line*height)
                                    if target[1] < -1*(galaxy.height/2)+(height/2):
                                        target[1] = targetorig[1]
                                    goodPlace=True
                                    break
                            #S'il n'a pas trouvÃ© de place dans cette ligne
                            if goodPlace==False:
                                line+=1
                                #Si la prochaine ligne n'existe pas, on la crÃ©e
                                if (len(lineTaken)-1)<line:
                                    numberOfSpaces=1+line
                                    thatLine=[]
                                    for a in range(0,numberOfSpaces):
                                        thatLine.append(False)
                                    lineTaken.append(thatLine)
                        #Lorsqu'il a trouvÃ© sa place, on le fait bouger Ã  sa nouvelle Target  
                        if int(units[i]) < len(self.units):
                            self.units[int(units[i])].changeFlag(t.Target([target[0],target[1],0]),int(action))
        else:
            if int(units[0]) < len(self.units):
                self.units[int(units[0])].changeFlag(t.Target([target[0],target[1],0]),int(action))
        
#Represente la camera            
class Camera():
    def __init__(self, defaultPos, galaxy, player, width, height):
        self.defaultPos = defaultPos
        self.position = defaultPos
        self.screenCenter = (width/2,(height/2))
        self.screenWidth = width
        self.screenHeight = height
        self.galaxy = galaxy #reference a la galaxie
        self.player = player
        self.movingDirection = []
        self.recalculateDefault()

    #Pour replacer la position du dÃ©but sur le mothership
    def recalculateDefault(self):
        if self.defaultPos[0]-self.screenCenter[0] < (self.galaxy.width*-1)/2:
            self.position[0] = (self.galaxy.width*-1)/2+self.screenCenter[0]
        if self.defaultPos[0]+self.screenCenter[0] > self.galaxy.width/2:
            self.position[0] = (self.galaxy.width)/2-self.screenCenter[0]
        if self.defaultPos[1]-self.screenCenter[1] < (self.galaxy.height*-1)/2:
            self.position[1] = (self.galaxy.height*-1)/2+self.screenCenter[1]
        if self.defaultPos[1]+self.screenCenter[1] > self.galaxy.height/2:
            self.position[1] = (self.galaxy.height)/2-self.screenCenter[1]
        self.defaultPos = [self.position[0], self.position[1]]

    #Pour savoir si la position est dans le gameArea
    def inGameArea(self, position):
        if position[0] > self.position[0] - self.screenWidth/2 and position[0] < self.position[0] + self.screenWidth/2:
            if position[1] > self.position[1] - self.screenHeight/2 and position[1] < self.position[1] + self.screenHeight/2:
                return True
        return False

    def ensurePositionIsInWorld(self, position):
        if position[0] > self.galaxy.width/2 - self.screenWidth/2:
            position[0] = self.galaxy.width/2 - self.screenWidth/2
        elif position[0] < self.galaxy.width/2*-1 + self.screenWidth/2:
            position[0] = self.galaxy.width/2*-1 + self.screenWidth/2
        if position[1] > self.galaxy.height/2 - self.screenHeight/2:
            position[1] = self.galaxy.height/2 - self.screenHeight/2
        elif position[1] < self.galaxy.height/2*-1 + self.screenHeight/2:
            position[1] = self.galaxy.height/2*-1 + self.screenHeight/2
        return position

    def ensurePositionIsOnPlanet(self, position):
        if position[0] > w.Planet.WIDTH - self.screenWidth/2:
            position[0] = w.Planet.WIDTH - self.screenWidth/2
        elif position[0] < self.screenWidth/2:
            position[0] = self.screenWidth/2
        if position[1] > w.Planet.HEIGHT - self.screenHeight/2:
            position[1] = w.Planet.HEIGHT - self.screenHeight/2
        elif position[1] < self.screenHeight/2:
            position[1] = self.screenHeight/2
        return position

    #Pour calculer la distance entre la camera et un point
    def calcDistance(self, position):
        distX = position[0] - self.position[0]
        distY = position[1] - self.position[1]
        return [distX+self.screenCenter[0], distY+self.screenCenter[1]]
    
    #Pour calculer un point dans la galaxie a partir d'un point dans l'ecran
    def calcPointInWorld(self, x,y):
        dist = self.calcDistance([x,y])
        rX = self.position[0]-self.screenCenter[0]+x
        rY = self.position[1]-self.screenCenter[1]+y
        return [rX,rY,0]
    
    #Pour calculer un point sur la minimap a partir d'un point dans l'espace
    def calcPointOnMap(self, x, y):
        rX = x/200 * self.galaxy.width - self.galaxy.width/2
        rY = y/200 * self.galaxy.height - self.galaxy.height/2
        if rX < 0-self.galaxy.width/2+self.screenWidth/2:
            rX = 0-self.galaxy.width/2+self.screenWidth/2
        elif rX > self.galaxy.width/2-self.screenWidth/2:
            rX = self.galaxy.width/2-self.screenWidth/2
            
        if rY < 0-self.galaxy.height/2+self.screenHeight/2:
            rY = 0-self.galaxy.height/2+self.screenHeight/2
        elif rY > self.galaxy.height/2-self.screenHeight/2:
            rY = self.galaxy.height/2-self.screenHeight/2
        return [rX, rY]
		
    def calcPointOnPlanetMap(self, x, y):
        rX = x * self.player.currentPlanet.WIDTH / 200
        rY = y * self.player.currentPlanet.HEIGHT / 200
        if rX < 0 + self.screenWidth/2:
            rX = 0 + self.screenWidth/2
        elif rX > self.player.currentPlanet.WIDTH - self.screenWidth/2:
            rX = self.player.currentPlanet.WIDTH - self.screenWidth/2
        if rY < 0 + self.screenHeight/2:
            rY = 0 + self.screenHeight/2
        elif rY > self.player.currentPlanet.HEIGHT - self.screenHeight/2:
            rY = self.player.currentPlanet.HEIGHT - self.screenHeight/2
        return [rX, rY]
    
    #Pour calculer un point dans la galaxie a partir d'un point dans la minimap
    def calcPointMinimap(self,x ,y ):
        rX = x/200 * self.galaxy.width - self.galaxy.width/2
        rY = y/200 * self.galaxy.height - self.galaxy.height/2
        return [rX, rY]
    
    #Retourne Vrai si la position est visible par la camera en ce moment
    def isInFOV(self, position):
        if position[0] > self.position[0]-self.screenWidth/2-20 and position[0] < self.position[0]+self.screenWidth/2+20:
            if position[1] > self.position[1]-self.screenHeight/2-20 and position[1] < self.position[1]+self.screenHeight/2+20:
                return True
        return False

    def placeOnLanding(self, landingZone):
        planet = self.player.currentPlanet
        self.position = [landingZone.position[0], landingZone.position[1]]
        if self.position[0]-self.screenCenter[0] < 0:
            self.position[0] = 0 + self.screenCenter[0]
        if self.position[0] + self.screenCenter[0] > planet.WIDTH:
            self.position[0] = planet.WIDTH-self.screenCenter[0]
        if self.position[1] - self.screenCenter[1] < 0:
            self.position[1] = 0+self.screenCenter[1]
        if self.position[1] + self.screenCenter[1] > planet.HEIGHT:
            self.position[1] = planet.HEIGHT - self.screenCenter[1]

    def placeOverPlanet(self):
        if self.position[0]-self.screenCenter[0] < (self.galaxy.width*-1)/2:
            self.position[0] = (self.galaxy.width*-1)/2+self.screenCenter[0]
        if self.position[0]+self.screenCenter[0] > self.galaxy.width/2:
            self.position[0] = (self.galaxy.width)/2-self.screenCenter[0]
        if self.position[1]-self.screenCenter[1] < (self.galaxy.height*-1)/2:
            self.position[1] = (self.galaxy.height*-1)/2+self.screenCenter[1]
        if self.position[1]+self.screenCenter[1] > self.galaxy.height/2:
            self.position[1] = (self.galaxy.height)/2-self.screenCenter[1]
    
    
    
    #Deplace la camera selon le contenu de la liste movingDirection
    def move(self):
        if self.player.currentPlanet == None:
            if 'LEFT' in self.movingDirection:
                if self.position[0] > (self.galaxy.width*-1)/2+self.screenCenter[0]:
                    self.position[0]-=20
            elif 'RIGHT' in self.movingDirection:
                if self.position[0] < self.galaxy.width/2 - self.screenCenter[0]:
                    self.position[0]+=20
            if 'UP' in self.movingDirection:
                if self.position[1] > (self.galaxy.height*-1)/2 + self.screenCenter[1]:
                    self.position[1]-=20
            elif 'DOWN' in self.movingDirection:
                if self.position[1] < self.galaxy.height/2 - self.screenCenter[1]:
                    self.position[1]+=20
        else:
            planet = self.player.currentPlanet
            if 'LEFT' in self.movingDirection:
                if self.position[0] > 0 + self.screenCenter[0]:
                    self.position[0]-=20
                else:
                    self.position[0] = self.screenCenter[0]
            elif 'RIGHT' in self.movingDirection:
                if self.position[0] < planet.WIDTH - self.screenCenter[0]:
                    self.position[0]+=20
                else:
                    self.position[0] = planet.WIDTH - self.screenCenter[0]
            if 'UP' in self.movingDirection:
                if self.position[1] > 0 + self.screenCenter[1]:
                    self.position[1]-=20
                else:
                    self.position[1] = self.screenCenter[1]
            elif 'DOWN' in self.movingDirection:
                if self.position[1] < planet.HEIGHT - self.screenCenter[1]:
                    self.position[1]+=20
                else:
                    self.position[1] = planet.HEIGHT - self.screenCenter[1]
