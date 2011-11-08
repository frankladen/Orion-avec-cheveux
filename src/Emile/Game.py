# -*- coding: UTF-8 -*-
import View as v
import World as w
import Player as p
import Target as t
import Unit as u
from Helper import *
from Flag import *
from Constants import *
import Pyro4
import socket
import math
from time import time
class Game():
    def __init__(self, controller):
        self.parent = controller
        self.players = []
        self.playerId = 0
        self.mess = []
        self.changes = []
        self.multiSelect = False
        
    #Pour changer le flag des unites selectionne pour le deplacement    
    def setMovingFlag(self,x,y):
        units = ''
        send = False
        #Si plusieurs unités sont sélectionnées, on les ajoute toutes dans le changement à envoyer
        for i in self.players[self.playerId].selectedObjects:
            if isinstance(i, u.Unit) and i.type != i.MOTHERSHIP:              
                units += str(self.players[self.playerId].units.index(i)) + ","
                send = True
            elif isinstance(i, u.Mothership):
                self.setMotherShipRallyPoint([x,y,0])
        if send:
            self.parent.pushChange(units, Flag(i,t.Target([x,y,0]),FlagState.MOVE))
            
    def setGroundMovingFlag(self,x,y):
        units = ''
        #Si plusieurs unités sont sélectionnées, on les ajoute toutes dans le changement à envoyer
        for i in self.players[self.playerId].selectedObjects:
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
            if isinstance(i, u.Unit) and i.type != i.MOTHERSHIP:
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
                    if attackedUnit.type == u.Unit.TRANSPORT:
                        if not attackedUnit.landed:
                            units += str(self.players[self.playerId].units.index(i)) + ","
                    else:
                        units += str(self.players[self.playerId].units.index(i)) + ","
                else:
                    self.parent.pushChange((str(self.players[self.playerId].units.index(i)) + ","), Flag(i,t.Target([attackedUnit.position[0],attackedUnit.position[1],0]),FlagState.MOVE))
            if units != "":
                self.parent.pushChange(units, Flag(i,attackedUnit,FlagState.ATTACK))
            if attackedUnit.type == attackedUnit.MOTHERSHIP or attackedUnit.type == attackedUnit.ATTACK_SHIP:
                    unit = self.players[self.playerId].units[int(units.split(",")[0])]
                    self.parent.pushChange((str(self.players[attackedUnit.owner].units.index(attackedUnit)) + ","), Flag(attackedUnit.owner,unit,FlagState.ATTACK))

    def setGatherFlag(self,ship,ressource):
        units = str(self.players[self.playerId].units.index(ship)) + ","
        self.parent.pushChange(units, Flag(t.Target([0,0,0]),ressource, FlagState.GATHER))
    
    def setLandingFlag(self, unit, planet):
        solarsystemId = 0
        planetIndex = 0
        for i in self.galaxy.solarSystemList:
            for j in i.planets:
                if j == planet:
                    solarsystemId = self.galaxy.solarSystemList.index(i)
                    planetIndex = self.galaxy.solarSystemList[solarsystemId].planets.index(planet)
        self.parent.pushChange(str(self.players[self.playerId].units.index(unit)), (solarsystemId, planetIndex, FlagState.LAND))

    def setMotherShipRallyPoint(self, pos):
        self.parent.pushChange(0, Flag(finalTarget = pos, flagState = FlagState.CHANGE_RALLY_POINT))

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

    #Trade entre joueurs
    def setTradeFlag(self, item, playerId2, quantite):
        for i in items:
            self.parent.pushChange(playerId2, Flag(i, quantite[items.index(i)], FlagState.TRADE))

    #Pour ajouter une unit
    def addUnit(self, unit):
        mineralCost = u.Unit.BUILD_COST[unit][0]
        gazCost = u.Unit.BUILD_COST[unit][1]
        if self.players[self.playerId].gaz - gazCost >= 0 and self.players[self.playerId].mineral - mineralCost >= 0:
            self.parent.pushChange(0, Flag(finalTarget = unit, flagState = FlagState.CREATE))

    def cancelUnit(self, unit):
        self.parent.pushChange(0, Flag(finalTarget = unit, flagState = FlagState.CANCEL_UNIT))
            
    #Pour effacer un Unit
    def eraseUnit(self):
        if len(self.players[self.playerId].selectedObjects) > 0:
            if isinstance(self.players[self.playerId].selectedObjects[len(self.players[self.playerId].selectedObjects)-1], u.Unit) and self.players[self.playerId].selectedObjects[len(self.players[self.playerId].selectedObjects)-1].type != self.players[self.playerId].selectedObjects[len(self.players[self.playerId].selectedObjects)-1].MOTHERSHIP:
                self.parent.pushChange(self.players[self.playerId].units.index(self.players[self.playerId].selectedObjects[len(self.players[self.playerId].selectedObjects)-1]), Flag(None,None,FlagState.DESTROY))
                
    #Pour effacer tous les units
    def eraseUnits(self, playerId=None):
        if playerId == None:
            playerId = self.playerId
        self.parent.pushChange(playerId, Flag(None,playerId,FlagState.DESTROY_ALL))    #Pour selectionner une unit

    def selectUnitEnemy(self, posSelected):
        if self.players[self.playerId].currentPlanet == None:
            if len(self.players[self.playerId].selectedObjects) > 0:
                    for i in self.players:
                        if i != self.players[self.playerId]:
                            for j in i.units:
                                if j.isAlive:
                                    if j.position[0] >= pos[0]-j.SIZE[j.type][0]/2 and j.position[0] <= pos[0]+j.SIZE[j.type][0]/2 :
                                        if j.position[1] >= pos[1]-j.SIZE[j.type][1]/2  and j.position[1] <= pos[1]+j.SIZE[j.type][1]/2 :
                                            self.setAttackFlag(j)

    def select(self, posSelected):
        if self.players[self.playerId].currentPlanet == None:
            #Si on selectionne une unit dans l'espace             
            for j in self.players[self.playerId].units:
                if j.isAlive:
                    if j.position[0] >= posSelected[0]-(j.SIZE[j.type][0]/2) and j.position[0] <= posSelected[0]+(j.SIZE[j.type][0]/2):
                        if j.position[1] >= posSelected[1]-(j.SIZE[j.type][1]/2) and j.position[1] <= posSelected[1]+(j.SIZE[j.type][1]/2): 
                            if self.multiSelect == False:
                                if j.type == j.TRANSPORT:
                                    if not j.landed:
                                        self.players[self.playerId].selectedObjects = []
                                else:
                                    self.players[self.playerId].selectedObjects = []
                            if j not in self.players[self.playerId].selectedObjects:
                                if j.type == j.TRANSPORT:
                                    if not j.landed:
                                        self.players[self.playerId].selectedObjects.append(j)
                                else:
                                    self.players[self.playerId].selectedObjects.append(j)
            #Si on selectionne une planete
            for i in self.galaxy.solarSystemList:
                for j in i.planets:
                    if j.position[0] >= posSelected[0]-j.IMAGE_WIDTH/2 and j.position[0] <= posSelected[0]+j.IMAGE_WIDTH/2:
                        if j.position[1] >= posSelected[1]-j.IMAGE_HEIGHT/2 and j.position[1] <= posSelected[1]+j.IMAGE_HEIGHT/2:
                            if j not in self.players[self.playerId].selectedObjects:
                                if self.players[self.playerId].inViewRange(j.position) or j.alreadyLanded(self.playerId):
                                    self.players[self.playerId].selectedObjects = []
                                    self.players[self.playerId].selectedObjects.append(j)
                            else:
                                if j.alreadyLanded(self.players[self.playerId].id):
                                    self.players[self.playerId].currentPlanet = j
                                    self.view.changeBackground('PLANET')
                                    spot = j.getLandingSpot(self.playerId)
                                    self.players[self.playerId].camera.position = [spot.position[0], spot.position[1]]
                                    self.players[self.playerId].camera.placeOnLanding()
                                    self.view.drawPlanetGround(j)
                                
                for j in i.nebulas:
                    if j.position[0] >= posSelected[0]-j.NEBULA_WIDTH/2 and j.position[0] <= posSelected[0]+j.NEBULA_WIDTH/2:
                        if j.position[1] >= posSelected[1]-j.NEBULA_HEIGHT/2 and j.position[1] <= posSelected[1]+j.NEBULA_HEIGHT/2:
                            if j not in self.players[self.playerId].selectedObjects and self.players[self.playerId].inViewRange(j.position):
                                self.players[self.playerId].selectedObjects = []
                                self.players[self.playerId].selectedObjects.append(j)
                for j in i.asteroids:
                    if j.position[0] >= posSelected[0]-j.ASTEROID_WIDTH/2 and j.position[0] <= posSelected[0]+j.ASTEROID_WIDTH/2:
                        if j.position[1] >= posSelected[1]-j.ASTEROID_HEIGHT/2 and j.position[1] <= posSelected[1]+j.ASTEROID_HEIGHT/2:
                            if j not in self.players[self.playerId].selectedObjects and self.players[self.playerId].inViewRange(j.position):
                                self.players[self.playerId].selectedObjects = []
                                self.players[self.playerId].selectedObjects.append(j)
            self.view.actionMenuType = self.view.MAIN_MENU
        else:
            planet = self.players[self.playerId].currentPlanet
            for i in planet.landingZones:
                if posSelected[0] > i.position[0]-i.WIDTH/2 and posSelected[0] < i.position[0]+i.WIDTH/2:
                    if posSelected[1] > i.position[1]-i.HEIGHT/2 and posSelected[1] < i.position[1]+i.HEIGHT/2:
                        if i not in self.players[self.playerId].selectedObjects:
                            self.players[self.playerId].selectedObjects = []
                            self.players[self.playerId].selectedObjects.append(i)
            for i in planet.minerals:
                if posSelected[0] > i.position[0]-i.WIDTH/2 and posSelected[0] < i.position[0]+i.WIDTH/2:
                    if posSelected[1] > i.position[1]-i.HEIGHT/2 and posSelected[1] < i.position[1]+i.HEIGHT/2:
                        if i not in self.players[self.playerId].selectedObjects:
                            self.players[self.playerId].selectedObjects = []
                            self.players[self.playerId].selectedObjects.append(i)
            for i in planet.gaz:
                if posSelected[0] > i.position[0]-i.WIDTH/2 and posSelected[0] < i.position[0]+i.WIDTH/2:
                    if posSelected[1] > i.position[1]-i.HEIGHT/2 and posSelected[1] < i.position[1]+i.HEIGHT/2:
                        if i not in self.players[self.playerId].selectedObjects:
                            self.players[self.playerId].selectedObjects = []
                            self.players[self.playerId].selectedObjects.append(i)
            for i in planet.units:
                if posSelected[0] > i.position[0]-i.SIZE[i.type][0]/2 and posSelected[0] < i.position[0]+i.SIZE[i.type][0]/2:
                    if posSelected[1] > i.position[1]-i.SIZE[i.type][1]/2 and posSelected[1] < i.position[1]++i.SIZE[i.type][1]/2:
                        if i not in self.players[self.playerId].selectedObjects:
                            self.players[self.playerId].selectedObjects = []
                            self.players[self.playerId].selectedObjects.append(i)
    def selectAll(self, posSelected):
        if self.players[self.playerId].currentPlanet == None:
            self.select(posSelected)
            if len(self.players[self.playerId].selectedObjects) > 0:
                unitToCheck = self.players[self.playerId].selectedObjects[0]
                cam = self.players[self.playerId].camera
                for j in self.players[self.playerId].units:
                    if j.position[0] > cam.position[0]-cam.screenWidth/2 and j.position[0] < cam.position[0]+cam.screenWidth/2:
                        if j.position[1] > cam.position[1]-cam.screenHeight/2 and j.position[1] < cam.position[1]+cam.screenHeight/2:
                            if j.name == unitToCheck.name:
                                if j != unitToCheck:
                                    if j.type == j.TRANSPORT:
                                        if not j.landed:
                                            self.players[self.playerId].selectedObjects.append(j)
                                    else:
                                        self.players[self.playerId].selectedObjects.append(j)
        self.view.actionMenuType = self.view.MAIN_MENU

    def rightClic(self, pos):
        empty = True
        if self.players[self.playerId].currentPlanet == None:
            for i in self.galaxy.solarSystemList:
                for j in i.planets:
                    if pos[0] > j.position[0]-j.IMAGE_WIDTH/2 and pos[0] < j.position[0]+j.IMAGE_WIDTH/2:
                        if pos[1] > j.position[1]-j.IMAGE_HEIGHT/2 and pos[1] < j.position[1]+j.IMAGE_HEIGHT/2:
                            if len(self.players[self.playerId].selectedObjects) > 0:
                                if isinstance(self.players[self.playerId].selectedObjects[0], w.AstronomicalObject) == False and isinstance(self.players[self.playerId].selectedObjects[0], w.Planet) == False:               
                                    if self.players[self.playerId].selectedObjects[0].type == u.Unit.TRANSPORT:
                                        self.setLandingFlag(self.players[self.playerId].selectedObjects[0], j)
                                        empty = False
            if empty:
                if len(self.players[self.playerId].selectedObjects) > 0:
                    for i in self.galaxy.solarSystemList:
                        for j in i.asteroids:
                            if pos[0] > j.position[0]-j.ASTEROID_WIDTH/2 and pos[0] < j.position[0]+j.ASTEROID_WIDTH/2:
                                if pos[1] > j.position[1]-j.ASTEROID_HEIGHT/2 and pos[1] < j.position[1]+j.ASTEROID_HEIGHT/2:
                                        for unit in self.players[self.playerId].selectedObjects:
                                            if isinstance(unit, w.AstronomicalObject) == False and isinstance(unit, w.Planet) == False:
                                                if unit.type == unit.CARGO:
                                                    self.setGatherFlag(unit, j)
                                                    empty = False
            if empty:
                if len(self.players[self.playerId].selectedObjects) > 0:
                    for i in self.galaxy.solarSystemList:
                        for j in i.nebulas:
                            if pos[0] > j.position[0]-j.NEBULA_WIDTH/2 and pos[0] < j.position[0]+j.NEBULA_WIDTH/2:
                                if pos[1] > j.position[1]-j.NEBULA_HEIGHT/2 and pos[1] < j.position[1]+j.NEBULA_HEIGHT/2:
                                        for unit in self.players[self.playerId].selectedObjects:
                                            if isinstance(unit, w.AstronomicalObject) == False and isinstance(unit, w.Planet) == False:
                                                if unit.type == unit.CARGO:
                                                    self.setGatherFlag(unit, j)
                                                    empty = False
            if empty:
                if len(self.players[self.playerId].selectedObjects) > 0:
                    if pos[0] > self.players[self.playerId].motherShip.position[0]-u.Unit.SIZE[u.Unit.MOTHERSHIP][0]/2 and pos[0] < self.players[self.playerId].motherShip.position[0]+u.Unit.SIZE[u.Unit.MOTHERSHIP][0]/2:
                                if pos[1] > self.players[self.playerId].motherShip.position[1]-u.Unit.SIZE[u.Unit.MOTHERSHIP][1]/2 and pos[1] < self.players[self.playerId].motherShip.position[1]+u.Unit.SIZE[u.Unit.MOTHERSHIP][1]/2:
                                        for unit in self.players[self.playerId].selectedObjects:
                                            if isinstance(unit, w.AstronomicalObject) == False and isinstance(unit, w.Planet) == False:
                                                if unit.type == unit.CARGO:
                                                    self.setGatherFlag(unit, j)
                                                    empty = False
            if empty:
                if len(self.players[self.playerId].selectedObjects) > 0:
                    for i in self.players:
                        if i != self.players[self.playerId]:
                            for j in i.units:
                                if j.isAlive:
                                    if j.position[0] >= pos[0]-j.SIZE[j.type][0]/2 and j.position[0] <= pos[0]+j.SIZE[j.type][0]/2:
                                        if j.position[1] >= pos[1]-j.SIZE[j.type][1]/2 and j.position[1] <= pos[1]+j.SIZE[j.type][1]/2:
                                            self.setAttackFlag(j)
                                            empty = False
            if empty:
                self.setMovingFlag(pos[0],pos[1])
            self.view.drawWorld()
        else:
            if empty:
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
        first = True
        if self.players[self.playerId].currentPlanet == None:
            for i in self.players[self.playerId].units:
                if i.isAlive:
                    if i.position[0] >= realStart[0]-i.SIZE[i.type][0]/2 and i.position[0] <= realEnd[0]+i.SIZE[i.type][0]/2:
                        if i.position[1] >= realStart[1]-i.SIZE[i.type][1]/2 and i.position[1] <= realEnd[1]+i.SIZE[i.type][1]/2:
                            if first:
                                self.players[self.playerId].selectedObjects = []
                                first = False
                            if isinstance(i, u.Mothership) == False:
                                if i.type == i.TRANSPORT:
                                    if not i.landed:
                                        self.players[self.playerId].selectedObjects.append(i)
                                else:
                                    self.players[self.playerId].selectedObjects.append(i)
        else:
            for i in self.players[self.playerId].currentPlanet.units:
                if i.isAlive:
                    if i.position[0] >= realStart[0]-i.SIZE[i.type][0]/2 and i.position[0] <= realEnd[0]+i.SIZE[i.type][0]/2:
                        if i.position[1] >= realStart[1]-i.SIZE[i.type][1]/2 and i.position[1] <= realEnd[1]+i.SIZE[i.type][1]/2:
                            if first:
                                self.players[self.playerId].selectedObjects = []
                                first = False
                            self.players[self.playerId].selectedObjects.append(i)
        self.view.actionMenuType = self.view.MAIN_MENU
        
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
        self.view.redrawMinimap()
        self.view.drawWorld()
        
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
