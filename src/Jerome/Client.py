# -*- coding: UTF-8 -*-
import View as v
import World as w
import Player as p
import Target as t
import Unit as u
import Game as g
from Helper import *
from Flag import *
from Constants import *
import Pyro4
import socket
import math
import subprocess
import time

class Controller():
    def __init__(self):
        #self.players = [] #La liste des joueurs
        #self.playerId = 0 #Le id du joueur courant
        self.refresh = 0 #Compteur principal
        self.mess = []
        #self.changes = []
        self.playerIp = socket.gethostbyname(socket.getfqdn())
        self.server = None
        self.isStarted=False
        #self.multiSelect = False
        self.currentFrame = None 
        self.attenteEcrit = False
        self.game = g.Game(self)
        self.view = v.View(self, self.game)
        self.view.root.mainloop()

    #TIMER D'ACTION DU JOUEUR COURANT
    def action(self, waitTime=50):
        #Si l'administrateur a quitté la partie, on l'indique au jouer et on quitte la partie
        if self.server.isGameStopped() == True and self.view.currentFrame == self.view.gameFrame:
            if self.game.playerId != 0:
                waitTime=99999999999999
                self.view.showAdminLeft()
                self.view.root.destroy()
        elif self.view.currentFrame != self.view.pLobby:
            self.refreshMessages(self.view.menuModes.chat)
            if self.refresh > 0:
                #À chaque itération je demande les nouvelles infos au serveur
                self.pullChange()
                self.game.action()
                self.view.refreshGame(self.game.isOnPlanet())
                self.refresh+=1
                waitTime = self.server.amITooHigh(self.game.playerId)
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
        if mess == "forcegaz":
            self.game.players[self.game.playerId].ressources[p.Player.GAS] += 500
        elif mess == "forcemine":
            self.game.players[self.game.playerId].ressources[p.Player.MINERAL] += 500
        elif len(mess)>0:
            mess = mess.replace('\\','/')
            self.server.addMessage(mess, self.game.players[self.game.playerId].name)

    def sendMessageLobby(self, mess, nom):
        mess = mess.replace('\\','/')
        self.server.addMessage(mess, self.server.getSockets()[self.game.playerId][1])

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
        time.sleep(3)
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
        #try:
            #Je demande au serveur si la partie est démarrée, si oui on le refuse de la partie, cela permet de vérifier
            #en même temps si le serveur existe réellement à cette adresse.
        if self.server.isGameStarted() == True:
            self.view.gameHasBeenStarted()
            self.view.changeFrame(self.view.mainMenu)
        else:
            #Je fais chercher auprès du serveur l'ID de ce client et par le fais même, le serveur prend connaissance de mon existence
            self.game.playerId=self.server.getNumSocket(login, self.playerIp)
            #Je vais au lobby, si la connection a fonctionner
            self.view.pLobby = self.view.fLobby()
            self.view.changeFrame(self.view.pLobby)
            self.action()
