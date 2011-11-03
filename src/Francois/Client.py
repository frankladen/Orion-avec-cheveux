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

class Controller():
    def __init__(self):
        self.players = [] #La liste des joueurs
        self.playerId = 0 #Le id du joueur courant
        self.refresh = 0
        self.mess = []
        self.changes = []
        self.playerIp = socket.gethostbyname(socket.getfqdn())
        self.server = None
        self.isStarted=False
        self.view = v.View(self)
        self.multiSelect = False
        self.currentFrame = None
        self.attenteEcrit = False
        self.view.root.mainloop()
        
 #Pour changer le flag des unites selectionne pour le deplacement    
    def setMovingFlag(self,x,y):
        units = ''
        send = False
        #Si plusieurs unit�s sont s�lectionn�es, on les ajoute toutes dans le changement � envoyer
        for i in self.players[self.playerId].selectedObjects:
            if isinstance(i, u.SpaceAttackUnit):
                i.attackcount = i.AttackSpeed
            if isinstance(i, u.Unit) and i.type != i.MOTHERSHIP:              
                units += str(self.players[self.playerId].units.index(i)) + ","
                send = True
            elif isinstance(i, u.Mothership):
                self.setMotherShipRallyPoint([x,y,0])
        if send:
            self.pushChange(units, Flag(i,t.Target([x,y,0]),FlagState.MOVE))

    def setDefaultMovingFlag(self,x,y, unit):
        units = ''
        send = False
        #Si plusieurs unit�s sont s�lectionn�es, on les ajoute toutes dans le changement � envoyer

        if isinstance(unit, u.SpaceAttackUnit):
            unit.attackcount = unit.AttackSpeed               
        units += str(self.players[self.playerId].units.index(unit)) + ","
        self.pushChange(units, Flag(unit,t.Target([x,y,0]),FlagState.MOVE))
    
    #Pour changer le flag des unites selectionne pour l'arret
    def setStandbyFlag(self):
        units = ""
        #Si plusieurs unit�s sont s�lectionn�es, on les ajoute toutes dans le changement � envoyer
        for i in self.players[self.playerId].selectedObjects:
            if isinstance(i, u.SpaceAttackUnit): 
                i.attackcount = i.AttackSpeed
            if isinstance(i, u.Unit):
                units += str(self.players[self.playerId].units.index(i)) + ","
        if units != "":
            self.pushChange(units, Flag(i,t.Target([0,0,0]),FlagState.STANDBY))

    def setAStandByFlag(self, unit):
        units = str(self.players[self.playerId].units.index(unit)) + ","
        self.pushChange(units, Flag(i,t.Target([0,0,0]),FlagState.STANDBY))

    def setPatrolFlag(self, pos):
        units = ''
        send = False
        #Si plusieurs unit�s sont s�lectionn�es, on les ajoute toutes dans le changement � envoyer
        for i in self.players[self.playerId].selectedObjects:
            if isinstance(i, u.SpaceAttackUnit) and i.type != i.MOTHERSHIP:
                i.attackcount = i.AttackSpeed
                units += str(self.players[self.playerId].units.index(i)) + ","
                send = True
            elif isinstance(i, u.Unit) and i.type != i.MOTHERSHIP:
                units += str(self.players[self.playerId].units.index(i)) + ","
                send = True
        if send:
            self.pushChange(units, Flag(i,t.Target([pos[0],pos[1],0]),FlagState.PATROL))
            
    #Pour changer le flag des unit�s s�lectionn�s pour attaquer        
    def setAttackFlag(self, attackedUnit):
        attacking = True
        if attacking:
            units = ""
            for i in self.players[self.playerId].selectedObjects:
                if isinstance(i, u.SpaceAttackUnit):
                    if attackedUnit.type == u.Unit.TRANSPORT:
                        if not attackedUnit.landed:
                            i.attackcount = i.AttackSpeed
                            units += str(self.players[self.playerId].units.index(i)) + ","
                    else:
                        i.attackcount = i.AttackSpeed
                        units += str(self.players[self.playerId].units.index(i)) + ","
                else:
                    self.pushChange((str(self.players[self.playerId].units.index(i)) + ","), Flag(i,t.Target([attackedUnit.position[0],attackedUnit.position[1],0]),FlagState.MOVE))
            if units != "":
                self.pushChange(units, Flag(i,attackedUnit,FlagState.ATTACK))

    def setGatherFlag(self,ship,ressource):
        units = str(self.players[self.playerId].units.index(ship)) + ","
        self.pushChange(units, Flag(t.Target([0,0,0]),ressource, FlagState.GATHER))
    
    def setLandingFlag(self, unit, planet):
        solarsystemId = 0
        planetIndex = 0
        for i in self.galaxy.solarSystemList:
            for j in i.planets:
                if j == planet:
                    solarsystemId = self.galaxy.solarSystemList.index(i)
                    planetIndex = self.galaxy.solarSystemList[solarsystemId].planets.index(planet)
        self.pushChange(str(self.players[self.playerId].units.index(unit)), (solarsystemId, planetIndex, FlagState.LAND))

    def setMotherShipRallyPoint(self, pos):
        self.pushChange(0, Flag(finalTarget = pos, flagState = FlagState.CHANGE_RALLY_POINT))
        
    #Pour ajouter une unit
    def addUnit(self, unit):
        mineralCost = u.Unit.BUILD_COST[unit][0]
        gazCost = u.Unit.BUILD_COST[unit][1]
        if self.players[self.playerId].gaz - gazCost >= 0 and self.players[self.playerId].mineral - mineralCost >= 0:
            self.pushChange(0, Flag(finalTarget = unit, flagState = FlagState.CREATE))

    def cancelUnit(self, unit):
        self.pushChange(0, Flag(finalTarget = unit, flagState = FlagState.CANCEL_UNIT))
    
    #Trade entre joueurs
    def tradePlayers(self, items, playerId2, quantite):
        for i in items:
            self.pushChange(i, (self.playerId2, quantite))
            
    #Pour effacer un Unit
    def eraseUnit(self):
        if len(self.players[self.playerId].selectedObjects) > 0:
            if isinstance(self.players[self.playerId].selectedObjects[len(self.players[self.playerId].selectedObjects)-1], u.Unit) and self.players[self.playerId].selectedObjects[len(self.players[self.playerId].selectedObjects)-1].type != self.players[self.playerId].selectedObjects[len(self.players[self.playerId].selectedObjects)-1].MOTHERSHIP:
                self.pushChange(self.players[self.playerId].units.index(self.players[self.playerId].selectedObjects[len(self.players[self.playerId].selectedObjects)-1]), Flag(None,None,FlagState.DESTROY))
                
    #Pour effacer tous les units
    def eraseUnits(self, playerId=None):
        if playerId == None:
            playerId = self.playerId
        self.pushChange(playerId, 'deleteAllUnits')    #Pour selectionner une unit

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

    #Selection avec le clic-drag
    def boxSelect(self, selectStart, selectEnd):
        if self.players[self.playerId].currentPlanet == None:
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
        self.view.actionMenuType = self.view.MAIN_MENU
        
    #Deplacement rapide de la camera vers un endroit de la minimap
    def quickMove(self, x,y, canva):
        if self.players[self.playerId].currentPlanet == None:
            posSelected = self.players[self.playerId].camera.calcPointOnMap(x,y)
            self.players[self.playerId].camera.position = posSelected
        
    def takeOff(self, ship, planet, playerId):
        ship.takeOff(planet)
        self.players[playerId].currentPlanet = None
        self.view.drawWorld()
        
    def setTakeOffFlag(self, ship, planet):
        planetId = 0
        sunId = 0
        shipId = self.players[self.playerId].units.index(ship)
        for i in self.galaxy.solarSystemList:
            for j in i.planets:
                if j == planet:
                    planetId = i.planets.index(j)
                    sunId = self.galaxy.solarSystemList.index(i)
        self.pushChange(shipId,(planetId, sunId, 'TAKEOFF'))
    #Envoyer le message pour le chat
    def sendMessage(self, mess):
        if mess == "forcegaz":
            self.players[self.playerId].gaz += 500
        elif mess == "forcemine":
            self.players[self.playerId].mineral += 500
        elif len(mess)>0:
            mess = mess.replace('\\','/')
            self.server.addMessage(mess, self.players[self.playerId].name)

    def sendMessageLobby(self, mess, nom):
        mess = mess.replace('\\','/')
        self.server.addMessage(mess, self.server.getSockets()[self.playerId][1])

    #Pour aller chercher les nouveaux messages
    def refreshMessages(self, chat):
        textChat=''
        for i in range(len(self.mess), len(self.server.getMessage())):
            self.mess.append(self.server.getMessage()[i])
        if len(self.mess) > 5:
            for i in range(len(self.mess)-5, len(self.mess)):
                textChat+=self.mess[i]+'\r'
        else:
            for i in range(0, len(self.mess)):
                textChat+=self.mess[i]+'\r'
        chat.config(text=textChat)

    def choiceColor(self, name ,index, mode):
        response = self.server.isThisColorChosen(self.view.variableColor.get(),self.playerId)
        if response == True:
            self.view.colorAlreadyChosen()
            
    #TIMER D'ACTION DU JOUEUR COURANT
    def action(self, waitTime=50):
        if self.server.isGameStopped() == True and self.view.currentFrame == self.view.gameFrame:
            if self.playerId != 0:
                self.view.showGameIsFinished()
                self.view.root.destroy()
        elif self.view.currentFrame != self.view.pLobby:
            if self.refresh > 0:
                self.players[self.playerId].camera.move()
                for p in self.players:
                    for i in p.units:
                        if i.isAlive:
                            if i.flag.flagState == FlagState.MOVE:
                                i.move()
                            elif i.flag.flagState == FlagState.ATTACK:
                                if isinstance(i.flag.finalTarget, u.TransportShip):
                                    if i.flag.finalTarget.landed:
                                        self.setAStandByFlag(i)
                                killedIndex = i.attack(self.players)
                                if killedIndex[0] > -1:
                                    self.killUnit(killedIndex)
                            elif i.flag.flagState == FlagState.PATROL:
                                unit = i.patrol(self.players)
                                if unit != None:
                                    self.setAttackFlag(unit)
                            elif i.flag.flagState == FlagState.LAND:
                                i.land(self, self.players.index(p))
                            elif i.flag.flagState == FlagState.GATHER:
                                i.gather(p,self)
                    if p.motherShip.isAlive:
                        p.motherShip.action()
                        if len(p.motherShip.unitBeingConstruct) > 0:
                            if(p.motherShip.isUnitFinished()):
                                self.buildUnit(p)
                        else:
                            p.motherShip.flag.flagState = FlagState.STANDBY
                    else:
                        p.motherShip.unitBeingConstruct = []
                        self.eraseUnits(self.players.index(p))
                if self.refresh % 10 == 0:
                    self.refreshMessages(self.view.menuModes.chat)
                self.refresh+=1
                self.view.showMinerals.config(text="Mineraux: "+str(self.players[self.playerId].mineral))
                self.view.showGaz.config(text="Gaz: "+str(self.players[self.playerId].gaz))
	            #À chaque itération je pousse les nouveaux changements au serveur et je demande des nouvelles infos.
                self.pullChange()
                self.view.createUnitsConstructionPanel()
                if self.players[self.playerId].currentPlanet == None:
                    self.view.drawWorld()
                else:
                    self.view.drawPlanetGround(self.players[self.playerId].currentPlanet)
                    self.view.redrawMinimap()
                waitTime = self.server.amITooHigh(self.playerId)

            else:
                self.refreshMessages(self.view.menuModes.chat)
                response = self.server.isEveryoneReady(self.playerId)
                if response:
                    self.refresh+=1
                    if self.playerId == 0:
                        self.sendMessage("La partie va maintenant débuter.")
                else:
                    if self.playerId == 0 and self.attenteEcrit == False:
                        self.attenteEcrit=True
                        self.sendMessage("Attente des autres joueurs.")
        else:
            if self.server.isGameStarted() == True:
                self.startGame()
            else:
                waitTime=1000
                self.refreshMessages(self.view.chatLobby)
                self.view.redrawLobby(self.view.pLobby)
        self.view.root.after(waitTime, self.action)
        
    def killUnit(self, killedIndexes):
        #Désélection de l'unité qui va mourir afin d'éviter le renvoie d'une actio avec cette unité
        if killedIndexes[1] == self.playerId:
            if self.players[self.playerId].units[killedIndexes[0]] in self.players[self.playerId].selectedObjects:
               self.players[self.playerId].selectedObjects.remove(self.players[self.playerId].units[killedIndexes[0]])
        self.players[killedIndexes[1]].units[killedIndexes[0]].kill()

    def buildUnit(self, player):
        unit = player.motherShip.unitBeingConstruct.pop(0)
        unit.changeFlag(t.Target(player.motherShip.rallyPoint), FlagState.MOVE)
        player.units.append(unit)
              
	#Connection au serveur			
    def connectServer(self, login, serverIP):
        self.server=Pyro4.core.Proxy("PYRO:ServeurOrion@"+serverIP+":54400")
        try:
            #Je demande au serveur si la partie est démarrée, si oui on le refuse de la partie, cela permet de vérifier
            #en même temps si le serveur existe réellement à cette adresse.
            if self.server.isGameStarted() == True:
                self.view.gameHasBeenStarted()
                self.view.changeFrame(self.view.mainMenu)
            else:
                #Je fais chercher auprès du serveur l'ID de ce client et par le fais même, le serveur prend connaissance de mon existence
                self.playerId=self.server.getNumSocket(login, self.playerIp)
                #Je vais au lobby, si la connection a fonctionner
                self.view.pLobby = self.view.fLobby()
                self.view.changeFrame(self.view.pLobby)
                self.action()
        except:
            self.view.loginFailed()
            self.view.changeFrame(self.view.mainMenu)
            
    #Enleve le joueur courant de la partie ainsi que ses units
    def removePlayer(self):
        if self.view.currentFrame == self.view.gameFrame:
            self.sendMessage('a quitté la partie')
            self.eraseUnits()
            self.server.removePlayer(self.playerIp, self.players[self.playerId].name, self.playerId)
        self.view.root.destroy()
        
    #Demmare la partie et genere la galaxie (Quand l'admin appui sur start game dans le lobby)    
    def startGame(self):
        if self.playerId==0:
            self.server.startGame()
        for i in range(0, len(self.server.getSockets())):
            if self.server.getSockets()[i][3] == -1:
                self.server.firstColorNotChosen(i)
            self.players.append(p.Player(self.server.getSockets()[i][1], i, self.server.getSockets()[i][3]))
        self.galaxy=w.Galaxy(self.server.getNumberOfPlayers(), self.server.getSeed())
        for i in range(0, len(self.server.getSockets())):
            startPos = self.galaxy.getSpawnPoint()
            self.players[i].addBaseUnits(startPos)  
        self.players[self.playerId].addCamera(self.galaxy, self.view.taille)
        self.view.gameFrame = self.view.fGame()
        self.view.changeFrame(self.view.gameFrame)
        self.view.root.after(50, self.action)
    
    #Méthode de mise à jour auprès du serveur, actionnée à chaque
    def pushChange(self, playerObject, flag):
        actionString = ""
        if isinstance(flag, Flag):
            if flag.flagState == FlagState.MOVE or flag.flagState == FlagState.STANDBY:
                actionString = str(self.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(flag.finalTarget.position)
            elif flag.flagState == FlagState.ATTACK:
                targetId = self.players[flag.finalTarget.owner].units.index(flag.finalTarget)
                actionString = str(self.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/U"+str(targetId)+"P"+str(flag.finalTarget.owner)
            elif flag.flagState == FlagState.CREATE:
                actionString = str(self.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState) + "/" + str(flag.finalTarget)
            elif flag.flagState == FlagState.CHANGE_RALLY_POINT:
                actionString = str(self.playerId) + "/" + "0" + "/" + str(flag.flagState) + "/" + str(flag.finalTarget)
            elif flag.flagState == FlagState.DESTROY:
                actionString = str(self.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/0"
            elif flag.flagState == FlagState.CANCEL_UNIT:
                actionString = str(self.playerId) + "/" + "0" + "/" + str(flag.flagState) + "/" + str(flag.finalTarget)
            elif flag.flagState == FlagState.PATROL:
                actionString = str(self.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(flag.finalTarget.position)
            elif flag.flagState == FlagState.GATHER:
                if isinstance(flag.finalTarget, w.AstronomicalObject):
                    if flag.finalTarget.type == 'nebula':
                        nebulaId = flag.finalTarget.id
                        solarId = flag.finalTarget.solarSystem.sunId
                        actionString = str(self.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(nebulaId)+","+str(solarId)+",0"
                    elif flag.finalTarget.type == 'asteroid':
                        mineralId = flag.finalTarget.id
                        solarId = flag.finalTarget.solarSystem.sunId
                        actionString = str(self.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(mineralId)+","+str(solarId)+",1"
                else:
                    actionString = str(self.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/retouraumothership,sansbriserlaactionstring,2"
            
        elif isinstance(flag, str):
            if flag == 'deleteAllUnits':
                actionString = str(self.playerId)+"/"+str(playerObject)+"/"+flag+"/deleteAllUnits"
            elif flag == 'changeFormation':
                actionString = str(self.playerId)+"/"+playerObject+"/"+flag+"/changementDeFormation"
		#Si c'est un échange
        elif isinstance(flag, tuple):
            if flag[2] == FlagState.LAND:
                actionString = str(self.playerId)+"/"+playerObject+"/"+str(flag[2])+"/"+str(flag[0])+","+str(flag[1])
            elif flag[2] == 'TAKEOFF':
                actionString = str(self.playerId)+"/"+str(playerObject)+"/"+str(flag[2])+"/"+str(flag[0])+","+str(flag[1])
            else:
                actionString = str(self.playerId)+"/"+playerObject+"/"+flag[0]+"/"+flag[1]
        self.server.addChange(actionString)
    
    def pullChange(self):
        toRemove = []
        for i in self.server.getChange(self.playerId, self.refresh):
            self.changes.append(i)
        for changeString in self.changes:
            if int(changeString.split("/")[4]) == self.refresh:
                self.doAction(changeString)
                toRemove.append(changeString)
        for tR in toRemove:
            self.changes.remove(tR)
    
    def doAction(self, changeString):
        changeInfo = changeString.split("/")
        actionPlayerId = int(changeInfo[0])
        unitIndex = changeInfo[1]
        unitIndex = unitIndex.split(",")
        action = changeInfo[2]
        target = changeInfo[3]
        refresh = int(changeInfo[4])
        #si l'action est Move, la target sera sous forme de tableau de positions [x,y,z]
        if action == str(FlagState.MOVE) or action == str(FlagState.STANDBY) or action == str(FlagState.PATROL):
            target = target.strip("[")
            target = target.strip("]")
            target = target.split(",")
            for i in range(0, len(target)):
                target[i]=math.trunc(float(target[i])) #nécessaire afin de s'assurer que les positions sont des entiers
            self.makeFormation(actionPlayerId, unitIndex, target, action)
        elif action == str(FlagState.ATTACK):
            target = target.split("P")
            target[0] = target[0].strip("U")
            for i in unitIndex:
                if i != '':
                    self.players[actionPlayerId].units[int(i)].changeFlag(self.players[int(target[1])].units[int(target[0])], int(action))
        elif action == str(FlagState.LAND):
            target = target.split(',')
            self.players[actionPlayerId].units[int(unitIndex[0])].changeFlag(self.galaxy.solarSystemList[int(target[0])].planets[int(target[1])],int(action))
        elif action == 'TAKEOFF':
            target = target.split(',')
            unit = self.players[actionPlayerId].units[int(unitIndex[0])]
            planet = self.galaxy.solarSystemList[int(target[1])].planets[int(target[0])]
            self.takeOff(unit, planet, actionPlayerId)
            if actionPlayerId == self.playerId:
                cam = self.players[self.playerId].camera
                cam.position = cam.defaultPos
                self.view.changeBackground('GALAXY')
        elif action == str(FlagState.GATHER):
            target = target.split(',')
            for i in unitIndex:
                if i != '':
                    i = int(i)
                    if target[2] == '0':
                        self.players[actionPlayerId].units[i].changeFlag(self.galaxy.solarSystemList[int(target[1])].nebulas[int(target[0])],int(action))
                    elif target[2] == '1':
                        self.players[actionPlayerId].units[i].changeFlag(self.galaxy.solarSystemList[int(target[1])].asteroids[int(target[0])],int(action))
                    else:
                        self.players[actionPlayerId].units[i].changeFlag(self.players[actionPlayerId].motherShip,int(action))
        
        #ici, le target sera l'index de l'unit� dans le tableau de unit du player cibl�
        
        elif action == str(FlagState.CREATE):
            self.players[actionPlayerId].motherShip.changeFlag(int(target),int(action))
            self.players[actionPlayerId].motherShip.action()
            self.players[actionPlayerId].gaz -= self.players[actionPlayerId].motherShip.unitBeingConstruct[len(self.players[actionPlayerId].motherShip.unitBeingConstruct)-1].buildCost[1]
            self.players[actionPlayerId].mineral -= self.players[actionPlayerId].motherShip.unitBeingConstruct[len(self.players[actionPlayerId].motherShip.unitBeingConstruct)-1].buildCost[0]
            self.players[actionPlayerId].motherShip.flag.flagState = FlagState.BUILD_UNIT
        
        elif action == str(FlagState.CHANGE_RALLY_POINT):
            self.players[actionPlayerId].motherShip.changeFlag(target,int(action))
        
        elif action == str(FlagState.CANCEL_UNIT):
            self.players[actionPlayerId].gaz += self.players[actionPlayerId].motherShip.unitBeingConstruct[int(target)].buildCost[1]
            self.players[actionPlayerId].mineral += self.players[actionPlayerId].motherShip.unitBeingConstruct[int(target)].buildCost[0]
            self.players[actionPlayerId].motherShip.changeFlag(target, int(action))

        elif action == str(FlagState.DESTROY):
            self.killUnit((int(unitIndex[0]),actionPlayerId))
        
        elif action == 'deleteAllUnits':
            self.players[int(unitIndex[0])].units = []
        
        elif action == 'changeFormation':
            if unitIndex[0]=='t':
                self.players[actionPlayerId].formation="triangle"
            elif unitIndex[0]=='c':
                self.players[actionPlayerId].formation="carre"
            unitIndex = []
            for i in self.players[actionPlayerId].selectedObjects:
                unitIndex.append(self.players[actionPlayerId].units.index(i))
            unitIndex.append(987123465)
            self.makeFormation(actionPlayerId, unitIndex, self.players[actionPlayerId].selectedObjects[0].flag.finalTarget.position, FlagState.MOVE)

        elif unitIndex == 'g' or unitIndex == 'm':
            if unitIndex == 'm':
                self.players[actionPlayerId].mineral-=quantite
                self.players[int(action)].mineral+=quantite
            elif unitIndex == 'g':
                self.players[actionPlayerId].gaz-=quantite
                self.players[int(action)].gaz+=quantite

    def makeFormation(self, actionPlayerId, unitIndex, target, action):
        lineTaken=[]
        line=0
        targetorig=[0,0]
        targetorig[0]=target[0]
        targetorig[1]=target[1]
        #Formation en carré selon le nombre de unit qui se déplace, OH YEAH
        if self.players[actionPlayerId].formation == "carre":
            thatLine = []
            lineTaken = []
            numberOfLines = math.sqrt(len(unitIndex)-1)
            if str(numberOfLines).split('.')[1] != '0':
                numberOfLines+=1
            math.trunc(float(numberOfLines))
            numberOfLines = int(numberOfLines)
            for l in range(0,numberOfLines):
                thatLine = []
                for k in range(0,numberOfLines):
                    thatLine.append(False)
                lineTaken.append(thatLine)
            for i in range(0,len(unitIndex)-1):
                goodPlace=False
                line=0
                while goodPlace==False:
                    for p in range(0,len(lineTaken[line])):
                        if lineTaken[line][p]==False:
                            lineTaken[line][p]=True
                            target[0]=targetorig[0]+(p*20)
                            if target[0] < -1*(self.galaxy.width/2)+9:
                                target[0] = -1*(self.galaxy.width/2)+18
                            elif target[0] > (self.galaxy.width/2)-9:
                                target[0] = (self.galaxy.width/2)-18
                            target[1]=targetorig[1]-(line*20)
                            if target[1] < -1*(self.galaxy.height/2)+9:
                                target[1] = -1*(self.galaxy.height/2)+18
                            goodPlace=True
                            break
                    if goodPlace==False:
                        line+=1
                        if (len(lineTaken)-1)<line:
                            numberOfSpaces=1+line
                            thatLine=[]
                            for a in range(0,numberOfSpaces):
                                thatLine.append(False)
                            lineTaken.append(thatLine)
                self.players[actionPlayerId].units[int(unitIndex[i])].changeFlag(t.Target([target[0],target[1],target[2]]),int(action))
        #Formation en triangle, FUCK YEAH
        elif self.players[actionPlayerId].formation == "triangle":
            thatLine=[]
            xLineBefore=[0,0,0,0,0,0,0,0,0,0,0,0]
            thatLine.append([False])
            lineTaken.append(thatLine[False])
            for i in range(0,len(unitIndex)-1):
                goodPlace=False
                line=0
                while goodPlace==False:
                    for p in range(0,len(lineTaken[line])):
                        if lineTaken[line][p]==False:
                            lineTaken[line][p]=True
                            if line != 0:
                                if p==len(lineTaken[line-1]):
                                    target[0]=targetorig[0]+(p*20)
                                    #jerome ajoute ca ici la largeur du vaisseau
                                    if target[0] > (self.galaxy.width/2)-9:
                                        target[0] = target[0]-(target[0]-(self.galaxy.width/2)+18)
                                    xLineBefore[p] = target[0]
                                else:
                                    target[0]=xLineBefore[p]-20
                                    if target[0] < -1*(self.galaxy.width/2)+9:
                                        target[0] = xLineBefore[p]
                                    elif target[0] > (self.galaxy.width/2)-9:
                                        target[0] = target[0]-(target[0]-(self.galaxy.width/2)+18)
                                    xLineBefore[p] = target[0]
                            target[1]=targetorig[1]-(line*20)
                            if target[1] < -1*(self.galaxy.height/2)+9:
                                target[1] = targetorig[1]
                            goodPlace=True
                            break
                    if goodPlace==False:
                        line+=1
                        if (len(lineTaken)-1)<line:
                            numberOfSpaces=1+line
                            thatLine=[]
                            for a in range(0,numberOfSpaces):
                                thatLine.append(False)
                            lineTaken.append(thatLine)
                    if line == 0:
                        xLineBefore[0] = target[0]
                self.players[actionPlayerId].units[int(unitIndex[i])].changeFlag(t.Target([target[0],target[1],target[2]]),int(action))


if __name__ == '__main__':
    c = Controller()
