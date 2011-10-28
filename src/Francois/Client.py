# -*- coding: UTF-8 -*-
import View as v
import World as w
import Player as p
import Target as t
import Unit as u
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
        
 #Pour changer le flagdes unites selectionne pour le deplacement    
    def setMovingFlag(self,x,y):
        units = ''
        send = False
        #Si plusieurs unit�s sont s�lectionn�es, on les ajoute toutes dans le changement � envoyer
        for i in self.players[self.playerId].selectedObjects:
            if isinstance(i, u.SpaceAttackUnit):
                i.attackcount = i.AttackSpeed
            if i.__module__ == 'Unit':                
                units += str(self.players[self.playerId].units.index(i)) + ","
                send = True
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
            if i.__module__ == 'Unit':
                units += str(self.players[self.playerId].units.index(i)) + ","
        if units != "":
            self.pushChange(units, Flag(i,t.Target([0,0,0]),FlagState.STANDBY))

    def setAStandByFlag(self, unit):
        units += str(self.players[self.playerId].units.index(unit)) + ","
        units = str(self.players[self.playerId].units.index(unit)) + ","
        self.pushChange(units, Flag(i,t.Target([0,0,0]),FlagState.STANDBY))
            
    #Pour changer le flag des unit�s s�lectionn�s pour attaquer        
    def setAttackFlag(self, attackedUnit):
        attacking = True
