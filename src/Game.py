# -*- coding: UTF-8 -*-
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

    def getMyPlayer(self):
        return self.players[self.playerId]
    
    def healUnitForReal(self, actionPlayerId, target, healUnitIndex):
        if target[1] == 0:
            self.players[actionPlayerId].units[healUnitIndex].changeFlag(self.players[actionPlayerId].units[int(target[0])],FlagState.HEAL)
        else:
            self.players[actionPlayerId].units[healUnitIndex].changeFlag(self.players[actionPlayerId].buildings[int(target[0])],FlagState.HEAL)

    def selectUnitToHeal(self, pos):
        toHeal = self.getMyPlayer().selectUnitToHeal(pos)
        if toHeal != None:
            if isinstance(toHeal, u.Unit):
                typeToHeal = 0
            elif isinstance(toHeal, Building):
                typeToHeal = 1
            else:
                typeToHeal = 2
            if typeToHeal != 2:
                self.setActionHealUnit(toHeal, typeToHeal)
    
    def setActionHealUnit(self, toHeal, typeToHeal):
        if typeToHeal == 0:
            toHealIndex = self.getMyPlayer().units.index(toHeal)
        elif typeToHeal == 1:
            toHealIndex = self.getMyPlayer().buildings.index(toHeal)
        healerUnitIndex = self.getMyPlayer().getSelectedHealUnitIndex()
        if healerUnitIndex != None:
            self.parent.pushChange(healerUnitIndex, Flag(finalTarget = t.Target([toHealIndex,typeToHeal,0]),flagState = FlagState.HEAL))
    
    def action(self):
        self.getMyPlayer().camera.move()
        self.parent.view.gameArea.delete('enemyRange')
        for w in self.galaxy.wormholes:
            if w.duration > 0:
                w.action()
        for p in self.players:
            if p.isAlive:
                 p.action()
        return self.getMyPlayer().isAlive

    def start(self, players, seed, width, height):
        self.galaxy=w.Galaxy(len(players), seed)
        self.players = players
        for i in self.players:
            startPos = self.galaxy.getSpawnPoint()
            i.addBaseUnits(startPos) 
        self.getMyPlayer().addCamera(self.galaxy, width, height)

    # Pour créer une notification qui vient du serveur
    def makeNotification(self, actionPlayerId, target, unitIndex):
        #target[0] = c'est le id du joueur qui doit recevoir la notification
        #target[1] = c'est le id du unit/building qui va faire l'action
        #target[2] = c'est le type de l'action (ATTACKED_UNIT, ATTACKED_BUILDING, ALLIANCE,...)
        #self.parent.pushChange(None, Flag(None,[attackedUnit.owner,self.players[attackedUnit.owner].units.index(attackedUnit), t.Notification.ATTACKED_UNIT],FlagState.NOTIFICATION))
        #pushChange= (None, Flag(None,[idJoueurQuiDoitLeRecevoir,idUnitQuiEstVisé,FlagDeLaNotification],FlagState.NOTIFICATION)
        player = self.players[target[0]]
        actionPlayerName = self.players[actionPlayerId].name
        addIt = True
        notif = None
        if not target[1] in (t.Notification.MESSAGE_ALL, t.Notification.MESSAGE_ALLIES, t.Notification.PING):
            if target[1] == t.Notification.ATTACKED_UNIT:
                for i in player.notifications:
                    if i.position == player.units[target[2]].position and i.actionPlayerName == actionPlayerName:
                        addIt = False
                if addIt:
                    #Tu ajoutes seulement le 4e paramètre si tu en as besoin, le nom de l'autre joueur
                    notif = t.Notification(player.units[target[2]].position, target[1], actionPlayerName)
            elif target[1] == t.Notification.ATTACKED_BUILDING:
                for i in player.notifications:
                    if i.position == player.buildings[target[2]].position and i.actionPlayerName == actionPlayerName:
                        addIt = False
                if addIt:
                    notif = t.Notification(player.buildings[target[2]].position, target[1], actionPlayerName)
            if notif != None:
                player.notifications.append(notif)
        else:
            mess = ""
            for i in unitIndex:
                mess+=i
            mess = actionPlayerName+" : "+mess
            if target[1] == t.Notification.MESSAGE_ALL:
                notif = t.Notification([-10000,-10000,-10000],target[1],mess)
                if self.playerId != player.id:
                    self.getMyPlayer().notifications.append(notif)
            elif target[1] == t.Notification.MESSAGE_ALLIES:
                notif = t.Notification([-10000,-10000,-10000],target[1],mess)
                if player.isAlly(self.playerId):
                    if self.playerId != player.id:
                        self.getMyPlayer().notifications.append(notif)
            elif target[1] == t.Notification.PING:
                notif = t.Notification([target[2],target[3],0],target[1],actionPlayerName)
                if player.isAlly(self.playerId):
                    if self.playerId != player.id:
                        if self.getMyPlayer().checkIfCanAddNotif(t.Notification.PING):
                            self.getMyPlayer().notifications.append(notif)
        

    # Pour changer le flag des unités selectionne pour la construction        
    def setBuildingFlag(self,x,y, type, sunId=0, planetId=0):
        units = ''
        #Si plusieurs unit�s sont s�lectionn�es, on les ajoute toutes dans le changement � envoyer
        for i in self.getMyPlayer().selectedObjects:
            if i.type in (i.SCOUT, i.GROUND_BUILDER_UNIT):
                units+= str(self.getMyPlayer().units.index(i))+","
        if self.getMyPlayer().ressources[0] >= Building.COST[type][0] and self.getMyPlayer().ressources[1] >= Building.COST[type][1]:
            if Building.INSPACE[type] == True:
                self.parent.pushChange(units, Flag((type,0),t.Target([x,y,0]),FlagState.BUILD))
            else:
                self.parent.pushChange(units, Flag((type,sunId,planetId),t.Target([x,y,0]),FlagState.BUILD))

    def buildBuilding(self, playerId, target, flag, unitIndex, type, sunId=0, planetId=0):
        #Condition de construction
        wp = None
        if self.checkIfCanBuild((target[0], target[1],0), type, int(unitIndex[0]), playerId):
            player = self.players[playerId]
            if player.ressources[0] >= Building.COST[type][0] and player.ressources[1] >= Building.COST[type][1]:
                player.ressources[0] -= Building.COST[type][0]
                player.ressources[1] -= Building.COST[type][1]
                if type == Building.WAYPOINT:
                    wp = Waypoint(Building.WAYPOINT, [target[0],target[1],0], playerId)
                elif type == Building.UTILITY:
                    wp = Utility(Building.UTILITY, [target[0],target[1],0], playerId)
                elif type == Building.BARRACK:
                    wp = Barrack(Building.BARRACK, [target[0],target[1],0], playerId)
                elif type == Building.TURRET:
                    wp = Turret(Building.TURRET, [target[0],target[1],0], playerId)
                elif type == Building.FARM:
                    wp = Farm(Building.FARM, [target[0],target[1],0], playerId, sunId, planetId)
                    wp.planet = self.galaxy.solarSystemList[sunId].planets[planetId]
                    self.galaxy.solarSystemList[sunId].planets[planetId].buildings.append(wp)
                elif type == Building.LAB:
                    wp = Lab(Building.LAB, [target[0],target[1],0], playerId, sunId, planetId)
                    wp.planet = self.galaxy.solarSystemList[sunId].planets[planetId]
                    self.galaxy.solarSystemList[sunId].planets[planetId].buildings.append(wp)    
                elif type == Building.MOTHERSHIP:
                    wp = Mothership(Building.MOTHERSHIP, [target[0],target[1],0], playerId)
                    self.players[playerId].motherships.append(wp)
            if wp != None:
                if self.players[playerId].FORCE_BUILD_ACTIVATED:
                    wp.buildTime = 1
                self.players[playerId].buildings.append(wp)
                for i in unitIndex:
                    if i != '':
                        self.players[playerId].units[int(i)].changeFlag(wp,flag)

    def resumeBuildingFlag(self,building):
        units = ''
        for i in self.getMyPlayer().selectedObjects:
            if i.type in (i.SCOUT, i.GROUND_BUILDER_UNIT):
                units+= str(self.getMyPlayer().units.index(i))+","
        if not building.finished:
            self.parent.pushChange(units, Flag(i,building,FlagState.FINISH_BUILD))                          

    def resumeBuilding(self, playerId, building, unitIndex):
        for i in unitIndex:
            if i != '':
                if int(i) < len(self.players[playerId].units):
                    self.players[playerId].units[int(i)].changeFlag(self.players[playerId].buildings[building],FlagState.BUILD)

    #Pour changer le flag des unites selectionne pour le deplacement    
    def setMovingFlag(self,x,y):
        units = ''
        send = False
        if y > self.galaxy.height/2:
            y = self.galaxy.height/2-15
        #Si plusieurs unités sont sélectionnées, on les ajoute toutes dans le changement à envoyer
        for i in self.getMyPlayer().selectedObjects:
            if isinstance(i, u.Unit):              
                units += str(self.getMyPlayer().units.index(i)) + ","
                send = True
        if send:
            self.parent.pushChange(units, Flag(i,t.Target([x,y,0]),FlagState.MOVE))
            
    def setGroundMovingFlag(self,x,y):
        units = ''
        #Si plusieurs unités sont sélectionnées, on les ajoute toutes dans le changement à envoyer
        for i in self.getMyPlayer().selectedObjects:
            if isinstance(i, u.Unit):
                units += str(self.getMyPlayer().units.index(i))+ ","
        self.parent.pushChange(units, Flag(t.Target([0,0,0]), t.Target([x,y,0]),FlagState.GROUND_MOVE))

    def setDefaultMovingFlag(self,x,y, unit):
        units = ''
        send = False
        #Si plusieurs unités sont sélectionnées, on les ajoute toutes dans le changement à envoyer            
        units += str(self.getMyPlayer().units.index(unit)) + ","
        self.parent.pushChange(units, Flag(unit,t.Target([x,y,0]),FlagState.MOVE))
    
    #Pour changer le flag des unites selectionne pour l'arret
    def setStandbyFlag(self):
        units = ""
        #Si plusieurs unités sont sélectionnées, on les ajoute toutes dans le changement à envoyer
        for i in self.getMyPlayer().selectedObjects:
            if isinstance(i, u.Unit):
                units += str(self.getMyPlayer().units.index(i)) + ","
        if units != "":
            self.parent.pushChange(units, Flag(i,t.Target([0,0,0]),FlagState.STANDBY))

    def setPatrolFlag(self, pos):
        units = ''
        send = False
        #Si plusieurs unités sont sélectionnées, on les ajoute toutes dans le changement à envoyer
        for i in self.getMyPlayer().selectedObjects:
            if isinstance(i, u.Unit):
                units += str(self.getMyPlayer().units.index(i)) + ","
                send = True
        if send:
            self.parent.pushChange(units, Flag(i,t.Target([pos[0],pos[1],0]),FlagState.PATROL))
            
    #Pour changer le flag des unités sélectionnés pour attaquer        
    def setAttackFlag(self, attackedUnit):
        attacking = True
        if attacking:
            units = ""
            for i in self.getMyPlayer().selectedObjects:
                if isinstance(i, u.SpaceAttackUnit) or isinstance(i, u.NyanCat):
                    if isinstance(attackedUnit, u.Unit) :
                        if attackedUnit.type == u.Unit.TRANSPORT:
                            if attackedUnit.landed == False:
                                units += str(self.getMyPlayer().units.index(i)) + ","
                        else:
                            units += str(self.getMyPlayer().units.index(i)) + ","
                    else:
                        units += str(self.getMyPlayer().units.index(i)) + ","
                elif isinstance(i, u.GroundAttackUnit):
                    units += str(self.getMyPlayer().units.index(i)) + ","
            if units != "":
                self.parent.pushChange(units, Flag(i,attackedUnit,FlagState.ATTACK))
                if isinstance(attackedUnit,u.Unit):
                    self.parent.pushChange(None, Flag(None,[attackedUnit.owner, t.Notification.ATTACKED_UNIT, self.players[attackedUnit.owner].units.index(attackedUnit)],FlagState.NOTIFICATION))
                else:
                    self.parent.pushChange(None, Flag(None,[attackedUnit.owner, t.Notification.ATTACKED_BUILDING, self.players[attackedUnit.owner].buildings.index(attackedUnit)], FlagState.NOTIFICATION))

    def setAttackBuildingFlag(self, pos):
        units = ''
        for i in self.getMyPlayer().selectedObjects:
            if i.type == u.Unit.SPACE_BUILDING_ATTACK:
                units += str(self.getMyPlayer().units.index(i)) + ","
        self.parent.pushChange(units, Flag(None, pos, FlagState.ATTACK_BUILDING))

    def makeSpaceBuildingAttack(self, playerId, target, unitId):
        for i in unitId:
            if i != '':
                if int(i) < len(self.players[playerId].units):
                    self.players[playerId].units[int(i)].changeFlag(t.Target(target), FlagState.ATTACK_BUILDING)

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

    def setWormHoleFlag(self, wormhole):
        units = ""
        for i in self.getMyPlayer().selectedObjects:
            if isinstance(i, u.Unit):              
                units += str(self.getMyPlayer().units.index(i)) + ","
        self.parent.pushChange(units, Flag(self.playerId, wormhole, FlagState.WORMHOLE))

    def makeUnitGoToWormhole(self, units, playerId, wormholeId):
        wormhole = self.galaxy.wormholes[wormholeId]
        self.players[playerId].makeUnitGoToWormhole(units, wormhole)

    def makeUnitsAttack(self, playerId, units, targetPlayer, targetUnit, type):
        self.players[playerId].makeUnitsAttack(units, self.players[targetPlayer], targetUnit, type)

    def killUnit(self, killedIndexes, hasToKill = True):
        if hasToKill:
            self.players[killedIndexes[1]].killUnit(killedIndexes)
            if killedIndexes[2] == True:
                if isinstance(self.players[killedIndexes[1]].buildings[killedIndexes[0]], LandingZone):
                    self.players[killedIndexes[1]].planets.remove(self.players[killedIndexes[1]].buildings[killedIndexes[0]].planet)
                elif isinstance(self.players[killedIndexes[1]].buildings[killedIndexes[0]], Mothership):
                    mothership = self.players[killedIndexes[1]].buildings[killedIndexes[0]]
                    if self.players[killedIndexes[1]].motherships.index(mothership) == 0:
                        if len(self.players[killedIndexes[1]].motherships) >= 2:
                            self.motherShip = self.players[killedIndexes[1]].buildings[killedIndexes[0]+1]
                    self.players[killedIndexes[1]].motherships.remove(self.players[killedIndexes[1]].buildings[killedIndexes[0]])
                    die = True
                    for i in self.players[killedIndexes[1]].motherships:
                        if i.isAlive:
                            die = False
                            break
                    if die:
                        self.killPlayer(killedIndexes[1])
            else:
                if isinstance(self.players[killedIndexes[1]].units[killedIndexes[0]], u.TransportShip):
                    for un in self.players[killedIndexes[1]].units[killedIndexes[0]].units:
                        self.killUnit((self.players[killedIndexes[1]].units.index(un),killedIndexes[1],killedIndexes[2]))
        for play in self.players:
            play.checkIfIsAttacking(killedIndexes)

    def removeLandingZoneFromPlanet(self, landingZone):
        planet = self.galaxy.solarSystemList[landingZone.sunId].planets[landingZone.planetId]
        if landingZone in planet.landingZones:
            planet.landingZones.remove(landingZone)

    def addBuildingEnemy(self, buildingFound, isFinished):
        for building in self.getMyPlayer().buildingsFound:
            if building[0] == buildingFound:
                building[1] = isFinished
                return None
        self.getMyPlayer().buildingsFound.append((buildingFound,isFinished))

    def setBuyTech(self, techType, index):
        self.parent.pushChange(techType, Flag(0,t.Target([int(index), self.getMyPlayer().getSelectedBuildingIndex(),0]),FlagState.BUY_TECH))

    def buyTech(self, playerId, techType, index, labIndex):
        player = self.players[playerId]
        techTree = player.techTree
        if techType == "Button_Buy_Unit_Tech":
            tech = techTree.getTechs(techTree.UNITS)[index]
        elif techType == "Button_Buy_Building_Tech":
            tech = techTree.getTechs(techTree.BUILDINGS)[index]
        elif techType == "Button_Buy_Mothership_Tech":
            tech = techTree.getTechs(techTree.MOTHERSHIP)[index]
        if player.ressources[0] >= tech.costMine and player.ressources[1] >= tech.costGaz and player.ressources[3] >= tech.costNuclear:
            if techType == "Button_Buy_Unit_Tech":
                tech = techTree.buyUpgrade(techTree.getTechs(techTree.UNITS)[index].name,techTree.UNITS, tech)
            elif techType == "Button_Buy_Building_Tech":
                tech = techTree.buyUpgrade(techTree.getTechs(techTree.BUILDINGS)[index].name,techTree.BUILDINGS, tech)
            elif techType == "Button_Buy_Mothership_Tech":
                tech = techTree.buyUpgrade(techTree.getTechs(techTree.MOTHERSHIP)[index].name,techTree.MOTHERSHIP, tech)
            player.ressources[0] -= tech.costMine
            player.ressources[1] -= tech.costGaz
            player.ressources[3] -= tech.costNuclear
            if labIndex < len(player.buildings) and isinstance(player.buildings[labIndex], Lab):
                if player.FORCE_BUILD_ACTIVATED:
                    tech.timeNeeded = 1
                if tech.effect == 'D':
                    player.buildings[labIndex].techsToResearch.append((tech, player.ATTACK_DAMAGE_BONUS))
                elif tech.effect == 'DB':
                    player.buildings[labIndex].techsToResearch.append((tech, player.ATTACK_DAMAGE_BUILDING_BONUS))
                elif tech.effect == 'S':
                    player.buildings[labIndex].techsToResearch.append((tech, player.MOVE_SPEED_BONUS))
                elif tech.effect == 'AS':
                    player.buildings[labIndex].techsToResearch.append((tech, player.ATTACK_SPEED_BONUS))
                elif tech.effect == 'AR':
                    player.buildings[labIndex].techsToResearch.append((tech, player.ATTACK_RANGE_BONUS))
                elif tech.effect == 'TN':
                    player.buildings[labIndex].techsToResearch.append((tech, player.ABILITY_WORM_HOLE))
                elif tech.effect == 'M':
                    player.buildings[labIndex].techsToResearch.append((tech, player.ABILITY_WALLS))
                elif tech.effect == 'VR':
                    player.buildings[labIndex].techsToResearch.append((tech, player.VIEW_RANGE_BONUS))
                elif tech.effect == 'BB':
                    player.buildings[labIndex].techsToResearch.append((tech, player.BUILDING_SHIELD_BONUS))
                elif tech.effect == 'BM':
                    player.buildings[labIndex].techsToResearch.append((tech, player.BUILDING_MOTHERSHIELD_BONUS))
                elif tech.effect == 'DM':
                    player.buildings[labIndex].techsToResearch.append((tech, player.ATTACK_DAMAGE_MOTHERSHIP))
        else:
            player.notifications.append(t.Notification([-10000,-10000,-10000],t.Notification.NOT_ENOUGH_RESSOURCES))
        
    def setGatherFlag(self, ship, ressource):
        units = str(self.getMyPlayer().units.index(ship)) + ","
        self.parent.pushChange(units, Flag(t.Target([0,0,0]),ressource, FlagState.GATHER))

    def setAllGatherFlag(self, ressource):
        units = ""
        for i in self.getMyPlayer().selectedObjects:
            if i.type == u.Unit.CARGO:
                units += str(self.getMyPlayer().units.index(i)) + ","
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
        units = str(self.getMyPlayer().units.index(ship)) + ","
        self.parent.pushChange(units, Flag(t.Target([0,0,0]), ressource, FlagState.GROUND_GATHER))

    def setAllGroundGatherFlag(self, ressource):
        units = ""
        for i in self.getMyPlayer().selectedObjects:
            if i.type == u.Unit.GROUND_GATHER:
                units += str(self.getMyPlayer().units.index(i)) + ","
        self.parent.pushChange(units, Flag(t.Target([0,0,0]), ressource, FlagState.GROUND_GATHER))
        
    def makeGroundUnitMove(self, playerId, unitsId, posX, posY, posZ, action):
        print('makeGroundUnitMove dans Game pour le joueur: ', playerId)
        self.players[int(playerId)].makeGroundUnitsMove(unitsId, [posX, posY, posZ], int(action))

    def makeGroundUnitsGather(self, playerId, unitsId, ressourceId, planetId, sunId, ressourceType):
        if ressourceType == Planet.MINERAL:
            ressource = self.galaxy.solarSystemList[sunId].planets[planetId].minerals[ressourceId]
        elif ressourceType == Planet.GAZ:
            ressource = self.galaxy.solarSystemList[sunId].planets[planetId].gaz[ressourceId]
        elif ressourceType == Planet.NUCLEAR:
            ressource = self.galaxy.solarSystemList[sunId].planets[planetId].nuclearSite
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
            if int(self.parent.view.menuModes.spinMinerals1.get()) <= self.getMyPlayer().ressources[0] and int(self.parent.view.menuModes.spinGaz1.get()) <= self.getMyPlayer().ressources[1]:
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
        self.parent.pushChange(str(self.getMyPlayer().units.index(unit)), (solarsystemId, planetIndex, FlagState.LAND))

    def makeUnitLand(self, playerId, unitId, solarSystemId, planetId):
        #if playerId == self.playerId:
        planet = self.galaxy.solarSystemList[solarSystemId].planets[planetId]
        self.players[playerId].makeUnitLand(unitId, planet)

    def setRallyPointPosition(self, pos):
        self.parent.pushChange(self.getMyPlayer().getSelectedBuildingIndex(), Flag(finalTarget = pos, flagState = FlagState.CHANGE_RALLY_POINT))

    def setChangeFormationFlag(self, formation):
        units = ""
        for i in self.getMyPlayer().selectedObjects:           
            units += str(self.getMyPlayer().units.index(i)) + ","
        self.parent.pushChange(units, Flag(i,formation,FlagState.CHANGE_FORMATION))
        
    def setTakeOffFlag(self, ship, planet):
        planetId = 0
        sunId = 0
        shipId = self.getMyPlayer().units.index(ship)
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
                units += str(self.getMyPlayer().units.index(i)) + ","
        self.parent.pushChange(units, Flag(unit, landingZone, FlagState.LOAD))

    def loadUnit(self, units, planetId, sunId, playerId):
        planet = self.galaxy.solarSystemList[sunId].planets[planetId]
        landingZone = planet.getLandingSpot(playerId)
        if landingZone != None:
            self.players[playerId].makeUnitLoad(units, landingZone)

    def unload(self):
        zone = self.getMyPlayer().getShipToUnload()
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
        if self.getMyPlayer().canAfford(mineralCost, gazCost, foodCost):
            self.parent.pushChange(self.getMyPlayer().getSelectedBuildingIndex(),Flag(finalTarget = unitType, flagState = FlagState.CREATE))
        elif self.getMyPlayer().ressources[p.Player.FOOD]+foodCost > self.getMyPlayer().MAX_FOOD:
            if self.getMyPlayer().checkIfCanAddNotif(t.Notification.NOT_ENOUGH_POPULATION):
                self.getMyPlayer().notifications.append(t.Notification([-10000,-10000,-10000],t.Notification.NOT_ENOUGH_POPULATION))
        else:
            if self.getMyPlayer().checkIfCanAddNotif(t.Notification.NOT_ENOUGH_RESSOURCES):
                self.getMyPlayer().notifications.append(t.Notification([-10000,-10000,-10000],t.Notification.NOT_ENOUGH_RESSOURCES))

    def createUnit(self, player,constructionUnit, unitType):
        mineralCost = u.Unit.BUILD_COST[unitType][0]
        gazCost = u.Unit.BUILD_COST[unitType][1]
        foodCost = u.Unit.BUILD_COST[unitType][2]
        if self.players[player].canAfford(mineralCost, gazCost, foodCost):
            if constructionUnit <= (len(self.players[player].buildings)-1) and constructionUnit != None:
                if isinstance(self.players[player].buildings[constructionUnit], ConstructionBuilding):
                    self.players[player].createUnit(unitType, constructionUnit)

    def sendCancelUnit(self, unit):
        self.parent.pushChange(self.getMyPlayer().getSelectedBuildingIndex(), Flag(finalTarget = unit, flagState = FlagState.CANCEL_UNIT))

    def cancelUnit(self, player, unit, constructionBuilding):
        if constructionBuilding <= (len(self.players[player].buildings)-1) and constructionBuilding != None:
            self.players[player].cancelUnit(unit, constructionBuilding)

    def sendCancelTech(self, tech):
        self.parent.pushChange(self.getMyPlayer().getSelectedBuildingIndex(), Flag(finalTarget = tech, flagState = FlagState.CANCEL_TECH))

    def cancelTech(self, player, tech, constructionBuilding):
        if constructionBuilding <= (len(self.players[player].buildings)-1) and constructionBuilding != None:
            self.players[player].cancelTech(tech, constructionBuilding)
    
    #Pour effacer un Unit
    def eraseUnit(self):
        if len(self.getMyPlayer().selectedObjects) > 0:
            if isinstance(self.getMyPlayer().selectedObjects[len(self.getMyPlayer().selectedObjects)-1], u.Unit):
                self.parent.pushChange(self.getMyPlayer().units.index(self.getMyPlayer().selectedObjects[len(self.getMyPlayer().selectedObjects)-1]), Flag(None,None,FlagState.DESTROY))
                
    #Pour effacer tous les units
    def eraseUnits(self, playerId=None):
        if playerId == None:
            playerId = self.playerId
        #self.parent.pushChange(playerId, Flag(None,playerId,FlagState.DESTROY_ALL))

    def checkIfGameFinished(self):
        myPlayer = self.getMyPlayer()
        for i in self.players:
            if i.isAlive and i.id != myPlayer.id:
                if not myPlayer.isAlly(i.id):
                    return False
        return True

    def calculateWhoWon(self):
        scores = []
        for pl in self.players:
            toInsert = []
            toInsert.append(pl.colorId)
            toInsert.append(pl.name)
            toInsert.append(pl.calculateFinalBuildingsScore())
            toInsert.append(pl.calculateFinalUnitsScore())
            toInsert.append(pl.calculateFinalRessourcesScore())
            toInsert.append(pl.calculateFinalKilledScore())
            toInsert.append(pl.calculateFinalDiplomacyScore())
            toInsert.append(toInsert[2]+toInsert[3]+toInsert[4]+toInsert[5]+toInsert[6])
            indexToInsert = 0
            for i in scores:
                if toInsert[7] > i[7]:
                    break
                indexToInsert += 1
            scores.insert(indexToInsert, toInsert)
        return scores

    def killPlayer(self, playerId):
        self.players[playerId].kill()
        if playerId == self.playerId:
            self.parent.removePlayer()
            self.getMyPlayer().selectedObjects = []
            self.parent.goToWinFrame(self.calculateWhoWon())
        elif self.checkIfGameFinished():
            self.parent.goToWinFrame(self.calculateWhoWon())
    
    def trade(self, player1, player2, ressourceType, amount):
        self.players[player1].adjustRessources(ressourceType, amount)
        self.players[player2].adjustRessources(ressourceType, amount*-1)

    def adjustRessources(self, player, ressourceType, amount):
        self.players[player].adjustRessources(ressourceType, amount)

    def cheatPlayer(self, playerId , type):
        if type == "forcegaz":
            self.players[playerId].ressources[p.Player.GAS] += 5000
        elif type == "forcemine":
            self.players[playerId].ressources[p.Player.MINERAL] += 5000
        elif type == "forcenuke":
            self.players[playerId].ressources[p.Player.NUCLEAR] += 25
        elif type == "forcepop":
            self.players[playerId].MAX_FOOD += 30
        elif type == "forcebuild":
            self.players[playerId].FORCE_BUILD_ACTIVATED = True
            player = self.players[playerId]
            for un in player.units:
                if isinstance(un, u.GatherShip) or isinstance(un, u.GroundGatherUnit) or isinstance(un, u.SpecialGather):
                    un.GATHERTIME = 0
            for i in player.buildings:
                if isinstance(i, b.ConstructionBuilding) and i.finished:
                    for a in i.unitBeingConstruct:
                        a.buildTime = 1
                elif not i.finished:
                    i.hitpoints = i.MAX_HP[i.type]
                    i.buildTime = 1
                elif isinstance(i, b.Lab) and i.finished:
                    for t in i.techsToResearch:
                        t[0].timeNeeded = 1
        elif type == "doabarrelroll":
            un = u.NyanCat(u.Unit.NYAN_CAT, [0,0,0], playerId)
            self.players[playerId].units.append(un)
        elif type == "allyourbasesbelongtous":
            self.players[playerId].motherships[0].viewRange = 1000000000
    
    def demandAlliance(self, playerId, otherPlayerId, newStatus):
        self.players[playerId].changeDiplomacy(otherPlayerId, newStatus)
        if otherPlayerId == self.playerId:
            #Dire au joueur que quelqu'un a changé de diplomacie avec toi (système de notifications)
            if newStatus == "Ally":
                if self.players[otherPlayerId].isAlly(playerId):
                    self.getMyPlayer().notifications.append(t.Notification((-10000,-10000,-10000),t.Notification.ALLIANCE_ALLY,self.players[playerId].name))
                else:
                    self.getMyPlayer().notifications.append(t.Notification((-10000,-10000,-10000),t.Notification.ALLIANCE_DEMAND_ALLY,self.players[playerId].name))
            else:
                self.getMyPlayer().notifications.append(t.Notification((-10000,-10000,-10000),t.Notification.ALLIANCE_ENNEMY,self.players[playerId].name))
        elif playerId == self.playerId:
            if newStatus == "Ally" and self.players[otherPlayerId].isAlly(playerId):
                    self.getMyPlayer().notifications.append(t.Notification((-10000,-10000,-10000),t.Notification.ALLIANCE_ALLY,self.players[otherPlayerId].name))
        if self.checkIfGameFinished():
            self.parent.goToWinFrame(self.calculateWhoWon())

    def getPlayerId(self, player):
        for i in self.players:
            if i.name == player:
                return i.id
        return -1
    
    def isAllied(self, player1Id, player2Id):
        if self.players[player1Id].diplomacies[player2Id] == "Ally":
            return True
        else:
            return False

    def getAllies(self):
        allies = []
        for p in self.players:
            if p != self.getMyPlayer():
                if p.isAlly(self.playerId):
                    allies.append(p.name)
        return allies

    def getFirstUnitSelected(self):
        return self.getMyPlayer().selectedObjects[0]

    def selectWaypointWall(self, pos):
        if self.getMyPlayer().currentPlanet == None:
            for bd in self.getMyPlayer().buildings:
                if isinstance(bd, Waypoint) and bd != self.getFirstUnitSelected():
                    way = bd.select(pos)
                    if way != None:
                        return way
        return None

    def calcCostWall(self, waypoint1, waypoint2):
        distance = Helper.calcDistance(waypoint1.position[0], waypoint1.position[1], waypoint2.position[0], waypoint2.position[1])
        cost = (distance*3)-((distance*3)%25)+25
        return cost
    
    def setLinkedWaypoint(self, pos):
        selectedWayPoint = self.getFirstUnitSelected()
        otherWaypoint = self.selectWaypointWall(pos)
        if otherWaypoint != None:
            if selectedWayPoint.hasFreeWall and otherWaypoint.hasFreeWall:
                cost = int(self.calcCostWall(selectedWayPoint, otherWaypoint))
                if self.getMyPlayer().canAfford(0,cost,0):
                    way1 = self.getMyPlayer().buildings.index(selectedWayPoint)
                    way2 = self.getMyPlayer().buildings.index(otherWaypoint)
                    self.parent.pushChange("0,", Flag(None, [way1,way2,cost], FlagState.LINK_WAYPOINTS))
                else:
                    self.getMyPlayer().notifications.append(t.Notification([-10000,-10000,-10000],t.Notification.NOT_ENOUGH_RESSOURCES))

    def linkWaypoints(self, playerId, wayId1, wayId2, cost):
        player = self.players[playerId]
        if player.canAfford(0,cost,0):
           player.linkWaypoints(wayId1, wayId2, cost)

    def unitsInLine(self, wall):
        units = []
        for pl in self.players:
            if pl.id != wall.owner:
                for un in pl.units:
                    if un.isAlive:
                        if wall.isRectangleOnLine(un.position, un.SIZE[un.type]):
                            units.append(un)
                for bd in pl.buildings:
                    if bd.isAlive:
                        if wall.isRectangleOnLine(bd.position, bd.SIZE[bd.type]):
                            units.append(build)
        return units

   #Pour selectionner une unit
    def selectUnitEnemy(self, posSelected):
        if self.getMyPlayer().currentPlanet == None:
            if len(self.getMyPlayer().selectedObjects) > 0:
                    for i in self.players:
                        if i.isAlive:
                            if i.id != self.playerId and self.getMyPlayer().isAlly(i.id) == False:
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

    def hasUnitInRange(self, bullet):
        unitsToAttack = []
        for pl in self.players:
            if pl.isAlive and pl.id != bullet.owner:
                for un in pl.units:
                    if un.isAlive and (isinstance(un, u.SpaceUnit) or un.type == u.Unit.SCOUT):
                        unitInRange = un.isInRange(bullet.position, bullet.range)
                        if unitInRange != None:
                            unitsToAttack.append(unitInRange)
                for bd in pl.buildings:
                    if bd.isAlive and (isinstance(bd, SpaceBuilding) or isinstance(bd, Mothership) or isinstance(bd, Barrack) or isinstance(bd, Utility)):
                        buildingInRange = bd.isInRange(bullet.position, bullet.range)
                        if buildingInRange != None:
                            unitsToAttack.append(buildingInRange)
        return unitsToAttack
    
    def checkIfCanBuild(self, position, type, index = None, playerId = None):
        if index != None:
            if index < len(self.players[playerId].units):
                unit = self.players[playerId].units[index]
            else:
                return False
        else:
            if len(self.getMyPlayer().selectedObjects) > 0:
                unit = self.getMyPlayer().selectedObjects[0]
            else:
                return False
        start = (position[0]-(Building.SIZE[type][0]/2),position[1]-(Building.SIZE[type][1]/2),0)
        end = (position[0]+(Building.SIZE[type][0]/2),position[1]+(Building.SIZE[type][1]/2),0)
        
        for p in self.players:
            for b in p.buildings:
                if self.getCurrentPlanet() != None:
                    if (isinstance(b, GroundBuilding) or isinstance(b, LandingZone)) and isinstance(unit, u.GroundUnit):
                        if unit.planet == b.planet:
                            if b.selectIcon(start, end) != None:
                                return False
                else:
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
        self.getMyPlayer().selectUnitsByType(typeId)
    
    def select(self, posSelected):
        player = self.getMyPlayer()
        if player.currentPlanet == None:
            if not self.multiSelect:
                player.selectUnit(posSelected)
            else:
                player.multiSelectUnit(posSelected)
            spaceObj = self.galaxy.select(posSelected, False)
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
        self.getMyPlayer().selectObjectFromMenu(unitId)
    
    def selectAll(self, posSelected):
        self.getMyPlayer().selectAll(posSelected)
        self.parent.changeActionMenuType(View.MAIN_MENU)

    def rightClic(self, pos):
        empty = True
        if self.getCurrentPlanet() == None:
            unit = self.getMyPlayer().getFirstUnit()
            if unit != None:
                clickedObj = self.galaxy.select(pos)
                if clickedObj == None:
                    for i in self.players:
                        clickedObj = i.rightClic(pos, self.playerId)
                        if clickedObj != None:
                            break
                if clickedObj != None and not isinstance(unit, Building):
                    if unit.type == unit.HEALING_UNIT:
                        if isinstance(clickedObj, u.Unit):
                            if clickedObj.owner == self.playerId:
                                self.setActionHealUnit(clickedObj, 0)
                        elif isinstance(clickedObj, Building):
                            if clickedObj.owner == self.playerId:
                                self.setActionHealUnit(clickedObj, 1)
                    if unit.type == unit.TRANSPORT:
                        if isinstance(clickedObj, w.Planet):
                            self.setLandingFlag(unit, clickedObj)
                        elif isinstance(clickedObj, Mothership):
                            self.setGatherFlag(unit, clickedObj)
                    elif unit.type == unit.CARGO:
                        if isinstance(clickedObj, w.AstronomicalObject):
                            self.setAllGatherFlag(clickedObj)
                        elif isinstance(clickedObj, Mothership) or isinstance(clickedObj, Waypoint):
                            if clickedObj.owner == self.playerId:
                                self.setGatherFlag(unit, clickedObj)
                    elif unit.type in (unit.ATTACK_SHIP, unit.NYAN_CAT):
                        if (isinstance(clickedObj, u.Unit) or isinstance(clickedObj, SpaceBuilding) or isinstance(clickedObj, Mothership) or isinstance(clickedObj, Utility) or isinstance(clickedObj, Barrack)) and  not isinstance(clickedObj, u.GroundUnit):
                            if clickedObj.owner != self.playerId:
                                self.setAttackFlag(clickedObj)
                    elif unit.type == unit.SPACE_BUILDING_ATTACK:
                        if (isinstance(clickedObj, u.Unit) or isinstance(clickedObj, SpaceBuilding) or isinstance(clickedObj, Mothership) or isinstance(clickedObj, Utility) or isinstance(clickedObj, Barrack)) and  not isinstance(clickedObj, u.GroundUnit):
                            if clickedObj.owner != self.playerId:
                                pos = clickedObj.position
                            self.setAttackBuildingFlag([pos[0], pos[1], 0])
                    elif unit.type == unit.SCOUT:
                        if isinstance(clickedObj, Building):
                            if clickedObj.owner == self.playerId:
                                if clickedObj.finished == False:
                                    self.resumeBuildingFlag(clickedObj)
                    if isinstance(clickedObj, w.WormHole):
                        if clickedObj.duration > 0 and clickedObj.playerId == self.playerId:
                            self.setWormHoleFlag(clickedObj)
                else:
                    if isinstance(unit, ConstructionBuilding):
                        self.setRallyPointPosition(pos)
                    else:
                        self.setMovingFlag(pos[0], pos[1])
        else:
            unit = self.getMyPlayer().getFirstUnit()
            clickedObj = self.getCurrentPlanet().groundSelect(pos)
            if unit != None:
                if clickedObj != None and not isinstance(unit, Building):
                    if unit.type == unit.GROUND_GATHER:
                        if isinstance(clickedObj, w.MineralStack) or isinstance(clickedObj, w.GazStack) or isinstance(clickedObj, b.LandingZone):
                            self.setAllGroundGatherFlag(clickedObj)
                    elif unit.type == unit.GROUND_ATTACK:
                        if isinstance(clickedObj, u.Unit) or isinstance(clickedObj, Building):
                            if clickedObj.owner != self.playerId and not self.getMyPlayer().isAlly(clickedObj.owner):
                                self.setAttackFlag(clickedObj)
                    elif unit.type == unit.GROUND_BUILDER_UNIT:
                        if isinstance(clickedObj, Building):
                            if clickedObj.owner == self.playerId:
                                if clickedObj.finished == False:
                                    self.resumeBuildingFlag(clickedObj)
                    elif unit.type == unit.SPECIAL_GATHER:
                        if isinstance(clickedObj, NuclearSite):
                            self.setGroundGatherFlag(unit, clickedObj)
                    if isinstance(clickedObj, b.LandingZone) and clickedObj.owner == self.playerId:
                        self.setLoadFlag(self.getMyPlayer().selectedObjects, clickedObj)
                else:
                    if isinstance(unit, LandingZone):
                        self.setRallyPointPosition(pos)
                    else:
                        self.setGroundMovingFlag(pos[0], pos[1])
                
    #Selection avec le clic-drag
    def boxSelect(self, selectStart, selectEnd):
        realStart = self.getMyPlayer().camera.calcPointInWorld(selectStart[0], selectStart[1])
        realEnd = self.getMyPlayer().camera.calcPointInWorld(selectEnd[0], selectEnd[1])
        temp = [0,0]
        if realStart[0] > realEnd[0]:
            temp[0] = realStart[0]
            realStart[0] = realEnd[0]
            realEnd[0] = temp[0]
        if realStart[1] > realEnd[1]:
            temp[1] = realStart[1]
            realStart[1] = realEnd[1]
            realEnd[1] = temp[1]
        self.getMyPlayer().boxSelect(realStart, realEnd)
        self.parent.view.actionMenuType = self.parent.view.MAIN_MENU
        
    #Deplacement rapide de la camera vers un endroit de la minimap
    def quickMove(self, x, y):
        if self.getMyPlayer().currentPlanet == None:
            posSelected = self.getMyPlayer().camera.calcPointOnMap(x,y)
            self.getMyPlayer().camera.position = posSelected
        else:
            posSelected = self.getMyPlayer().camera.calcPointOnPlanetMap(x,y)
            self.getMyPlayer().camera.position = posSelected

    def pingAllies(self, x, y):
        self.parent.pushChange(self.getMyPlayer().name, Flag(None,[self.playerId,t.Notification.PING,x,y],FlagState.NOTIFICATION))
    
    def takeOff(self, ship, planet, playerId):
        ship.takeOff(planet)
        self.players[playerId].currentPlanet = None
        self.parent.redrawMinimap()
        self.parent.drawWorld()

    def getCurrentCamera(self):
        return self.getMyPlayer().camera

    def isOnPlanet(self):
        if self.getMyPlayer().currentPlanet == None:
            return False
        else:
            return True

    def getCurrentPlanet(self):
        return self.getMyPlayer().currentPlanet
        
    def setTakeOffFlag(self, ship, planet):
        planetId = 0
        sunId = 0
        shipId = self.getMyPlayer().units.index(ship)
        self.getMyPlayer().selectedUnit = []
        for i in self.galaxy.solarSystemList:
            for j in i.planets:
                if j == planet:
                    planetId = i.planets.index(j)
                    sunId = self.galaxy.solarSystemList.index(i)
        self.parent.pushChange(shipId,(planetId, sunId, 'TAKEOFF'))

    def changeFormation(self, playerId, newType, units, action):
        self.players[playerId].formation = newType
        self.players[playerId].makeFormation(units, self.galaxy, action = action)

    def makeFormation(self, playerId, units, target, action):
        self.players[playerId].makeFormation(units, self.galaxy, target, action)

    def selectMemory(self, selected):
        self.getMyPlayer().selectMemory(selected)

    def newMemory(self, selected):
        self.getMyPlayer().newMemory(selected)

    def makeWormHole(self, playerId, startPosition, endPosition, mothership):
        gazCost = Helper.calcDistance(startPosition[0], startPosition[1], endPosition[0], endPosition[1])
        gazCost = int(math.trunc(gazCost))
        if self.players[playerId].canAfford(0,gazCost, 0,WormHole.NUKECOST) and mothership.wormhole == None:
            self.players[playerId].ressources[p.Player.NUCLEAR] -= WormHole.NUKECOST
            self.players[playerId].ressources[p.Player.GAS] -= gazCost
            newWormHole = WormHole(startPosition, endPosition, playerId)
            self.galaxy.wormholes.append(newWormHole)
            mothership.wormhole = newWormHole
        
    def createWormHole(self, position):
        mothership = self.getMyPlayer().selectedObjects[0]
        motherIndex = self.getMyPlayer().motherships.index(mothership)
        self.parent.pushChange(motherIndex, (mothership.position, position, 'WORMHOLE'))
		
    def canSetAttack(self):
        player = self.getMyPlayer()
        for i in player.selectedObjects:
            if i.type == u.Unit.ATTACK_SHIP or i.type == u.Unit.GROUND_ATTACK:
                return 'Normal'
            elif i.type == u.Unit.SPACE_BUILDING_ATTACK:
                return 'Building'
        return None
