# -*- coding: UTF-8 -*-
#import World as w
import Player as p
import Target as t
import Unit as u
from World import *
from Building import *
from View import*
from Helper import *
from Flag import *
import math
from time import time

class Game():
    def __init__(self, controller):
        self.parent = controller
        self.players = []
        self.playerId = 0
        self.mess = []
        self.changes = []
        self.idTradeWith = self.playerId
        self.tradePage=-1
        self.isMasterTrade=False
        self.multiSelect = False

    def action(self):
        self.players[self.playerId].camera.move()
        self.parent.view.gameArea.delete('enemyRange')
        for p in self.players:
            if p.isAlive:
                p.action()
        return self.players[self.playerId].isAlive

    def start(self, players, seed, taille):
        self.galaxy=w.Galaxy(len(players), seed)
        self.players = players
        for i in self.players:
            startPos = self.galaxy.getSpawnPoint()
            i.addBaseUnits(startPos) 
        self.players[self.playerId].addCamera(self.galaxy, taille)

    # Pour créer une notification qui vient du serveur
    def makeNotification(self, actionPlayerId, target):
        #target[0] = c'est le id du joueur qui doit recevoir la notification
        #target[1] = c'est le id du unit/building qui va faire l'action
        #target[2] = c'est le type de l'action (ATTACKED_UNIT, ATTACKED_BUILDING, ALLIANCE,...)
        #self.parent.pushChange(None, Flag(None,[attackedUnit.owner,self.players[attackedUnit.owner].units.index(attackedUnit), t.Notification.ATTACKED_UNIT],FlagState.NOTIFICATION))
        #pushChange= (None, Flag(None,[idJoueurQuiDoitLeRecevoir,idUnitQuiEstVisé,FlagDeLaNotification],FlagState.NOTIFICATION)
        player = self.players[target[0]]
        actionPlayerName = self.players[actionPlayerId].name
        addIt = True
        notif = None
        if target[2] == t.Notification.ATTACKED_UNIT:
            for i in player.notifications:
                if i.position == player.units[target[1]].position and i.actionPlayerName == actionPlayerName:
                    addIt = False
            if addIt:
                #Tu ajoutes seulement le 4e paramètre si tu en as besoin, le nom de l'autre joueur
                notif = t.Notification(player.units[target[1]].position, target[2], actionPlayerName)
        elif target[2] == t.Notification.ATTACKED_BUILDING:
            for i in player.notifications:
                if i.position == player.buildings[target[1]].position and i.actionPlayerName == actionPlayerName:
                    addIt = False
            if addIt:
                notif = t.Notification(player.buildings[target[1]].position, target[2], actionPlayerName)
        if notif != None:
            player.notifications.append(notif)

    # Pour changer le flag des unités selectionne pour la construction        
    def setBuildingFlag(self,x,y, type, sunId=0, planetId=0):
        units = ''
        #Si plusieurs unit�s sont s�lectionn�es, on les ajoute toutes dans le changement � envoyer
        for i in self.players[self.playerId].selectedObjects:
            if i.type in (i.SCOUT, i.GROUND_BUILDER_UNIT):
                units+= str(self.players[self.playerId].units.index(i))+","
        if self.players[self.playerId].ressources[0] >= Building.COST[type][0] and self.players[self.playerId].ressources[1] >= Building.COST[type][1]:
            if Building.INSPACE[type] == True:
                self.parent.pushChange(units, Flag((type,0),t.Target([x,y,0]),FlagState.BUILD))
            else:
                self.parent.pushChange(units, Flag((type,sunId,planetId),t.Target([x,y,0]),FlagState.BUILD))

    def buildBuilding(self, playerId, target, flag, unitIndex, type, sunId=0, planetId=0):
        #Condition de construction
        wp = None
        if self.checkIfCanBuild((target[0], target[1],0), type):
            player = self.players[playerId]
            if player.ressources[0] >= Building.COST[type][0] and player.ressources[1] >= Building.COST[type][1]:
                player.ressources[0] -= Building.COST[type][0]
                player.ressources[1] -= Building.COST[type][1]
                if type == Building.WAYPOINT:
                    wp = Waypoint(Building.WAYPOINT, [target[0],target[1],0], playerId)
                    wp.MAX_SHIELD = player.BONUS[player.BUILDING_SHIELD_BONUS]
                    wp.shield = wp.MAX_SHIELD
                elif type == Building.TURRET:
                    wp = Turret(Building.TURRET, [target[0],target[1],0], playerId)
                    wp.MAX_SHIELD = player.BONUS[player.BUILDING_SHIELD_BONUS]
                    wp.shield = wp.MAX_SHIELD
                elif type == Building.FARM:
                    wp = Farm(Building.FARM, [target[0],target[1],0], playerId, sunId, planetId)
                    wp.MAX_SHIELD = player.BONUS[player.BUILDING_SHIELD_BONUS]
                    wp.shield = wp.MAX_SHIELD
                    wp.planet = self.galaxy.solarSystemList[sunId].planets[planetId]
                    self.galaxy.solarSystemList[sunId].planets[planetId].buildings.append(wp)
            if wp != None:
                self.players[playerId].buildings.append(wp)
                for i in unitIndex:
                    if i != '':
                        self.players[playerId].units[int(i)].changeFlag(wp,flag)

    def resumeBuildingFlag(self,building):
        units = ''
        for i in self.players[self.playerId].selectedObjects:
            if i.type in (i.SCOUT, i.GROUND_BUILDER_UNIT):
                units+= str(self.players[self.playerId].units.index(i))+","
        if not building.finished:
            self.parent.pushChange(units, Flag(i,building,FlagState.FINISH_BUILD))                          

    def resumeBuilding(self, playerId, building, unitIndex):
        for i in unitIndex:
            if i != '':
                self.players[playerId].units[int(i)].changeFlag(self.players[playerId].buildings[building],FlagState.BUILD)

    #Pour changer le flag des unites selectionne pour le deplacement    
    def setMovingFlag(self,x,y):
        units = ''
        send = False
        if y > self.galaxy.height/2:
            y = self.galaxy.height/2-15
        #Si plusieurs unités sont sélectionnées, on les ajoute toutes dans le changement à envoyer
        for i in self.players[self.playerId].selectedObjects:
            print("1")
            if isinstance(i, u.Unit):              
                units += str(self.players[self.playerId].units.index(i)) + ","
                print("2")
                send = True
        if send:
            print("3")

            self.parent.pushChange(units, Flag(i,t.Target([x,y,0]),FlagState.MOVE))
            
    def setGroundMovingFlag(self,x,y):
        units = ''
        #Si plusieurs unités sont sélectionnées, on les ajoute toutes dans le changement à envoyer
        for i in self.players[self.playerId].selectedObjects:
            if isinstance(i, u.Unit):
                units += str(self.players[self.playerId].units.index(i))+ ","
        self.parent.pushChange(units, Flag(t.Target([0,0,0]), t.Target([x,y,0]),FlagState.GROUND_MOVE))

    def setDefaultMovingFlag(self,x,y, unit):
        units = ''
        send = False
        #Si plusieurs unités sont sélectionnées, on les ajoute toutes dans le changement à envoyer            
        units += str(self.players[self.playerId].units.index(unit)) + ","
        self.parent.pushChange(units, Flag(unit,t.Target([x,y,0]),FlagState.MOVE))
    
    #Pour changer le flag des unites selectionne pour l'arret
    def setStandbyFlag(self):
        units = ""
        #Si plusieurs unités sont sélectionnées, on les ajoute toutes dans le changement à envoyer
        for i in self.players[self.playerId].selectedObjects:
            if isinstance(i, u.Unit):
                units += str(self.players[self.playerId].units.index(i)) + ","
        if units != "":
            self.parent.pushChange(units, Flag(i,t.Target([0,0,0]),FlagState.STANDBY))

    def setAStandByFlag(self, unit):
        units = str(self.players[self.playerId].units.index(unit)) + ","
        self.parent.pushChange(units, Flag(i,t.Target([0,0,0]),FlagState.STANDBY))

    def setPatrolFlag(self, pos):
        units = ''
        send = False
        #Si plusieurs unités sont sélectionnées, on les ajoute toutes dans le changement à envoyer
        for i in self.players[self.playerId].selectedObjects:
            if isinstance(i, u.Unit):
                units += str(self.players[self.playerId].units.index(i)) + ","
                send = True
        if send:
            self.parent.pushChange(units, Flag(i,t.Target([pos[0],pos[1],0]),FlagState.PATROL))
            
    #Pour changer le flag des unités sélectionnés pour attaquer        
    def setAttackFlag(self, attackedUnit):
        attacking = True
        if attacking:
            units = ""
            for i in self.players[self.playerId].selectedObjects:
                if isinstance(i, u.SpaceAttackUnit):
                    if isinstance(attackedUnit, u.Unit) :
                        if attackedUnit.type == u.Unit.TRANSPORT:
                            if not attackedUnit.landed:
                                units += str(self.players[self.playerId].units.index(i)) + ","
                        else:
                            units += str(self.players[self.playerId].units.index(i)) + ","
                    else:
                        units += str(self.players[self.playerId].units.index(i)) + ","
                elif isinstance(i, u.GroundAttackUnit):
                    units += str(self.players[self.playerId].units.index(i)) + ","
                else:
                    self.parent.pushChange((str(self.players[self.playerId].units.index(i)) + ","), Flag(i,t.Target([attackedUnit.position[0],attackedUnit.position[1],0]),FlagState.MOVE))
            if units != "":
                self.parent.pushChange(units, Flag(i,attackedUnit,FlagState.ATTACK))
                if isinstance(attackedUnit,u.Unit):
                    self.parent.pushChange(None, Flag(None,[attackedUnit.owner,self.players[attackedUnit.owner].units.index(attackedUnit), t.Notification.ATTACKED_UNIT],FlagState.NOTIFICATION))
                else:
                    self.parent.pushChange(None, Flag(None,[attackedUnit.owner,self.players[attackedUnit.owner].buildings.index(attackedUnit), t.Notification.ATTACKED_BUILDING],FlagState.NOTIFICATION))


    def setAnAttackFlag(self, attackedUnit, unit):
        units = ""
        if attackedUnit.type == u.Unit.TRANSPORT:
            if not attackedUnit.landed:
                unit.attackcount = unit.AttackSpeed
                units += str(self.players[unit.owner].units.index(unit)) + ","
        else:
            unit.attackcount = unit.AttackSpeed
            units += str(self.players[unit.owner].units.index(unit)) + ","
        if units != "":
            self.pushChange(units, Flag(unit.owner,attackedUnit,FlagState.ATTACK))

    def makeUnitsAttack(self, playerId, units, targetPlayer, targetUnit, type):
        self.players[playerId].makeUnitsAttack(units, self.players[targetPlayer], targetUnit, type)

    def killUnit(self, killedIndexes, hasToKill = True):
        if hasToKill:
            self.players[killedIndexes[1]].killUnit(killedIndexes)
        for play in self.players:
            play.checkIfIsAttacking(killedIndexes)

    def removeLandingZoneFromPlanet(self, landingZone):
        planet = self.galaxy.solarSystemList[landingZone.sunId].planets[landingZone.planetId]
        if landingZone in planet.landingZones:
            planet.landingZones.remove(landingZone)

    def setBuyTech(self, techType, index):
        self.parent.pushChange(index, Flag(techType,0,FlagState.BUY_TECH))

    def buyTech(self, playerId, techType, index):
        player = self.players[playerId]
        techTree = player.techTree
        if techType == "Button_Buy_Unit_Tech":
            tech = techTree.getTechs(techTree.UNITS)[index]
        elif techType == "Button_Buy_Building_Tech":
            tech = techTree.getTechs(techTree.BUILDINGS)[index]
        elif techType == "Button_Buy_Mothership_Tech":
            tech = techTree.getTechs(techTree.MOTHERSHIP)[index]
        if player.ressources[0] >= tech.costMine and player.ressources[1] >= tech.costGaz:
            if techType == "Button_Buy_Unit_Tech":
                tech = techTree.buyUpgrade(techTree.getTechs(techTree.UNITS)[index].name,techTree.UNITS, tech)
            elif techType == "Button_Buy_Building_Tech":
                tech = techTree.buyUpgrade(techTree.getTechs(techTree.BUILDINGS)[index].name,techTree.BUILDINGS, tech)
            elif techType == "Button_Buy_Mothership_Tech":
                tech = techTree.buyUpgrade(techTree.getTechs(techTree.MOTHERSHIP)[index].name,techTree.MOTHERSHIP, tech)
            player.ressources[0] -= tech.costMine
            player.ressources[1] -= tech.costGaz
            if tech.effect == 'D':
                player.BONUS[player.ATTACK_DAMAGE_BONUS] = tech.add
            elif tech.effect == 'S':
                player.BONUS[player.MOVE_SPEED_BONUS] = tech.add
            elif tech.effect == 'AS':
                player.BONUS[player.ATTACK_SPEED_BONUS] = tech.add
            elif tech.effect == 'AR':
                player.BONUS[player.ATTACK_RANGE_BONUS] = tech.add
            elif tech.effect == 'VR':
                player.BONUS[player.VIEW_RANGE_BONUS] = tech.add
            elif tech.effect == 'BB':
                player.BONUS[player.BUILDING_SHIELD_BONUS] = tech.add
                for b in player.buildings:
                    if not isinstance(b, Mothership):
                        b.MAX_SHIELD = tech.add
                        b.shield = tech.add
            elif tech.effect == 'BM':
                player.motherShip.MAX_SHIELD = tech.add
                player.motherShip.shield = player.motherShip.MAX_SHIELD
                
            player.changeBonuses()
        
    def setGatherFlag(self,ship,ressource):
        units = str(self.players[self.playerId].units.index(ship)) + ","
        self.parent.pushChange(units, Flag(t.Target([0,0,0]),ressource, FlagState.GATHER))

    def makeUnitsGather(self, playerId, unitsId, solarSystemId, astroObjectId, astroObjectType):
        if astroObjectType == AstronomicalObject.NEBULA:
            astroObject = self.galaxy.solarSystemList[solarSystemId].nebulas[astroObjectId]
        elif astroObjectType == AstronomicalObject.ASTEROID:
            astroObject = self.galaxy.solarSystemList[solarSystemId].asteroids[astroObjectId]
        elif astroObjectType == b.Building.WAYPOINT:
            astroObject = self.players[playerId].buildings[astroObjectId]
        else:
            astroObject = self.players[playerId].motherShip
        self.players[playerId].makeUnitsGather(unitsId, astroObject)

    def setGroundGatherFlag(self, ship, ressource):
        units = str(self.players[self.playerId].units.index(ship)) + ","
        self.parent.pushChange(units, Flag(t.Target([0,0,0]), ressource, FlagState.GROUND_GATHER))

    def makeGroundUnitsGather(self, playerId, unitsId, ressourceId, planetId, sunId, ressourceType):
        if ressourceType == Planet.MINERAL:
            ressource = self.galaxy.solarSystemList[sunId].planets[planetId].minerals[ressourceId]
        elif ressourceType == Planet.GAZ:
            ressource = self.galaxy.solarSystemList[sunId].planets[planetId].gaz[ressourceId]
        else:
            ressource = self.galaxy.solarSystemList[sunId].planets[planetId].landingZones[ressourceId]
        if isinstance(ressource, LandingZone):
            if ressource.LandedShip == None:
                self.players[playerId].makeGroundUnitsGather(unitsId, ressource)
        else:
            self.players[playerId].makeGroundUnitsGather(unitsId, ressource)

    #Trade entre joueurs
    def setTradeFlag(self, item, playerId2, quantite):
        for i in items:
            self.parent.pushChange(playerId2, Flag(i, quantite[items.index(i)], FlagState.TRADE))

    def askTrade(self, name, index, mode):
        idOtherPlayer = -1
        for p in self.players:
            if p.isAlive:
                if p.name == self.parent.view.menuModes.variableTrade.get():
                    idOtherPlayer = p.id
                    break
        if idOtherPlayer != -1:
            self.parent.pushChange(idOtherPlayer, Flag(1, "askTrade", FlagState.TRADE))
            self.tradePage=1
            self.idTradeWith=idOtherPlayer
            self.parent.view.ongletTradeWaiting()

    def stopTrade(self):
        self.parent.pushChange(self.idTradeWith, Flag(5, "stopTrade", FlagState.TRADE))

    def startTrade(self, answer, id1):
        if answer == True:
            self.parent.pushChange(id1, Flag(2, "startTrade", FlagState.TRADE))
        else:
            self.parent.pushChange(id1, Flag(3, "deniedTrade", FlagState.TRADE))
            self.parent.view.ongletTradeChoicePlayer()

    def confirmTradeQuestion(self, id2):
        try:
            if int(self.parent.view.menuModes.spinMinerals1.get()) <= self.players[self.playerId].ressources[0] and int(self.parent.view.menuModes.spinGaz1.get()) <= self.players[self.playerId].ressources[1]:
                if int(self.parent.view.menuModes.spinMinerals2.get()) <= self.players[self.idTradeWith].ressources[0] and int(self.parent.view.menuModes.spinGaz2.get()) <= self.players[self.idTradeWith].ressources[1]:
                    self.parent.pushChange(id2, Flag(4, self.parent.view.menuModes.spinMinerals1.get()+','+self.parent.view.menuModes.spinMinerals2.get()+','+self.parent.view.menuModes.spinGaz1.get()+','+self.parent.view.menuModes.spinGaz2.get(), FlagState.TRADE))
                    self.tradePage=1
                    self.parent.view.ongletTradeWaiting()
        except:
            print('du texte dans les spins de trade')
            
    def confirmTrade(self, answer, id1, min1, min2, gaz1, gaz2):
        if answer == True:
            self.parent.pushChange(self.idTradeWith, Flag("m", min1, FlagState.TRADE))
            self.parent.pushChange(self.playerId, Flag("m", min2+','+str(self.idTradeWith), FlagState.TRADE))
            self.parent.pushChange(self.idTradeWith, Flag("g", gaz1, FlagState.TRADE))
            self.parent.pushChange(self.playerId, Flag("g", gaz2+','+str(self.idTradeWith), FlagState.TRADE))
        else:
            self.parent.pushChange(id1, Flag(3, "deniedTrade", FlagState.TRADE))
            self.tradePage=-1
            self.parent.view.ongletTradeChoicePlayer()

    def tradeActions(self, actionPlayerId, target, unitIndex):
        if target[0] == '1':
            if int(unitIndex[0])==self.playerId:
                self.tradePage=3
                self.idTradeWith=actionPlayerId
                self.parent.view.ongletTradeYesNoQuestion(actionPlayerId)
        elif target[0] == '2':
            if int(unitIndex[0])==self.playerId or actionPlayerId == self.playerId:
                if int(unitIndex[0])==self.playerId:
                    self.isMasterTrade=True
                    self.parent.view.ongletTrade(self.playerId,self.idTradeWith)
                else:
                    self.isMasterTrade=False
                    self.parent.view.ongletTrade(self.idTradeWith,self.playerId)
                self.tradePage=2                       
        elif target[0] == '3':
            if int(unitIndex[0])==self.playerId:
                self.isMasterTrade=False
                self.tradePage=-1
                self.idTradeWith=self.playerId
                self.parent.view.ongletTradeNoAnswer()
        elif target[0] == '4':
            if int(unitIndex[0])==self.playerId:
                self.tradePage=4
                self.toTrade = (target[1],target[2],target[3],target[4])
                self.parent.view.ongletTradeAskConfirm(actionPlayerId,self.toTrade[0],self.toTrade[1],self.toTrade[2],self.toTrade[3])
        elif target[0] == '5':
            if int(unitIndex[0])==self.playerId or actionPlayerId == self.playerId:
                self.isMasterTrade=False
                self.tradePage=-1
                self.idTradeWith=self.playerId
                self.parent.view.ongletTradeCancel()
        elif target[0] == 'm' or target[0] == 'g':
            if target[0] == 'm':
                ressourceType = p.Player.MINERAL
            elif target[0] == 'g':
                ressourceType = p.Player.GAS
            if int(unitIndex[0]) != actionPlayerId:
                self.trade(actionPlayerId, int(unitIndex[0]), ressourceType, int(target[1]))
            else:
                self.trade(int(target[2]), actionPlayerId, ressourceType, int(target[1]))
            self.isMasterTrade=False
            self.tradePage=-1
            self.idTradeWith=self.playerId
            self.parent.view.ongletTradeYesAnswer()

    
    def setLandingFlag(self, unit, planet):
        solarsystemId = 0
        planetIndex = 0
        for i in self.galaxy.solarSystemList:
            for j in i.planets:
                if j == planet:
                    solarsystemId = self.galaxy.solarSystemList.index(i)
                    planetIndex = self.galaxy.solarSystemList[solarsystemId].planets.index(planet)
        self.parent.pushChange(str(self.players[self.playerId].units.index(unit)), (solarsystemId, planetIndex, FlagState.LAND))

    def makeUnitLand(self, playerId, unitId, solarSystemId, planetId):
        #if playerId == self.playerId:
        planet = self.galaxy.solarSystemList[solarSystemId].planets[planetId]
        self.players[playerId].makeUnitLand(unitId, planet)

    def setRallyPointPosition(self, pos):
        self.parent.pushChange(self.players[self.playerId].getSelectedBuildingIndex(), Flag(finalTarget = pos, flagState = FlagState.CHANGE_RALLY_POINT))

    def setChangeFormationFlag(self, formation):
        units = ""
        for i in self.players[self.playerId].selectedObjects:           
            units += str(self.players[self.playerId].units.index(i)) + ","
        self.parent.pushChange(units, Flag(i,formation,FlagState.CHANGE_FORMATION))
        
    def setTakeOffFlag(self, ship, planet):
        planetId = 0
        sunId = 0
        shipId = self.players[self.playerId].units.index(ship)
        for i in self.galaxy.solarSystemList:
            for j in i.planets:
                if j == planet:
                    planetId = i.planets.index(j)
                    sunId = self.galaxy.solarSystemList.index(i)
        self.parent.pushChange(shipId,(planetId, sunId, 'TAKEOFF'))

    def setLoadFlag(self, unit, landingZone):
        units = ""
        for i in unit:
            if isinstance(i, u.GroundUnit):
                units += str(self.players[self.playerId].units.index(i)) + ","
        self.parent.pushChange(units, Flag(unit, landingZone, FlagState.LOAD))

    def loadUnit(self, units, planetId, sunId, playerId):
        planet = self.galaxy.solarSystemList[sunId].planets[planetId]
        landingZone = planet.getLandingSpot(playerId)
        if landingZone != None:
            self.players[playerId].makeUnitLoad(units, landingZone)

    def unload(self):
        zone = self.players[self.playerId].getShipToUnload()
        if zone != None:
            self.parent.pushChange(zone, 'UNLOAD')

    def makeZoneUnload(self, zoneId, playerId, planetId, sunId):
        landingZone = self.galaxy.solarSystemList[sunId].planets[planetId].landingZones[zoneId]
        planet = self.galaxy.solarSystemList[sunId].planets[planetId]
        units = landingZone.LandedShip.units
        for i in units:
            position = [landingZone.position[0] + 40, landingZone.position[1] + 5 * self.players[playerId].units.index(i)]
            i.land(planet, position)
        del landingZone.LandedShip.units[:]

    #Trade entre joueurs
    def setTradeFlag(self, item, playerId2, quantite):
        for i in items:
            self.parent.pushChange(playerId2, Flag(i, quantite[items.index(i)], FlagState.TRADE))

    #Pour ajouter une unit
    def addUnit(self, unitType):
        mineralCost = u.Unit.BUILD_COST[unitType][0]
        gazCost = u.Unit.BUILD_COST[unitType][1]
        foodCost = u.Unit.BUILD_COST[unitType][2]
        if self.players[self.playerId].canAfford(mineralCost, gazCost, foodCost):
            self.parent.pushChange(self.players[self.playerId].getSelectedBuildingIndex(),Flag(finalTarget = unitType, flagState = FlagState.CREATE))

    def createUnit(self, player,constructionUnit, unitType):
        mineralCost = u.Unit.BUILD_COST[unitType][0]
        gazCost = u.Unit.BUILD_COST[unitType][1]
        foodCost = u.Unit.BUILD_COST[unitType][2]
        if self.players[player].canAfford(mineralCost, gazCost, foodCost):
            self.players[player].createUnit(unitType, constructionUnit)

    def sendCancelUnit(self, unit):
        self.parent.pushChange(self.players[self.playerId].getSelectedBuildingIndex(), Flag(finalTarget = unit, flagState = FlagState.CANCEL_UNIT))

    def cancelUnit(self, player, unit, constructionBuilding):
        self.players[player].cancelUnit(unit, constructionBuilding)
    
    #Pour effacer un Unit
    def eraseUnit(self):
        if len(self.players[self.playerId].selectedObjects) > 0:
            if isinstance(self.players[self.playerId].selectedObjects[len(self.players[self.playerId].selectedObjects)-1], u.Unit):
                self.parent.pushChange(self.players[self.playerId].units.index(self.players[self.playerId].selectedObjects[len(self.players[self.playerId].selectedObjects)-1]), Flag(None,None,FlagState.DESTROY))
                
    #Pour effacer tous les units
    def eraseUnits(self, playerId=None):
        if playerId == None:
            playerId = self.playerId
        #self.parent.pushChange(playerId, Flag(None,playerId,FlagState.DESTROY_ALL))

    def killPlayer(self, playerId):
        self.players[playerId].kill()
        if playerId == self.playerId:
            self.parent.removePlayer()
            self.players[self.playerId].selectedObjects = []
        if playerId == 0 or playerId == self.playerId:
            self.parent.endGame()
    
    def trade(self, player1, player2, ressourceType, amount):
        self.players[player1].adjustRessources(ressourceType, amount)
        self.players[player2].adjustRessources(ressourceType, amount*-1)

    def adjustRessources(self, player, ressourceType, amount):
        self.players[player].adjustRessources(ressourceType, amount)

    def demandAlliance(self, playerId, otherPlayerId, newStatus):
        self.players[playerId].changeDiplomacy(otherPlayerId, newStatus)
        if otherPlayerId == self.playerId:
            #Dire au joueur que quelqu'un a changé de diplomacie avec toi (système de notifications)
            if newStatus == "Ally":
                if self.players[otherPlayerId].isAlly(playerId):
                    self.players[self.playerId].notifications.append(t.Notification((-10000,-10000,-10000),t.Notification.ALLIANCE_ALLY,self.players[playerId].name))
                else:
                    self.players[self.playerId].notifications.append(t.Notification((-10000,-10000,-10000),t.Notification.ALLIANCE_DEMAND_ALLY,self.players[playerId].name))
            else:
                self.players[self.playerId].notifications.append(t.Notification((-10000,-10000,-10000),t.Notification.ALLIANCE_ENNEMY,self.players[playerId].name))
        elif playerId == self.playerId:
            if newStatus == "Ally" and self.players[otherPlayerId].isAlly(playerId):
                    self.players[self.playerId].notifications.append(t.Notification((-10000,-10000,-10000),t.Notification.ALLIANCE_ALLY,self.players[otherPlayerId].name))

    def getPlayerId(self, player):
        for i in self.players:
            if i.name == player:
                player = i.id
                break
        return player
    
    def isAllied(self, player1Id, player2Id):
        if self.players[player1Id].diplomacies[player2Id] == "Ally":
            return True
        else:
            return False

    def getAllies(self):
        allies = []
        for p in self.players:
            if p != self.players[self.playerId]:
                if p.isAlly(self.playerId):
                    allies.append(p.name)
        return allies

   #Pour selectionner une unit
    def selectUnitEnemy(self, posSelected):
        if self.players[self.playerId].currentPlanet == None:
            if len(self.players[self.playerId].selectedObjects) > 0:
                    for i in self.players:
                        if i.isAlive:
                            if i.id != self.playerId and self.players[self.playerId].isAlly(i.id) == False:
                                for j in i.units:
                                    if j.select(posSelected):
                                        self.setAttackFlag(j)

    def checkIfEnemyInRange(self, unit, onPlanet = False, planetId = -1, solarSystemId = -1):
        for pl in self.players:
            if pl.isAlive:
                if pl.id != unit.owner and self.players[unit.owner].isAlly(pl.id) == False:
                    enemyUnit = pl.hasUnitInRange(unit.position, unit.range, onPlanet, planetId, solarSystemId)
                    if enemyUnit != None:
                        self.attackEnemyInRange(unit, enemyUnit)
                        break
        if onPlanet:
            planet = self.galaxy.solarSystemList[solarSystemId].planets[planetId]
            enemyZone = planet.hasZoneInRange(unit.position, unit.range)
            if enemyZone != None and enemyZone.ownerId != unit.owner and not self.players[unit.owner].isAlly(enemyZone.ownerId):
                self.attackEnemyInRange(unit, enemyZone)
                                        
    def attackEnemyInRange(self, unit, unitToAttack):
        unit.changeFlag(unitToAttack, FlagState.ATTACK)

    def checkIfCanBuild(self, position, type):
        start = (position[0]-(Building.SIZE[type][0]/2),position[1]-(Building.SIZE[type][1]/2),0)
        end = (position[0]+(Building.SIZE[type][0]/2),position[1]+(Building.SIZE[type][1]/2),0)
        for p in self.players:
            for b in p.buildings:
                if isinstance(b, GroundBuilding):
                    if self.players[self.playerId].selectedObjects[0].planet == b.planet:
                        if b.selectIcon(start, end) != None:
                            return False
        if self.getCurrentPlanet() == None:
            for i in self.galaxy.solarSystemList:
                if i.over(start, end):
                    return False
        else:
            if self.getCurrentPlanet().groundOver(start, end):
                return False
        return True
    
    def selectUnitByType(self, typeId):
        self.players[self.playerId].selectUnitsByType(typeId)
    
    def select(self, posSelected):
        player = self.players[self.playerId]
        if player.currentPlanet == None:
            if not self.multiSelect:
                player.selectUnit(posSelected)
            else:
                player.multiSelectUnit(posSelected)
            spaceObj = self.galaxy.select(posSelected)
            if isinstance(spaceObj, w.Planet):
                player.selectPlanet(spaceObj)
            else:
                player.selectObject(spaceObj, False)
        else:
            planet = player.currentPlanet
            groundObj = planet.groundSelect(posSelected)
            player.selectObject(groundObj, False)
        self.parent.changeActionMenuType(View.MAIN_MENU)
    
    def selectObjectFromMenu(self, unitId):
        self.players[self.playerId].selectObjectFromMenu(unitId)
    
    def selectAll(self, posSelected):
        self.players[self.playerId].selectAll(posSelected)
        self.parent.changeActionMenuType(View.MAIN_MENU)

    def rightClic(self, pos):
        empty = True
        if self.getCurrentPlanet() == None:
            clickedObj = self.galaxy.select(pos)
            if clickedObj == None:
                for i in self.players:
                    clickedObj = i.rightClic(pos, self.playerId)
                    if clickedObj != None:
                        break
            unit = self.players[self.playerId].getFirstUnit()
            if unit != None:
                if clickedObj != None:
                    if unit.type == unit.TRANSPORT:
                        if isinstance(clickedObj, w.Planet):
                            self.setLandingFlag(unit, clickedObj)
                    elif unit.type == unit.CARGO:
                        if isinstance(clickedObj, w.AstronomicalObject):
                            self.setGatherFlag(unit, clickedObj)
                        elif isinstance(clickedObj, Mothership) or isinstance(clickedObj, Waypoint):
                            if clickedObj.owner == self.playerId:
                                self.setGatherFlag(unit, clickedObj)
                    elif unit.type == unit.ATTACK_SHIP:
                        if isinstance(clickedObj, u.Unit) or isinstance(clickedObj, Building):
                            if clickedObj.owner != self.playerId:
                                self.setAttackFlag(clickedObj)
                    elif unit.type == unit.SCOUT:
                        if isinstance(clickedObj, Waypoint):
                            if clickedObj.owner == self.playerId:
                                if clickedObj.finished == False:
                                    self.resumeBuildingFlag(clickedObj)
                else:
                    if isinstance(unit, Mothership) or isinstance(unit, LandingZone):
                        self.setRallyPointPosition(pos)
                    else:
                        self.setMovingFlag(pos[0], pos[1])
        else:
            unit = self.players[self.playerId].getFirstUnit()
            clickedObj = self.getCurrentPlanet().groundSelect(pos)
            if unit != None:
                if clickedObj != None:
                    if unit.type == unit.GROUND_GATHER:
                        if isinstance(clickedObj, w.MineralStack) or isinstance(clickedObj, w.GazStack) or isinstance(clickedObj, b.LandingZone):
                            self.setGroundGatherFlag(unit, clickedObj)
                    elif unit.type == unit.GROUND_ATTACK:
                        if isinstance(clickedObj, u.Unit) or isinstance(clickedObj, Building):
                            if clickedObj.owner != self.playerId and not self.players[self.playerId].isAlly(clickedObj.owner):
                                self.setAttackFlag(clickedObj)
                    elif unit.type == unit.GROUND_BUILDER_UNIT:
                        if isinstance(clickedObj, Building):
                            if clickedObj.owner == self.playerId:
                                if clickedObj.finished == False:
                                    self.resumeBuildingFlag(clickedObj)
                    if isinstance(clickedObj, b.LandingZone) and clickedObj.owner == self.playerId:
                        self.setLoadFlag(self.players[self.playerId].selectedObjects, clickedObj)
                else:
                    if isinstance(unit, LandingZone):
                        self.setRallyPointPosition(pos)
                    else:
                        self.setGroundMovingFlag(pos[0], pos[1])
                
    #Selection avec le clic-drag
    def boxSelect(self, selectStart, selectEnd):
        realStart = self.players[self.playerId].camera.calcPointInWorld(selectStart[0], selectStart[1])
        realEnd = self.players[self.playerId].camera.calcPointInWorld(selectEnd[0], selectEnd[1])
        temp = [0,0]
        if realStart[0] > realEnd[0]:
            temp[0] = realStart[0]
            realStart[0] = realEnd[0]
            realEnd[0] = temp[0]
        if realStart[1] > realEnd[1]:
            temp[1] = realStart[1]
            realStart[1] = realEnd[1]
            realEnd[1] = temp[1]
        self.players[self.playerId].boxSelect(realStart, realEnd)
        self.parent.view.actionMenuType = self.parent.view.MAIN_MENU
        
    #Deplacement rapide de la camera vers un endroit de la minimap
    def quickMove(self, x, y):
        if self.players[self.playerId].currentPlanet == None:
            posSelected = self.players[self.playerId].camera.calcPointOnMap(x,y)
            self.players[self.playerId].camera.position = posSelected
        else:
            posSelected = self.players[self.playerId].camera.calcPointOnPlanetMap(x,y)
            self.players[self.playerId].camera.position = posSelected
        
    def takeOff(self, ship, planet, playerId):
        ship.takeOff(planet)
        self.players[playerId].currentPlanet = None
        self.parent.redrawMinimap()
        self.parent.drawWorld()

    def getCurrentCamera(self):
        return self.players[self.playerId].camera

    def isOnPlanet(self):
        if self.players[self.playerId].currentPlanet == None:
            return False
        else:
            return True

    def getCurrentPlanet(self):
        return self.players[self.playerId].currentPlanet
        
    def setTakeOffFlag(self, ship, planet):
        planetId = 0
        sunId = 0
        shipId = self.players[self.playerId].units.index(ship)
        self.players[self.playerId].selectedUnit = []
        for i in self.galaxy.solarSystemList:
            for j in i.planets:
                if j == planet:
                    planetId = i.planets.index(j)
                    sunId = self.galaxy.solarSystemList.index(i)
        self.parent.pushChange(shipId,(planetId, sunId, 'TAKEOFF'))

    def changeFormation(self, playerId, newType, units, action):
        if newType == 'c':
            self.players[playerId].formation = "carre"
        elif newType =='t':
            self.players[playerId].formation = "triangle"
        self.players[playerId].makeFormation(units, self.galaxy, action = action)

    def makeFormation(self, playerId, units, target, action):
        self.players[playerId].makeFormation(units, self.galaxy, target, action)