##        #posSelected = self.players[self.playerId].camera.calcPointInWorld(x,y)
##        for i in self.players:
##            if i.id != self.playerId:
##                for j in i.units:
##                    if j.position[0] >= x-8 and j.position[0] <= x+8:
##                        if j.position[1] >= y-8 and j.position[1] <= y+8:
##                            attacking = True
##                            attackedUnit = j
##                            break
        if attacking:
            units = ""
            for i in self.players[self.playerId].selectedObjects:
                if isinstance(i, u.SpaceAttackUnit):
                    if attackedUnit.name == 'Transport':
                        if not attackedUnit.landed:
                            i.attackcount = i.AttackSpeed
                            units += str(self.players[self.playerId].units.index(i)) + ","
                    else:
                        i.attackcount = i.AttackSpeed
                        units += str(self.players[self.playerId].units.index(i)) + ","
            if units != "":
                self.pushChange(units, Flag(i,attackedUnit,FlagState.ATTACK))

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
        print(Flag(unit, FlagState.CREATE).flagState)
        self.pushChange(0, Flag(finalTarget = unit, flagState = FlagState.CREATE))
            
    #Trade entre joueurs
    def tradePlayers(self, items, playerId2, quantite):
        for i in items:
            self.pushChange(i, (self.playerId2, quantite))
            
    #Pour effacer un Unit
    def eraseUnit(self):
        if len(self.players[self.playerId].selectedObjects) > 0:
            if self.players[self.playerId].selectedObjects[len(self.players[self.playerId].selectedObjects)-1].__module__ == 'Unit':
                self.pushChange(self.players[self.playerId].selectedObjects[len(self.players[self.playerId].selectedObjects)-1], 'deleteUnit')
                self.players[self.playerId].selectedObjects.pop(len(self.players[self.playerId].selectedObjects)-1)
                
    #Pour effacer tous les units
    def eraseUnits(self):
        self.pushChange('lollegarspartdelagame', 'deleteAllUnits')    #Pour selectionner une unit

    def select(self, posSelected):
        if self.players[self.playerId].currentPlanet == None:
            #Si on selectionne une unit dans l'espace             
            for j in self.players[self.playerId].units:
                if j.isAlive:
                    if j.position[0] >= posSelected[0]-8 and j.position[0] <= posSelected[0]+8:
                        if j.position[1] >= posSelected[1]-8 and j.position[1] <= posSelected[1]+8: 
                            if self.multiSelect == False:
                                if j.name == 'Transport':
                                    if not j.landed:
                                        self.players[self.playerId].selectedObjects = []
                                else:
                                    self.players[self.playerId].selectedObjects = []
                            if j not in self.players[self.playerId].selectedObjects:
                                if j.name == 'Transport':
                                    if not j.landed:
                                        self.players[self.playerId].selectedObjects.append(j)
                                else:
                                    self.players[self.playerId].selectedObjects.append(j)
            #Si on selectionne une planete
            for i in self.galaxy.solarSystemList:
                for j in i.planets:
                    if j.position[0] >= posSelected[0]-10 and j.position[0] <= posSelected[0]+10:
                        if j.position[1] >= posSelected[1]-10 and j.position[1] <= posSelected[1]+10:
                            if j not in self.players[self.playerId].selectedObjects:
                                if self.players[self.playerId].inViewRange(j.position):
                                    self.players[self.playerId].selectedObjects = []
                                    self.players[self.playerId].selectedObjects.append(j)
                            else:
                                if j.alreadyLanded(self.players[self.playerId].id):
                                    self.players[self.playerId].currentPlanet = j
                                    self.view.changeBackground('PLANET')
                                    self.view.drawPlanetGround(j)
                                
                for j in i.nebulas:
                    if j.position[0] >= posSelected[0]-10 and j.position[0] <= posSelected[0]+10:
                        if j.position[1] >= posSelected[1]-10 and j.position[1] <= posSelected[1]+10:
                            if j not in self.players[self.playerId].selectedObjects and self.players[self.playerId].inViewRange(j.position):
                                self.players[self.playerId].selectedObjects = []
                                self.players[self.playerId].selectedObjects.append(j)
                for j in i.asteroids:
                    if j.position[0] >= posSelected[0]-10 and j.position[0] <= posSelected[0]+10:
                        if j.position[1] >= posSelected[1]-10 and j.position[1] <= posSelected[1]+10:
                            if j not in self.players[self.playerId].selectedObjects and self.players[self.playerId].inViewRange(j.position):
                                self.players[self.playerId].selectedObjects = []
                                self.players[self.playerId].selectedObjects.append(j)
            self.view.actionMenuType = MenuType.MAIN
        
    def selectAll(self, posSelected):
        if self.players[self.playerId].currentPlanet == None:
            for j in self.players[self.playerId].units:
                if j.isAlive:
                    if j.position[0] >= posSelected[0]-8 and j.position[0] <= posSelected[0]+8:
                        if j.position[1] >= posSelected[1]-8 and j.position[1] <= posSelected[1]+8:
                            self.players[self.playerId].selectedObjects = []
                            if j.name == 'Transport':
                                if not j.landed:
                                    self.players[self.playerId].selectedObjects.append(j)
                                else:
                                    self.players[self.playerId].selectedObjects.append(j)
                            break
            cam = self.players[self.playerId].camera
            for j in self.players[self.playerId].units:
                if j.position[0] > cam.position[0]-cam.screenWidth/2 and j.position[0] < cam.position[0]+cam.screenWidth/2:
                    if j.position[1] > cam.position[1]-cam.screenHeight/2 and j.position[1] < cam.position[1]+cam.screenHeight/2:
                        if j.name == self.players[self.playerId].selectedObjects[0].name:
                            if j != self.players[self.playerId].selectedObjects[0]:
                                if j.name == 'Transport':
                                    if not j.landed:
                                        self.players[self.playerId].selectedObjects.append(j)
                                else:
                                    self.players[self.playerId].selectedObjects.append(j)
        self.view.actionMenuType = MenuType.MAIN
    #===========================================================================
    # def rightClick(self, x, y):
    #    toAttack = []
    #    toGather = []
    #    toLand = []
    #    toMove = []
    #    for u in self.players[self.playerId].selectObjects:
    #        if u.name.find('Scout'):
    #            toMove.append(u)
    #        elif isinstance(self.players[self.playerId].selectedObjects[0], u.SpaceAttackUnit):
    #            for i in self.players:
    #                if i != self.players[self.playerId]:
    #                    for j in i.units:
    #                        if j.isAlive:
    #                            if j.position[0] >= x-8 and j.position[0] <= x+8:
    #                                if j.position[1] >= y-8 and j.position[1] <= y+8: 
    #                                    toAttack.append(u)
    #                            else:
    #                                toMove.append(u)
    #        elif isinstance(self.players[self.playerId].selectedObjects[0], u.SpaceLandingUnit):
    #            for i in self.galaxy.solarSystemList:
    #                for j in i.planets:
    #                    if j.position[0] >= x-10 and j.position[0] <= x+10:
    #                        if j.position[1] >= y-10 and j.position[1] <= y+10:
    #                            if j not in self.players[self.playerId].selectedObjects and self.players[self.playerId].inViewRange(j.position):
    #                                toLand.append(u)
    #                            else:
    #                                toMove.append(u)
    #               
    #        elif isinstance(self.players[self.playerId].selectedObjects[0], u.SpaceGatherUnit):
    #             for j in i.nebulas:
    #                if j.position[0] >= x-10 and j.position[0] <= x+10:
    #                    if j.position[1] >= y-10 and j.position[1] <= y+10:
    #                        if j not in self.players[self.playerId].selectedObjects and self.players[self.playerId].inViewRange(j.position):
    #                            toGather.append(u)
    #                        else:
    #                            toMove.append(u)
    #             for j in i.asteroids:
    #                if j.position[0] >= x-10 and j.position[0] <= x+10:
    #                    if j.position[1] >= y-10 and j.position[1] <= y+10:
    #                        if j not in self.players[self.playerId].selectedObjects and self.players[self.playerId].inViewRange(j.position):
    #                            toGather.append(u)
    #                        else:
    #                            toMove.append(u)
    #        else:
    #            toMove.append(u)
    #
    #    self.setMovingFlag(x,y,toMove)
    #    self.setAttackFlag(x,y,toAttack)
    #    self.setLandingFlag(x,y,toLand)
    #    self.setGatherFlag(x,y,toGather)
    #===========================================================================
    def rightClic(self, pos):
        empty = True
        if self.players[self.playerId].currentPlanet == None:
            for i in self.galaxy.solarSystemList:
                for j in i.planets:
                    if pos[0] > j.position[0]-8 and pos[0] < j.position[0]+8:
                        if pos[1] > j.position[1]-8 and pos[1] < j.position[1]+8:
                            if len(self.players[self.playerId].selectedObjects) > 0:
                                if self.players[self.playerId].selectedObjects[0].name == 'Transport':
                                    self.setLandingFlag(self.players[self.playerId].selectedObjects[0], j)
                                    empty = False
            if empty:
                if len(self.players[self.playerId].selectedObjects) > 0:
                    if isinstance(self.players[self.playerId].selectedObjects[0], u.SpaceAttackUnit):
                        for i in self.players:
                            if i != self.players[self.playerId]:
                                for j in i.units:
                                    if j.isAlive:
                                        if j.position[0] >= pos[0]-8 and j.position[0] <= pos[0]+8:
                                            if j.position[1] >= pos[1]-8 and j.position[1] <= pos[1]+8: 
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
                if i.position[0] >= realStart[0]-8 and i.position[0] <= realEnd[0]+8:
                    if i.position[1] >= realStart[1]-8 and i.position[1] <= realEnd[1]+8:
                        if first:
                            self.players[self.playerId].selectedObjects = []
                            first = False
                        if isinstance(i, u.Mothership) == False:
                            if i.name == 'Transport':
                                if not i.landed:
                                    self.players[self.playerId].selectedObjects.append(i)
                            else:
                                self.players[self.playerId].selectedObjects.append(i)
        self.view.actionMenuType = MenuType.MAIN
        
    #Deplacement rapide de la camera vers un endroit de la minimap
    def quickMove(self, x,y, canva):
        if self.players[self.playerId].currentPlanet == None:
            posSelected = self.players[self.playerId].camera.calcPointOnMap(x,y)
            self.players[self.playerId].camera.position = posSelected
        
    #Envoyer le message pour le chat
    def sendMessage(self, mess):
        if mess != "":
            self.server.addMessage(mess, self.players[self.playerId].name)
        if mess == "t" or "c":
            self.pushChange(mess, "changeFormation")

    #Pour aller chercher les nouveaux messages
    def refreshMessages(self):
        textChat=''
        for i in range(len(self.mess), len(self.server.getMessage())):
            self.mess.append(self.server.getMessage()[i])
        if len(self.mess) > 5:
            for i in range(len(self.mess)-5, len(self.mess)):
                textChat+=self.mess[i]+'\r'
        else:
            for i in range(0, len(self.mess)):
                textChat+=self.mess[i]+'\r'
        self.view.chat.config(text=textChat)
        
    #TIMER D'ACTION DU JOUEUR COURANT
    def action(self, waitTime=50):
        if self.server.isGameStopped() == True and self.view.currentFrame == self.view.gameFrame:
            if self.playerId != 0:
                self.view.showGameIsFinished()
                self.view.root.destroy()
        elif self.view.currentFrame != self.view.pLobby:
            if self.refresh==0:
                self.refreshMessages()
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
	                        elif i.flag.flagState == FlagState.LAND:
	                            i.land(self, self.players.index(p))
	                print(p.motherShip.flag.flagState)
	                if p.motherShip.flag.flagState == FlagState.CREATE:
                            print('allo?')
                            p.motherShip.progressUnitsConstruction()
                            if p.motherShip.isUnitFinished():
                                u = p.motherShip.unitBeingConstruct.pop(0)
                                u.changeFlag(p.motherShip.flag.finalTarget, FlagState.MOVE)
                                p.units.append(u)
	            self.refreshMessages()
	            self.refresh+=1
	            self.view.showMinerals.config(text=self.players[self.playerId].mineral)
	            self.view.showGaz.config(text=self.players[self.playerId].gaz)
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
            if self.server.isGameStarted() == True:
                self.startGame()
            else:
                waitTime=1000
                self.view.pLobby = self.view.fLobby()
                self.view.changeFrame(self.view.pLobby)

        self.view.root.after(waitTime, self.action)
        
    def killUnit(self, killedIndexes):
        #Désélection de l'unité qui va mourir afin d'éviter le renvoie d'une actio avec cette unité
        if killedIndexes[1] == self.playerId:
            if self.players[self.playerId].units[killedIndexes[0]] in self.players[self.playerId].selectedObjects:
               self.players[self.playerId].selectedObjects.remove(self.players[self.playerId].units[killedIndexes[0]])
        self.players[killedIndexes[1]].units[killedIndexes[0]].kill()
