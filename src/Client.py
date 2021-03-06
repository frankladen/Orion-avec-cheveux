# -*- coding: UTF-8 -*-
import View as v
import World as w
import Player as p
import Target as t
import Building as b
import Unit as u
import Game as g
import IA as ia
from IA import *
from Helper import *
from Flag import *
import os
import sys
import Pyro4
import socket
import math
import subprocess
import time

class Controller():
    def __init__(self):
        self.nIA = 0 #compteurIA
        self.refresh = 0 #Compteur principal
        self.players = []
        self.computers = []
        self.waitTime=50
        self.died = False
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
    def action(self):
        if self.view.currentFrame != self.view.pLobby:
            if self.server.isGameStopped() == False:
                if self.refresh > 0:
                    if self.game.action(): 
                        if self.refresh % 20 == 0:
                            self.refreshMessages(self.view.menuModes.chat)
                        #À chaque itération je demande les nouvelles infos au serveur
                        self.pullChange()
                        if not self.died:
                            self.view.refreshGame(self.game.isOnPlanet())
                            self.refresh+=1
                            self.waitTime = self.server.amITooHigh(self.game.playerId)
                    elif self.game.playerId != 0:
                        self.view.deleteAll()
                else:
                    self.checkIfGameStarting()
        else:
            if self.server.isGameStarted() == True:
                self.startGame()
            else:
                self.waitTime=1000
                self.refreshMessages(self.view.chatLobby)
                self.view.redrawLobby(self.view.pLobby)
        if not self.died:
            self.view.root.after(self.waitTime, self.action)

    def checkIfGameStarting(self):
        response = self.server.isEveryoneReady(self.game.playerId)
        if response:
            self.refresh+=1
            self.waitTime = 50
            if self.game.playerId == 0:
                self.sendMessage("La partie va maintenant débuter.")
        else:
            if self.game.playerId == 0 and self.attenteEcrit == False:
                self.attenteEcrit=True
                self.sendMessage("Attente des autres joueurs.")
    
    #Envoyer le message pour le chat
    def sendMessage(self, mess):
        if mess == "forcegaz":
            self.pushChange(0,Flag(None,"forcegaz",FlagState.CHEAT))
        elif mess == "forcemine":
            self.pushChange(0,Flag(None,"forcemine",FlagState.CHEAT))
        elif mess == "forcenuke":
            self.pushChange(0,Flag(None,"forcenuke",FlagState.CHEAT))
        elif mess == "forcepop":
            self.pushChange(0,Flag(None,"forcepop",FlagState.CHEAT))
        elif mess == "forcebuild":
            self.pushChange(0,Flag(None,"forcebuild",FlagState.CHEAT))
        elif mess == "doabarrelroll":
            self.pushChange(0,Flag(None,"doabarrelroll",FlagState.CHEAT))
        elif mess == "allyourbasesbelongtous":
            self.pushChange(0,Flag(None,"allyourbasesbelongtous",FlagState.CHEAT))
        elif mess.find("\\t ") == 0:
            mess = mess.split("\\t ")
            mess = "(Alliés) "+mess[1]
            self.server.addMessage(mess, self.game.players[self.game.playerId].name, self.game.playerId, True)
            self.pushChange(mess, Flag(None,[self.game.playerId,t.Notification.MESSAGE_ALLIES,0],FlagState.NOTIFICATION))
        elif len(mess)>0:
            mess = mess.replace('\\','/')
            self.server.addMessage(mess, self.game.players[self.game.playerId].name, self.game.playerId, False)
            self.pushChange(mess, Flag(None,[self.game.playerId,t.Notification.MESSAGE_ALL,0],FlagState.NOTIFICATION))

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
        paths = sys.path
        temp = None
        for i in paths:
            if i.find("\\lib\\") != -1:
                temp = i.split("\\lib\\")[0]
                break
        if temp != None:
            temp += "\\python.exe"
        else:
            temp= "C:\python32\python.exe"
        #Démarre le serveur dans un autre processus avec l'adresse spécifiée
        child = subprocess.Popen(temp + " server.py " + serverAddress, shell=True)
        #On doit attendre un peu afin de laisser le temps au serveur de partir et de se terminer si une erreur arrive
        time.sleep(1)
        #On vérifie si le serveur s'est terminé en erreur et si oui, on affiche un message à l'utilisateur
        if child.poll():
            if child.returncode != None:
                self.view.serverNotCreated()
            else:
                print("Shnitzel pas managé lors de la création du serveur")
        else:
            #Si l'usager veut se connecter en créant le serveur, on le fait
            if connect:
                self.connectServer(userName, serverAddress)
            else:
                self.view.changeFrame(self.view.mainMenu)
       
	#Connection au serveur			
    def connectServer(self, login, ns):
        self.server=Pyro4.core.Proxy("PYRO:ServeurOrion@"+ns+":54400")
        #Je demande au serveur si la partie est démarrée, si oui on le refuse de la partie, cela permet de vérifier
        #en même temps si le serveur existe réellement à cette adresse.
        if self.server.isGameStarted() == True:
            self.view.gameHasBeenStarted()
            self.view.changeFrame(self.view.mainMenu)
        else:
            #Je fais chercher auprès du serveur l'ID de ce client et par le fais même, le serveur prend connaissance de mon existence
            self.game.playerId=self.server.getNumSocket(login, self.playerIp, False)
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
        for i in range(0, len(self.server.getSockets())):
            if self.server.getSockets()[i][3] == -1:
                self.server.firstColorNotChosen(i)
            if not self.server.getSockets()[i][4]:
                self.players.append(p.Player(self.server.getSockets()[i][1], self.game, i, self.server.getSockets()[i][3]))
            else:
                self.players.append(ia.IA(self.server.getSockets()[i][1], self.game, i, self.server.getSockets()[i][3]))
                self.server.isEveryoneReady(len(self.players)-1)
        self.game.start(self.players, self.server.getSeed(), self.view.WIDTH, self.view.HEIGHT)
        self.view.gameFrame = self.view.fGame()
        self.view.changeFrame(self.view.gameFrame)
        self.view.root.after(50, self.action)
        
    def ajouterIA(self):
        self.nIA += 1
        self.server.getNumSocket("IA"+str(self.nIA), self.playerIp, True)
        
    def drawWorld(self):
        self.view.drawWorld()

    def redrawMinimap(self):
        self.view.redrawMinimap()

    def goToWinFrame(self, scores):
        self.view.scores = self.view.fScore(scores)
        self.view.changeFrame(self.view.scores)

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
            elif flag.flagState == FlagState.HEAL:
                actionString = str(self.game.playerId) + "/" + str(playerObject) + "/" + str(flag.flagState) + "/" + str(flag.finalTarget.position)
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
            elif flag.flagState in (FlagState.CREATE, FlagState.CHANGE_RALLY_POINT, FlagState.NOTIFICATION, FlagState.ATTACK_BUILDING, FlagState.LINK_WAYPOINTS, FlagState.CANCEL_UNIT, FlagState.CANCEL_TECH, FlagState.CHEAT, FlagState.CHANGE_FORMATION, FlagState.DESTROY_ALL, FlagState.DEMAND_ALLIANCE):
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState) + "/" + str(flag.finalTarget)
            elif flag.flagState == FlagState.DESTROY:
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/0"
            elif flag.flagState == FlagState.PATROL:
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(flag.finalTarget.position)
            elif flag.flagState == FlagState.TRADE:
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/["+str(flag.initialTarget)+","+str(flag.finalTarget)+"]"
            elif flag.flagState == FlagState.BUY_TECH:
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(flag.finalTarget.position)
            elif flag.flagState == FlagState.WORMHOLE:
                wormholeId = self.game.galaxy.wormholes.index(flag.finalTarget)
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(wormholeId)
            elif flag.flagState == FlagState.LOAD:
                planetId = flag.finalTarget.planetId
                solarId = flag.finalTarget.sunId
                zoneId = flag.finalTarget.id
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(zoneId)+","+str(planetId)+","+str(solarId)
            elif flag.flagState == FlagState.GATHER:
                if isinstance(flag.finalTarget, w.AstronomicalObject):
                    astroId = flag.finalTarget.id
                    solarId = flag.finalTarget.solarSystem.sunId
                    actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(astroId)+","+str(solarId)+","+str(flag.finalTarget.type)
                else:
                    actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(self.game.players[self.game.playerId].buildings.index(flag.finalTarget))+",0," + str(flag.finalTarget.type)
            elif flag.flagState == FlagState.GROUND_GATHER:
                sunId = flag.finalTarget.sunId
                planetId = flag.finalTarget.planetId
                ressourceId = 0
                if isinstance(flag.finalTarget, w.NuclearSite) == False and isinstance(flag.finalTarget, b.Farm) == False:
                    ressourceId = flag.finalTarget.id
                if isinstance(flag.finalTarget, w.MineralStack):
                    actionString = str(self.game.playerId) + "/" + str(playerObject) + "/" + str(flag.flagState) + "/" + str(ressourceId) + "," + str(planetId) + "," + str(sunId) + "," + "mine"
                elif isinstance(flag.finalTarget, w.GazStack):
                    actionString = str(self.game.playerId) + "/" + str(playerObject) + "/" + str(flag.flagState) + "/" + str(ressourceId) + "," + str(planetId) + "," + str(sunId) + "," + "gaz"
                elif isinstance(flag.finalTarget, w.NuclearSite):
                    actionString = str(self.game.playerId) + "/" + str(playerObject) + "/" + str(flag.flagState) + "/" + str(ressourceId) + "," + str(planetId) + "," + str(sunId) + "," + "nuclear"
                elif isinstance(flag.finalTarget, b.LandingZone):
                    actionString = str(self.game.playerId) + "/" + str(playerObject) + "/" + str(flag.flagState) + "/" + str(ressourceId) + "," + str(planetId) + "," + str(sunId) + "," + "landing"
                elif isinstance(flag.finalTarget, b.Farm):
                    actionString = str(self.game.playerId) + "/" + str(playerObject) + "/" + str(flag.flagState) + "/" + str(ressourceId) + "," + str(planetId) + "," + str(self.game.getMyPlayer().buildings.index(flag.finalTarget)) + "," + "farm"
        elif isinstance(flag, tuple):
            if flag[2] == FlagState.LAND:
                actionString = str(self.game.playerId)+"/"+playerObject+"/"+str(flag[2])+"/"+str(flag[0])+","+str(flag[1])
            elif flag[2] == 'TAKEOFF':
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag[2])+"/"+str(flag[0])+","+str(flag[1])
            elif flag[2] == 'WORMHOLE':
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag[2])+"/"+str(flag[0][0])+","+str(flag[0][1])+","+str(flag[1][0])+","+str(flag[1][1])
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
            if int(changeString.split("/")[4]) <= self.refresh:
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
            #self.game.makeGroundUnitMove(actionPlayerId, unitIndex, int(target[0]), int(target[1]), int(target[2]), action)
            self.game.makeFormation(actionPlayerId, unitIndex, target, action)
            #for i in unitIndex:
                #if i != '':
                    #self.game.players[actionPlayerId].units[int(i)].changeFlag(t.Target([int(target[0]),int(target[1]),int(target[2])]),int(action))
        
        elif action == str(FlagState.FINISH_BUILD):
            self.game.resumeBuilding(actionPlayerId, int(target), unitIndex)
            
        elif action == str(FlagState.BUILD):
            target = self.changeToInt(self.stripAndSplit(target))
            if len(target) == 5:
                self.game.buildBuilding(actionPlayerId, target, int(action), unitIndex, int(target[3]))
            else:
                self.game.buildBuilding(actionPlayerId, target, int(action), unitIndex, int(target[3]), int(target[4]), int(target[5]))
                        
        elif action == str(FlagState.ATTACK_BUILDING):
            target = self.changeToInt(self.stripAndSplit(target))
            self.game.makeSpaceBuildingAttack(actionPlayerId, target, unitIndex)

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

        elif action == 'WORMHOLE':
            target = self.changeToInt(self.stripAndSplit(target))
            mothership = self.game.players[actionPlayerId].motherships[int(unitIndex[0])]
            self.game.makeWormHole(actionPlayerId, [target[0],target[1]], [target[2],target[3]], mothership)

        elif action == 'UNLOAD':
            target = target.split(',')
            self.game.makeZoneUnload(int(unitIndex[0]), actionPlayerId, int(target[0]), int(target[1]))

        elif action == str(FlagState.WORMHOLE):
            target = self.changeToInt(self.stripAndSplit(target))
            self.game.makeUnitGoToWormhole(unitIndex, actionPlayerId, target[0])

        elif action == str(FlagState.NOTIFICATION):
            target = self.changeToInt(self.stripAndSplit(target))
            self.game.makeNotification(actionPlayerId, target, unitIndex)

        elif action == str(FlagState.LOAD):
            target = target.split(',')
            self.game.loadUnit(unitIndex, int(target[1]), int(target[2]), actionPlayerId)
                
        elif action == str(FlagState.GATHER):
            target = target.split(',')
            self.game.makeUnitsGather(actionPlayerId, unitIndex, int(target[1]), int(target[0]), int(target[2]))

        elif action == str(FlagState.GROUND_GATHER):
            target = target.split(',')
            self.game.makeGroundUnitsGather(actionPlayerId, unitIndex, int(target[0]),int(target[1]),int(target[2]),target[3])
        
        elif action == str(FlagState.CREATE):
            self.game.createUnit( actionPlayerId, int(unitIndex[0]), int(target))

        elif action == str(FlagState.CHEAT):
            self.game.cheatPlayer(actionPlayerId, target)
        
        elif action == str(FlagState.CHANGE_RALLY_POINT):
            target = self.changeToInt(self.stripAndSplit(target))
            if int(unitIndex[0]) < len(self.game.players[actionPlayerId].buildings) and unitIndex[0] != None:
                self.game.players[actionPlayerId].buildings[int(unitIndex[0])].changeFlag(target,int(action))
        
        elif action == str(FlagState.CANCEL_UNIT):
            self.game.cancelUnit(actionPlayerId, int(target), int(unitIndex[0]))

        elif action == str(FlagState.CANCEL_TECH):
            self.game.cancelTech(actionPlayerId, int(target), int(unitIndex[0]))

        elif action == str(FlagState.DESTROY):
            self.game.killUnit((int(unitIndex[0]),actionPlayerId,False))
        
        elif action == str(FlagState.DESTROY_ALL):
            self.game.killPlayer(actionPlayerId)

        elif action == str(FlagState.LINK_WAYPOINTS):
            target = self.changeToInt(self.stripAndSplit(target))
            self.game.linkWaypoints(actionPlayerId, target[0], target[1], target[2])
        
        elif action == str(FlagState.CHANGE_FORMATION):
            self.game.changeFormation(actionPlayerId, int(target), unitIndex, FlagState.MOVE)

        elif action == str(FlagState.BUY_TECH):
            target = self.changeToInt(self.stripAndSplit(target))
            techType = ""
            for i in unitIndex:
                techType += i
            self.game.buyTech(actionPlayerId, techType, target[0], target[1])

        elif action == str(FlagState.TRADE):
            target = self.stripAndSplit(target)
            self.game.tradeActions(actionPlayerId, target, unitIndex)
                
        elif action == str(FlagState.DEMAND_ALLIANCE):
            #actionPlayerId = le joueur qui change le status
            #unitIndex[0] = le joueur concerné par le changement
            #target = le nouveau status de l'alliance entre les deux
            self.game.demandAlliance(actionPlayerId, int(unitIndex[0]), target)
            self.view.refreshAlliances()
            
        elif action == str(FlagState.HEAL):
            target = self.changeToInt(self.stripAndSplit(target))
            self.game.healUnitForReal(actionPlayerId, target, int(unitIndex[0]))


    def endGame(self):
        self.died = True
        self.view.showGameIsFinished()
        self.view.scores = self.view.fScore(scores)
        self.view.changeFrame(self.view.scores)

    def sendKillPlayer(self):
        if self.view.currentFrame == self.view.gameFrame:
            if self.server:
                playerId = self.game.playerId
                self.pushChange(playerId, Flag(playerId,playerId,FlagState.DESTROY_ALL))
            else:
                self.view.root.destroy()
        else:
            self.view.root.destroy()

    #Enleve le joueur courant de la partie ainsi que ses units
    def removePlayer(self):
        if self.view.currentFrame == self.view.gameFrame:
            self.died = True
            self.view.selectedOnglet = self.view.SELECTED_CHAT
            self.sendMessage('a quitté la partie')
            self.server.removePlayer(self.game.players[self.game.playerId].name, self.game.playerId)
            
if __name__ == '__main__':
    c = Controller()
