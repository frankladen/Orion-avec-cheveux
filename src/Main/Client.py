# -*- coding: UTF-8 -*-
import View as v
import World as w
import Player as p
import Target as t
import Unit as u
import Game as g
from Helper import *
from Flag import *
import Pyro4
import socket
import math
import subprocess
import time

class Controller():
    def __init__(self):
        self.refresh = 0 #Compteur principal
        self.mess = []
        self.playerIp = socket.gethostbyname(socket.getfqdn())
        self.server = None
        self.isStarted=False
        self.currentFrame = None 
        self.attenteEcrit = False
        self.game = g.Game(self)
        self.view = v.View(self, self.game)
        self.view.root.mainloop()

    #TIMER D'ACTION DU JOUEUR COURANT
    def action(self, waitTime=50):
        if self.view.currentFrame != self.view.pLobby:
            if self.server.isGameStopped() == False:
                if self.refresh > 0:
                    if self.game.action():
                        self.refreshMessages(self.view.menuModes.chat)
                        #À chaque itération je demande les nouvelles infos au serveur
                        self.pullChange()
                        self.view.refreshGame(self.game.isOnPlanet())
                        self.refresh+=1
                        waitTime = self.server.amITooHigh(self.game.playerId)
                    elif self.game.playerId != 0:
                        self.view.deleteAll()
                else:
                    self.checkIfGameStarting()
        else:
            if self.server.isGameStarted() == True:
                self.startGame()
            else:
                waitTime=1000
                self.refreshMessages(self.view.chatLobby)
                self.view.redrawLobby(self.view.pLobby)
        self.view.root.after(waitTime, self.action)

    def checkIfGameStarting(self):
        response = self.server.isEveryoneReady(self.game.playerId)
        if response:
            self.refresh+=1
            if self.game.playerId == 0:
                self.sendMessage("La partie va maintenant débuter.")
        else:
            if self.game.playerId == 0 and self.attenteEcrit == False:
                self.attenteEcrit=True
                self.sendMessage("Attente des autres joueurs.")
    
    #Envoyer le message pour le chat
    def sendMessage(self, mess):
        if len(self.game.players) == 1:
            if mess == "forcegaz":
                self.game.players[self.game.playerId].ressources[p.Player.GAS] += 5000
            elif mess == "forcemine":
                self.game.players[self.game.playerId].ressources[p.Player.MINERAL] += 5000
        elif mess.find("\\t ") == 0:
            mess = mess.split("\\t ")
            mess = "(Alliés) "+mess[1]
            self.server.addMessage(mess, self.game.players[self.game.playerId].name, self.game.playerId, True)                                     
        elif len(mess)>0:
            mess = mess.replace('\\','/')
            self.server.addMessage(mess, self.game.players[self.game.playerId].name, self.game.playerId, False)

    def sendMessageLobby(self, mess, nom):
        mess = mess.replace('\\','/')
        self.server.addMessage(mess, self.server.getSockets()[self.game.playerId][1], self.game.playerId, False)

    #Pour aller chercher les nouveaux messages
    def refreshMessages(self, chat):
        if self.refresh % 10 == 0:
            textChat=''
            self.mess = []
            for i in range(len(self.mess), len(self.server.getMessage())):
                if self.server.getMessage()[i][2] == True:
                    if self.game.players[self.game.playerId].isAlly(self.server.getMessage()[i][0]):
                        self.mess.append(self.server.getMessage()[i][1])
                else:
                    self.mess.append(self.server.getMessage()[i][1])
            if len(self.mess) > 5:
                for i in range(len(self.mess)-5, len(self.mess)):
                    textChat+=self.mess[i]+'\r'
            else:
                for i in range(0, len(self.mess)):
                    textChat+=self.mess[i]+'\r'
            chat.config(text=textChat)

    def choiceColor(self, name ,index, mode):
        response = self.server.isThisColorChosen(self.view.variableColor.get(),self.game.playerId)
        if response == True:
            self.view.colorAlreadyChosen()

    def startServer(self, serverAddress, connect, userName):
        #Démarre le serveur dans un autre processus avec l'adresse spécifiée
        child = subprocess.Popen("C:\python32\python.exe server.py " + serverAddress, shell=True)
        #On doit attendre un peu afin de laisser le temps au serveur de partir et de se terminer si une erreur arrive
        time.sleep(1)
        #On vérifie si le serveur s'est terminé en erreur et si oui, on affiche un message à l'utilisateur
        if child.poll():
            if child.returncode != None:
                self.view.serverNotCreated()
            else:
                print("Shnitzel pas managé lors de la création du serveur")
        else:
            #self.serverCreated(serverAddress)
            #Si l'usager veut se connecter en créant le serveur, on le fait
            if connect:
                self.connectServer(userName, serverAddress)
            else:
                self.view.changeFrame(self.view.mainMenu)
       
	#Connection au serveur			
    def connectServer(self, login, serverIP):
        self.server=Pyro4.core.Proxy("PYRO:ServeurOrion@"+serverIP+":54400")
        #Je demande au serveur si la partie est démarrée, si oui on le refuse de la partie, cela permet de vérifier
        #en même temps si le serveur existe réellement à cette adresse.
        if self.server.isGameStarted() == True:
            self.view.gameHasBeenStarted()
            self.view.changeFrame(self.view.mainMenu)
        else:
            #Je fais chercher auprès du serveur l'ID de ce client et par le fais même, le serveur prend connaissance de mon existence
            self.game.playerId=self.server.getNumSocket(login, self.playerIp)
            if self.game.playerId != -1:
                #Je vais au lobby, si la connection a fonctionner
                self.view.pLobby = self.view.fLobby()
                self.view.changeFrame(self.view.pLobby)
                self.action()
            else:
                self.view.showNameAlreadyChosen()
                self.view.changeFrame(self.view.joinGame)
        
    #Demmare la partie et genere la galaxie (Quand l'admin appui sur start game dans le lobby)    
    def startGame(self):
        if self.game.playerId==0:
            self.server.startGame()
        players = []
        for i in range(0, len(self.server.getSockets())):
            if self.server.getSockets()[i][3] == -1:
                self.server.firstColorNotChosen(i)
            players.append(p.Player(self.server.getSockets()[i][1], self.game, i, self.server.getSockets()[i][3]))
        self.game.start(players, self.server.getSeed(), self.view.taille)
        self.view.gameFrame = self.view.fGame()
        self.view.changeFrame(self.view.gameFrame)
        self.view.root.after(50, self.action)

    def drawWorld(self):
        self.view.drawWorld()

    def redrawMinimap(self):
        self.view.redrawMinimap()

    def changeBackground(self, newBg):
        self.view.changeBackground(newBg)
    
    def drawPlanetGround(self, planet):
        self.view.drawPlanetGround(planet)

    def changeActionMenuType(self, newMenuType):
        self.view.actionMenuType = newMenuType

    def changeAlliance(self, player, newStatus):
        self.pushChange(player, Flag(finalTarget = newStatus, flagState = FlagState.DEMAND_ALLIANCE))
    
    #Méthode de mise à jour auprès du serveur, actionnée à chaque
    def pushChange(self, playerObject, flag):
        actionString = ""
        if isinstance(flag, Flag):
            if flag.flagState in (FlagState.MOVE, FlagState.STANDBY):
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(flag.finalTarget.position)
            elif flag.flagState == FlagState.GROUND_MOVE:
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(flag.finalTarget.position)
            elif flag.flagState == FlagState.ATTACK:
                if isinstance(flag.finalTarget, u.Unit):
                    targetId = self.game.players[flag.finalTarget.owner].units.index(flag.finalTarget)
                    type = "u"
                else:
                    type = "b"
                    targetId = self.game.players[flag.finalTarget.owner].buildings.index(flag.finalTarget)
                if isinstance(flag.initialTarget, int):
                    actionString = str(flag.initialTarget)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(targetId)+","+str(flag.finalTarget.owner)+","+type
                else:
                    actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(targetId)+","+str(flag.finalTarget.owner)+","+type
            elif flag.flagState == FlagState.FINISH_BUILD:
                buildingId = self.game.players[flag.finalTarget.owner].buildings.index(flag.finalTarget)
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(buildingId)   
            elif flag.flagState == FlagState.BUILD:
                for i in flag.initialTarget:
                    flag.finalTarget.position.append(i)
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(flag.finalTarget.position)
            elif flag.flagState == FlagState.CREATE:
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState) + "/" + str(flag.finalTarget)
            elif flag.flagState == FlagState.CHANGE_RALLY_POINT:
                actionString = str(self.game.playerId) + "/" + "0" + "/" + str(flag.flagState) + "/" + str(flag.finalTarget)
            elif flag.flagState == FlagState.NOTIFICATION:
                actionString = str(self.game.playerId) + "/" + str(playerObject) + "/" + str(flag.flagState) + "/" + str(flag.finalTarget)
            elif flag.flagState == FlagState.DESTROY:
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/0"
            elif flag.flagState == FlagState.CANCEL_UNIT:
                actionString = str(self.game.playerId) + "/" + str(playerObject) + "/" + str(flag.flagState) + "/" + str(flag.finalTarget)
            elif flag.flagState == FlagState.PATROL:
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(flag.finalTarget.position)
            elif flag.flagState == FlagState.CHANGE_FORMATION:
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(flag.finalTarget)
            elif flag.flagState == FlagState.DESTROY_ALL:
                actionString = str(playerObject)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(flag.finalTarget)
            elif flag.flagState == FlagState.TRADE:
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/["+str(flag.initialTarget)+","+str(flag.finalTarget)+"]"
            elif flag.flagState == FlagState.DEMAND_ALLIANCE:
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(flag.finalTarget)
            elif flag.flagState == FlagState.BUY_TECH:
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(flag.initialTarget)
            elif flag.flagState == FlagState.LOAD:
                planetId = flag.finalTarget.planetId
                solarId = flag.finalTarget.sunId
                zoneId = flag.finalTarget.id
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(zoneId)+","+str(planetId)+","+str(solarId)
            elif flag.flagState == FlagState.GATHER:
                if isinstance(flag.finalTarget, w.AstronomicalObject):
                    if flag.finalTarget.type == 'nebula':
                        astroId = flag.finalTarget.id
                        solarId = flag.finalTarget.solarSystem.sunId
                        type = w.AstronomicalObject.NEBULA
                    elif flag.finalTarget.type == 'asteroid':
                        astroId = flag.finalTarget.id
                        solarId = flag.finalTarget.solarSystem.sunId
                        type = w.AstronomicalObject.ASTEROID
                    actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(astroId)+","+str(solarId)+","+str(type)
                else:
                    actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(self.game.players[self.game.playerId].buildings.index(flag.finalTarget))+",0," + str(flag.finalTarget.type)
            elif flag.flagState == FlagState.GROUND_GATHER:
                sunId = flag.finalTarget.sunId
                planetId = flag.finalTarget.planetId
                ressourceId = flag.finalTarget.id
                if isinstance(flag.finalTarget, w.MineralStack):
                    actionString = str(self.game.playerId) + "/" + str(playerObject) + "/" + str(flag.flagState) + "/" + str(ressourceId) + "," + str(planetId) + "," + str(sunId) + "," + str(w.Planet.MINERAL)
                elif isinstance(flag.finalTarget, w.GazStack):
                    actionString = str(self.game.playerId) + "/" + str(playerObject) + "/" + str(flag.flagState) + "/" + str(ressourceId) + "," + str(planetId) + "," + str(sunId) + "," + str(w.Planet.GAZ)
                else:
                    actionString = str(self.game.playerId) + "/" + str(playerObject) + "/" + str(flag.flagState) + "/" + str(ressourceId) + "," + str(planetId) + "," + str(sunId) + "," + str(w.Planet.LANDINGZONE)
        elif isinstance(flag, tuple):
            if flag[2] == FlagState.LAND:
                actionString = str(self.game.playerId)+"/"+playerObject+"/"+str(flag[2])+"/"+str(flag[0])+","+str(flag[1])
            elif flag[2] == 'TAKEOFF':
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag[2])+"/"+str(flag[0])+","+str(flag[1])
            else:
                actionString = str(self.game.playerId)+"/"+playerObject+"/"+flag[0]+"/"+flag[1]
        elif isinstance(flag, str):
            if flag == 'UNLOAD':
                actionString = str(self.game.playerId)+"/"+str(playerObject.id)+"/"+flag+"/"+str(playerObject.planetId)+","+str(playerObject.sunId)
        self.server.addChange(actionString)
    
    def pullChange(self):
        toRemove = []
        for i in self.server.getChange(self.game.playerId, self.refresh):
            self.game.changes.append(i)
        for changeString in self.game.changes:
            if int(changeString.split("/")[4]) == self.refresh:
                self.doAction(changeString)
                toRemove.append(changeString)
        for tR in toRemove:
            self.game.changes.remove(tR)

    def stripAndSplit(self, toStripAndSplit):
        toStripAndSplit = toStripAndSplit.strip("[")
        toStripAndSplit = toStripAndSplit.strip("]")
        toStripAndSplit = toStripAndSplit.split(",")
        return toStripAndSplit

    def changeToInt(self, toChange):
        for i in range(0, len(toChange)):
            toChange[i]=math.trunc(float(toChange[i])) #nécessaire afin de s'assurer que les positions sont des entiers
        return toChange
    
    def doAction(self, changeString):
        changeInfo = changeString.split("/")
        actionPlayerId = int(changeInfo[0])
        unitIndex = changeInfo[1]
        unitIndex = unitIndex.split(",")
        action = changeInfo[2]
        target = changeInfo[3]
        refresh = int(changeInfo[4])
        #si l'action est Move, la target sera sous forme de tableau de positions [x,y,z]
        if action in (str(FlagState.MOVE), str(FlagState.STANDBY), str(FlagState.PATROL)):
            target = self.changeToInt(self.stripAndSplit(target))
            self.game.makeFormation(actionPlayerId, unitIndex, target, action)
            
        elif action == str(FlagState.GROUND_MOVE):
            target = self.changeToInt(self.stripAndSplit(target))
            for i in unitIndex:
                if i != '':
                    self.game.players[actionPlayerId].units[int(i)].changeFlag(t.Target([int(target[0]),int(target[1]),int(target[2])]),int(action))
            self.game.makeFormation(actionPlayerId, unitIndex, target, action)
        
        elif action == str(FlagState.FINISH_BUILD):
            self.game.resumeBuilding(actionPlayerId, int(target), unitIndex)
            
        elif action == str(FlagState.BUILD):
            target = self.changeToInt(self.stripAndSplit(target))
            if len(target) == 5:
                self.game.buildBuilding(actionPlayerId, target, int(action), unitIndex, int(target[3]))
            else:
                self.game.buildBuilding(actionPlayerId, target, int(action), unitIndex, int(target[3]), int(target[4]), int(target[5]))
                        
        elif action == str(FlagState.ATTACK):
            target = target.split(",")
            self.game.makeUnitsAttack(actionPlayerId, unitIndex, int(target[1]), int(target[0]), target[2])
                    
        elif action == str(FlagState.LAND):
            target = target.split(',')
            self.game.makeUnitLand(actionPlayerId, int(unitIndex[0]), int(target[0]), int(target[1]))
            
        elif action == 'TAKEOFF':
            target = target.split(',')
            unit = self.game.players[actionPlayerId].units[int(unitIndex[0])]
            planet = self.game.galaxy.solarSystemList[int(target[1])].planets[int(target[0])]
            self.game.takeOff(unit, planet, actionPlayerId)
            if actionPlayerId == self.game.playerId:
                cam = self.game.getCurrentCamera()
                cam.position = [unit.position[0], unit.position[1]]
                cam.placeOverPlanet()
                self.view.changeBackground('GALAXY')

        elif action == 'UNLOAD':
            target = target.split(',')
            self.game.makeZoneUnload(int(unitIndex[0]), actionPlayerId, int(target[0]), int(target[1]))

        elif action == str(FlagState.NOTIFICATION):
            target = self.changeToInt(self.stripAndSplit(target))
            self.game.makeNotification(actionPlayerId, target)

        elif action == str(FlagState.LOAD):
            target = target.split(',')
            self.game.loadUnit(unitIndex, int(target[1]), int(target[2]), actionPlayerId)
                
        elif action == str(FlagState.GATHER):
            target = target.split(',')
            self.game.makeUnitsGather(actionPlayerId, unitIndex, int(target[1]), int(target[0]), int(target[2]))

        elif action == str(FlagState.GROUND_GATHER):
            target = target.split(',')
            self.game.makeGroundUnitsGather(actionPlayerId, unitIndex, int(target[0]),int(target[1]),int(target[2]),int(target[3]))
        
        elif action == str(FlagState.CREATE):
            self.game.createUnit( actionPlayerId, int(unitIndex[0]), int(target))
        
        elif action == str(FlagState.CHANGE_RALLY_POINT):
            target = self.changeToInt(self.stripAndSplit(target))
            self.game.players[actionPlayerId].buildings[int(unitIndex[0])].changeFlag(target,int(action))
        
        elif action == str(FlagState.CANCEL_UNIT):
            self.game.cancelUnit(actionPlayerId, int(target), int(unitIndex[0]))

        elif action == str(FlagState.DESTROY):
            self.game.killUnit((int(unitIndex[0]),actionPlayerId,False))
        
        elif action == str(FlagState.DESTROY_ALL):
            self.game.killPlayer(actionPlayerId)
        
        elif action == str(FlagState.CHANGE_FORMATION):
            self.game.changeFormation(actionPlayerId, target, unitIndex, FlagState.MOVE)

        elif action == str(FlagState.BUY_TECH):
            self.game.buyTech(actionPlayerId, target, int(unitIndex[0]))

        elif action == str(FlagState.TRADE):
            target = self.stripAndSplit(target)
            self.game.tradeActions(actionPlayerId, target, unitIndex)
                
        elif action == str(FlagState.DEMAND_ALLIANCE):
            #actionPlayerId = le joueur qui change le status
            #unitIndex[0] = le joueur concerné par le changement
            #target = le nouveau status de l'alliance entre les deux
            self.game.demandAlliance(actionPlayerId, int(unitIndex[0]), target)
            self.view.refreshAlliances()


    def endGame(self):
        self.view.showGameIsFinished()
        self.view.root.destroy()

    def sendKillPlayer(self):
        if self.server:
            playerId = self.game.playerId
            self.pushChange(playerId, Flag(playerId,playerId,FlagState.DESTROY_ALL))
        else:
            self.view.root.destroy()

    #Enleve le joueur courant de la partie ainsi que ses units
    def removePlayer(self):
        if self.view.currentFrame == self.view.gameFrame:
            self.view.selectedOnglet = self.view.SELECTED_CHAT
            self.sendMessage('a quitté la partie')
            self.server.removePlayer(self.game.players[self.game.playerId].name, self.game.playerId)
            
if __name__ == '__main__':
    c = Controller()