##        except:
##            self.view.loginFailed()
##            self.view.changeFrame(self.view.mainMenu)
        
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

    def setTradeFlag(self, item, playerId2, quantite):
        for i in items:
            self.pushChange(playerId2, Flag(i, quantite[items.index(i)], FlagState.TRADE))

    def askTrade(self, eve):
        idOtherPlayer = self.view.menuModes.tradeOPTIONS.index(self.view.menuModes.variableTrade.get())
        if self.game.players[self.game.playerId].name != self.view.menuModes.variableTrade.get() and self.game.players[idOtherPlayer].units != []:
            self.pushChange(idOtherPlayer, Flag(1, "askTrade", FlagState.TRADE))
            self.game.tradePage=1
            self.game.idTradeWith=idOtherPlayer
            self.view.ongletTradeWaiting()

    def startTrade(self, answer, id1):
        if answer == True:
            self.pushChange(id1, Flag(2, "startTrade", FlagState.TRADE))
        else:
            self.pushChange(id1, Flag(3, "deniedTrade", FlagState.TRADE))
            self.view.ongletTradeChoicePlayer()

    def confirmTradeQuestion(self, id2):
        self.pushChange(id2, Flag(4, self.view.menuModes.spinMinerals1.get()+','+self.view.menuModes.spinMinerals2.get()+','+self.view.menuModes.spinGaz1.get()+','+self.view.menuModes.spinGaz2.get(), FlagState.TRADE))
        self.game.tradePage=1
        self.view.ongletTradeWaiting()

    def confirmTrade(self, answer, id1, min1, min2, gaz1, gaz2):
        if answer == True:
            self.pushChange(sel.gamef.idTradeWith, Flag("m", min1, FlagState.TRADE))
            self.pushChange(self.playerId, Flag("m", min2+','+str(self.game.idTradeWith), FlagState.TRADE))
            self.pushChange(self.game.idTradeWith, Flag("g", gaz1, FlagState.TRADE))
            self.pushChange(self.playerId, Flag("g", gaz2+','+str(self.game.idTradeWith), FlagState.TRADE))
        else:
            self.pushChange(id1, Flag(3, "deniedTrade", FlagState.TRADE))
            self.game.tradePage=-1
            self.view.ongletTradeChoicePlayer()

    def changeAlliance(self, player, newStatus):
        self.pushChange(player, Flag(finalTarget = newStatus, flagState = FlagState.DEMAND_ALLIANCE))
    
    #Méthode de mise à jour auprès du serveur, actionnée à chaque
    def pushChange(self, playerObject, flag):
        actionString = ""
        if isinstance(flag, Flag):
            if flag.flagState == FlagState.MOVE or flag.flagState == FlagState.STANDBY:
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(flag.finalTarget.position)
            elif flag.flagState == FlagState.GROUND_MOVE:
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(flag.finalTarget.position)
            elif flag.flagState == FlagState.ATTACK:
                targetId = self.players[flag.finalTarget.owner].units.index(flag.finalTarget)
                if isinstance(flag.initialTarget, int):
                    actionString = str(flag.initialTarget)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/U"+str(targetId)+"P"+str(flag.finalTarget.owner)
                else:
                    actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/U"+str(targetId)+"P"+str(flag.finalTarget.owner)
            elif flag.flagState == FlagState.CREATE:
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState) + "/" + str(flag.finalTarget)
            elif flag.flagState == FlagState.CHANGE_RALLY_POINT:
                actionString = str(self.game.playerId) + "/" + "0" + "/" + str(flag.flagState) + "/" + str(flag.finalTarget)
            elif flag.flagState == FlagState.DESTROY:
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/0"
            elif flag.flagState == FlagState.CANCEL_UNIT:
                actionString = str(self.game.playerId) + "/" + "0" + "/" + str(flag.flagState) + "/" + str(flag.finalTarget)
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
            elif flag.flagState == FlagState.GATHER:
                if isinstance(flag.finalTarget, w.AstronomicalObject):
                    if flag.finalTarget.type == 'nebula':
                        nebulaId = flag.finalTarget.id
                        solarId = flag.finalTarget.solarSystem.sunId
                        actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(nebulaId)+","+str(solarId)+",0"
                    elif flag.finalTarget.type == 'asteroid':
                        mineralId = flag.finalTarget.id
                        solarId = flag.finalTarget.solarSystem.sunId
                        actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/"+str(mineralId)+","+str(solarId)+",1"
                else:
                    actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag.flagState)+"/retouraumothership,sansbriserlaactionstring,2"
            
        elif isinstance(flag, tuple):
            if flag[2] == FlagState.LAND:
                actionString = str(self.game.playerId)+"/"+playerObject+"/"+str(flag[2])+"/"+str(flag[0])+","+str(flag[1])
            elif flag[2] == 'TAKEOFF':
                actionString = str(self.game.playerId)+"/"+str(playerObject)+"/"+str(flag[2])+"/"+str(flag[0])+","+str(flag[1])
            else:
                actionString = str(self.game.playerId)+"/"+playerObject+"/"+flag[0]+"/"+flag[1]
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
            self.game.makeFormation(actionPlayerId, unitIndex, action)
            
        elif action == str(FlagState.GROUND_MOVE):
            target = target.strip("[")
            target = target.strip("]")
            target = target.split(",")
            for i in range(0, len(target)):
                target[i]=math.trunc(float(target[i])) #nécessaire afin de s'assurer que les positions sont des entiers
            for i in unitIndex:
                if i != '':
                    self.players[actionPlayerId].units[int(i)].changeFlag(t.Target([int(target[0]),int(target[1]),int(target[2])]),int(action))
                    
        elif action == str(FlagState.ATTACK):
            target = target.split("P")
            target[0] = target[0].strip("U")
            self.game.makeUnitsAttack(actionPlayerId, unitIndex, int(target[1]), int(target[0]))
                    
        elif action == str(FlagState.LAND):
            target = target.split(',')
            self.game.makeUnitLand(actionPlayerId, int(unitIndex[0]), int(target[0]), int(target[1]))
            
        elif action == 'TAKEOFF':
            target = target.split(',')
            unit = self.players[actionPlayerId].units[int(unitIndex[0])]
            planet = self.galaxy.solarSystemList[int(target[1])].planets[int(target[0])]
            self.takeOff(unit, planet, actionPlayerId)
            if actionPlayerId == self.game.playerId:
                cam = self.game.getCurrentCamera()
                cam.position = [unit.position[0], unit.position[1]]
                cam.placeOverPlanet()
                self.view.changeBackground('GALAXY')
                
        elif action == str(FlagState.GATHER):
            target = target.split(',')
            self.game.makeUnitsGather(actionPlayerId, unitIndex, int(target[1]), int(target[0]), int(target[2]))
        
        elif action == str(FlagState.CREATE):
            self.game.createUnit( actionPlayerId, int(target))
        
        elif action == str(FlagState.CHANGE_RALLY_POINT):
            self.game.players[actionPlayerId].motherShip.changeFlag(target,int(action))
        
        elif action == str(FlagState.CANCEL_UNIT):
            self.game.cancelUnit(actionPlayerId, int(target))

        elif action == str(FlagState.DESTROY):
            self.game.killUnit((int(unitIndex[0]),actionPlayerId))
        
        elif action == str(FlagState.DESTROY_ALL):
            self.game.killPlayer(int(unitIndex[0]))
        
        elif action == str(FlagState.CHANGE_FORMATION):
            self.game.changeFormation(actionPlayerId, target, unitIndex, FlagState.MOVE)

        elif action == str(FlagState.TRADE):
            target = target.strip("[")
            target = target.strip("]")
            target = target.split(",")
            if target[0] == '1':
                if int(unitIndex[0])==self.game.playerId:
                    self.game.tradePage=3
                    self.game.idTradeWith=actionPlayerId
                    self.view.ongletTradeYesNoQuestion(actionPlayerId)
            elif target[0] == '2':
                if int(unitIndex[0])==self.game.playerId or actionPlayerId == self.game.playerId:
                    if int(unitIndex[0])==self.game.playerId:
                        self.game.isMasterTrade=True
                        self.view.ongletTrade(self.game.playerId,self.game.idTradeWith)
                    else:
                        self.game.isMasterTrade=False
                        self.view.ongletTrade(self.game.idTradeWith,self.game.playerId)
                    self.game.tradePage=2
                    
            elif target[0] == '3':
                if int(unitIndex[0])==self.game.playerId:
                    self.game.isMasterTrade=False
                    self.game.tradePage=-1
                    self.game.idTradeWith=self.game.playerId
                    self.view.ongletTradeNoAnswer()
            elif target[0] == '4':
                if int(unitIndex[0])==self.game.playerId:
                    self.game.tradePage=4
                    self.game.toTrade = (target[1],target[2],target[3],target[4])
                    self.view.ongletTradeAskConfirm(actionPlayerId,self.game.toTrade[0],self.game.toTrade[1],self.game.toTrade[2],self.game.toTrade[3])
            elif target[0] == 'm' or target[0] == 'g':
                if target[0] == 'm':
                    ressourceType = p.Player.MINERAL
                elif target[0] == 'g':
                    ressourceType = p.Player.GAS
                if int(unitIndex[0]) != actionPlayerId:
                    self.game.trade(actionPlayerId, int(unitIndex[0]), ressourceType, int(target[1]))
                else:
                    self.game.trade(int(target[2]), actionPlayerId, ressourceType, int(target[1]))
                self.game.isMasterTrade=False
                self.game.tradePage=-1
                self.game.idTradeWith=self.game.playerId
                self.view.ongletTradeYesAnswer()
                
        elif action == str(FlagState.DEMAND_ALLIANCE):
            #actionPlayerId = le joueur qui change le status
            #unitIndex[0] = le joueur concerné par le changement
            #target = le nouveau status de l'alliance entre les deux
            self.game.demandAlliance(actionPlayerId, int(unitIndex[0]), target)
            self.view.refreshAlliances()


    def endGame(self):
        self.view.showGameIsFinished()
        self.view.root.destroy()

    def sendKillPlayer(self, playerId=None):
        if playerId == None:
            self.removePlayer()
            playerId = self.game.playerId
        self.pushChange(playerId, Flag(None,playerId,FlagState.DESTROY_ALL))

    #Enleve le joueur courant de la partie ainsi que ses units
    def removePlayer(self):
        if self.view.currentFrame == self.view.gameFrame and self.server.isGameStopped() == False:
            self.sendMessage('a quitté la partie')
            self.server.removePlayer(self.playerIp, self.game.players[self.game.playerId].name, self.game.playerId)


if __name__ == '__main__':
    c = Controller()