#        #On va chercher les derniers changement sur le serveur afin de s'assurer de tous les changer
#        for i in self.server.getChange(self.playerId, self.refresh):
#            self.changes.append(i)       
#        toRemove = []
#        for i in self.changes:
#            if int(i.split("/")[0]) == killedIndexes[1] and int(i.split("/")[1] == killedIndexes[0]):
#                toRemove.append(i)
#            elif int(i.split("/")[0]) == killedIndexes[1]:
#                tempI = i.split("/")[1]
#                tempUnits = tempI.split(",")
#                tempI = ""
#                tempUnits.pop(len(tempUnits)-1)
#                for u in tempUnits:
#                    if  int(u) > killedIndexes[0]:
#                        u = str(int(u) -1)
#                    tempI += str(u) + ","
#                tempChange = i.split("/")
#                tempChange[1] = tempI
#                i = ""
#                for tc in tempChange:
#                    i += tc + "/"
#        for tr in toRemove:
#            self.changes.remove(tr)
#        self.players[killedIndexes[1]].units.pop(killedIndexes[0])
                
	#Connection au serveur			
    def connectServer(self, login, serverIP):
        self.server=Pyro4.core.Proxy("PYRO:controleurServeur@"+serverIP+":54440")
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
            self.players.append(p.Player(self.server.getSockets()[i][1], i))
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
            print(flag.flagState)
            if flag.flagState == FlagState.MOVE or flag.flagState == FlagState.STANDBY:
                actionString = str(self.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(flag.finalTarget.position)
            elif flag.flagState == FlagState.ATTACK:
                targetId = self.players[flag.finalTarget.owner].units.index(flag.finalTarget)
                actionString = str(self.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/U"+str(targetId)+"P"+str(flag.finalTarget.owner)
            elif flag.flagState == FlagState.CREATE:
                actionString = str(self.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState) + "/" + str(flag.finalTarget)
            elif flag.flagState == FlagState.CHANGE_RALLY_POINT:
                actionString = str(self.playerId) + "/" + "0" + "/" + str(flag.flagState) + "/" + str(flag.finalTarget)
                
        elif isinstance(flag, str):
            if flag == 'changeFormation':
                actionString = str(self.playerId)+"/"+playerObject+"/"+flag+"/changementDeFormation"
		#Si c'est un échange
        elif isinstance(flag, tuple):
            if flag[2] == FlagState.LAND:
                actionString = str(self.playerId)+"/"+playerObject+"/"+str(flag[2])+"/"+str(flag[0])+","+str(flag[1])
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
        if action == str(FlagState.MOVE) or action == str(FlagState.STANDBY):
            lineTaken=[]
            line=0
            target = target.strip("[")
            target = target.strip("]")
            target = target.split(",")
            for i in range(0, len(target)):
                target[i]=math.trunc(float(target[i])) #nécessaire afin de s'assurer que les positions sont des entiers
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
                                target[1]=targetorig[1]-(line*20)
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
                                        xLineBefore[p] = target[0]
                                    else:
                                        target[0]=xLineBefore[p]-20
                                        xLineBefore[p] = target[0]
                                target[1]=targetorig[1]-(line*20)
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
        elif action == str(FlagState.ATTACK):
            target = target.split("P")
            target[0] = target[0].strip("U")
            for i in unitIndex:
                if i != '':
                    self.players[actionPlayerId].units[int(i)].changeFlag(self.players[int(target[1])].units[int(target[0])], int(action))
        elif action == str(FlagState.LAND):
            target = target.split(',')
            self.players[actionPlayerId].units[int(unitIndex[0])].changeFlag(self.galaxy.solarSystemList[int(target[0])].planets[int(target[1])],int(action))
            #self.players[actionPlayerId].units[unitIndex[0]].flag = Flag(self.players[actionPlayerId].units[unitIndex[0]], planet, FlagState.LAND)
        #ici, le target sera l'index de l'unit� dans le tableau de unit du player cibl�
        
        elif action == str(FlagState.CREATE):
            print("va commencer a créer")
            self.players[actionPlayerId].motherShip.changeFlag(self.players[actionPlayerId].motherShip.flag.finalTarget,int(action), actionPlayerId, target)
        
        elif action == str(FlagState.CHANGE_RALLY_POINT):
            target = target.strip("[")
            target = target.strip("]")
            target = target.split(",")
            for i in range(0, len(target)):
                target[i]=math.trunc(float(target[i]))
            self.players[actionPlayerId].motherShip.flag.finalTarget.position = target
             
        elif action == 'deleteAllUnits':
            self.players[actionPlayerId].units = []
        
                            
            
        elif action == 'deleteUnit':
            self.killUnit((int(unitIndex[0]),actionPlayerId))
        elif action == 'changeFormation':
            if unitIndex[0]=='t':
                self.players[actionPlayerId].formation="triangle"
            elif unitIndex[0]=='c':
                self.players[actionPlayerId].formation="carre"
        elif unitIndex == 'g' or unitIndex == 'm':
            if unitIndex == 'm':
                self.players[actionPlayerId].mineral-=quantite
                self.players[int(action)].mineral+=quantite
            elif unitIndex == 'g':
                self.players[actionPlayerId].gaz-=quantite
                self.players[int(action)].gaz+=quantite

if __name__ == '__main__':
    c = Controller()
