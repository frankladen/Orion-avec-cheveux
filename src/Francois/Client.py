# -*- coding: UTF-8 -*-
import View as v
import World as w
import Player as p
import Target as t
import Unit as u
from Flag import *
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
        self.playerIp = socket.gethostbyname(socket.getfqdn())
        self.server = None
        self.isStarted=False
        self.view = v.View(self)
        self.multiSelect = False
        self.currentFrame = None

        self.view.root.mainloop()
    #Pour changer le flag des unites selectionne pour le deplacement    
    def setMovingFlag(self,x,y):
        for i in self.players[self.playerId].selectedObjects:
            if i.__module__ == 'Unit':
                self.pushChange(i, Flag(i,t.Target([x,y,0]),FlagState.MOVE))
    #Pour changer le flag des unites selectionne pour l'arret
    def setStandbyFlag(self):
        for i in self.players[self.playerId].selectedObjects:
            if i.__module__ == 'Unit':
                self.pushChange(i, Flag(i,t.Target([i.position[0],i.position[1],0]),FlagState.STANDBY))
    #Pour ajouter une unit             
    def addUnit(self, unit):
        if unit == "Scout":
            self.pushChange('Scout', 'addunit')
    #Trade entre joueurs
    def tradePlayers(self, items, playerId2):
        for i in items:
            self.pushChange(i, self.playerId2)
    #Pour effacer un Unit
    def eraseUnit(self):
        if len(self.players[self.playerId].selectedObjects) == 1:
            if self.players[self.playerId].selectedObjects[0].__module__ == 'Unit':
                self.pushChange(self.players[self.playerId].selectedObjects[0], 'deleteUnit')
                self.players[self.playerId].selectedObjects.pop(0)
    #Pour effacer tous les units
    def eraseUnits(self):
        self.pushChange('lollegarspartdelagame', 'deleteAllUnits')    #Pour selectionner une unit
        
    def select(self, x, y, canva):
        posSelected = self.players[self.playerId].camera.calcPointInWorld(x,y)
        #Si on selectionne une planete
        for i in self.galaxy.solarSystemList:
            for j in i.planets:
                if j.position[0] >= posSelected[0]-10 and j.position[0] <= posSelected[0]+10:
                    if j.position[1] >= posSelected[1]-10 and j.position[1] <= posSelected[1]+10:
                        if j not in self.players[self.playerId].selectedObjects:
                            self.players[self.playerId].selectedObjects = []
                            self.players[self.playerId].selectedObjects.append(j)
        #Si on selectionne une unit               
        for j in self.players[self.playerId].units:
            if j.position[0] >= posSelected[0]-8 and j.position[0] <= posSelected[0]+8:
                if j.position[1] >= posSelected[1]-8 and j.position[1] <= posSelected[1]+8: 
                    if self.multiSelect == False:
                        self.players[self.playerId].selectedObjects = []
                    if j not in self.players[self.playerId].selectedObjects:
                        self.players[self.playerId].selectedObjects.append(j)
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
        for i in self.players[self.playerId].units:
            if i.position[0] >= realStart[0]-8 and i.position[0] <= realEnd[0]+8:
                if i.position[1] >= realStart[1]-8 and i.position[1] <= realEnd[1]+8:
                    if first:
                        self.players[self.playerId].selectedObjects = []
                        first = False
                    self.players[self.playerId].selectedObjects.append(i)
    #Deplacement rapide de la camera vers un endroit de la minimap
    def quickMove(self, x,y, canva):
        posSelected = self.players[self.playerId].camera.calcPointOnMap(x,y)
        self.players[self.playerId].camera.position = posSelected
    #Envoyer le message pour le chat
    def sendMessage(self, mess):
        if mess != "":
            self.server.addMessage(mess, self.players[self.playerId].name)
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
            self.players[self.playerId].camera.move()
            for p in self.players:
                for i in p.units:
                    if i.flag.flagState == 2:
                        i.move()
            self.refreshMessages()
            #À chaque itération je pousse les nouveaux changements au serveur et je demande des nouvelles infos.
            self.pullChange()
            self.view.drawWorld()
        else:
            if self.server.isGameStarted() == True:
                self.startGame()
            else:
                waitTime=1000
                self.view.pLobby = self.view.fLobby()
                self.view.changeFrame(self.view.pLobby)

        self.view.root.after(waitTime, self.action)  
	#Connection au serveur			
    def connectServer(self, login, serverIP):
        self.server=Pyro4.core.Proxy("PYRO:controleurServeur@"+serverIP+":54440")
        try:
            #Je demande au serveur si la partie est démarrée, si oui on le refuse de la partie, cela permet de vérifier
            #en même temps si le serveur existe réellement à cette adresse.
            if self.server.isGameStarted() == True:
                self.view.gameHasBeenStarted()
                self.view.changeFrame(self.view.fLogin)
            else:
                #Je fais chercher auprès du serveur l'ID de ce client et par le fais même, le serveur prend connaissance de mon existence
                self.playerId=self.server.getNumSocket(login, self.playerIp)
                #Je vais au lobby, si la connection a fonctionner
                self.view.pLobby = self.view.fLobby()
                self.view.changeFrame(self.view.pLobby)
                self.action()
        except:
            self.view.loginFailed()
            self.view.changeFrame(self.view.fLogin)
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
        self.players[self.playerId].addCamera([0,0],self.galaxy)
        self.view.gameFrame = self.view.fGame()
        self.view.changeFrame(self.view.gameFrame)
        self.view.root.after(50, self.action)
    
    #Méthode de mise à jour auprès du serveur, actionnée à chaque
    def pushChange(self, playerObject, flag):
        if flag == 'addunit':
            actionString = str(self.playerId)+"/"+playerObject+"/"+flag+"/lolcasertarienceboutla"
            self.server.addChange(actionString)
        elif flag == 'deleteUnit':
            actionString = str(self.playerId)+"/"+str(self.players[self.playerId].units.index(playerObject))+"/"+flag+"/klolyvamourirleunit"
            self.server.addChange(actionString)
        elif flag == 'deleteAllUnits':
            actionString = str(self.playerId)+"/"+playerObject+"/"+flag+"/lolypartdelapartie"
            self.server.addChange(actionString)
        elif flag.__module__ == 'Flag':
            actionString = str(self.playerId)+"/"+str(self.players[self.playerId].units.index(playerObject))+"/"+str(flag.flagState)+"/"+str(flag.finalTarget.position)
            self.server.addChange(actionString)
    
    def pullChange(self):
        changes = self.server.getChange(self.playerId, self.refresh)
        for changeString in changes:
            self.doAction(changeString)
        #si le joueur est trop en avance
        #if change[len(change)].find("*") != -1 :
            #j'isole le nombre de frame d'avance pour utilisation futurs
        #    frameTooHigh = int(change[len(change)].rstrip("*"))
        self.refresh+=1
            
    def getRefresh(self):
        return self.refresh
    
    def doAction(self, changeString):
        changeInfo = changeString.split("/")
        actionPlayerId = int(changeInfo[0])
        unitIndex = changeInfo[1]
        action = changeInfo[2]
        target = changeInfo[3]
        refresh = int(changeInfo[4])
        if action == str(FlagState.MOVE) or action == str(FlagState.STANDBY):
            target = target.strip("[")
            target = target.strip("]")
            target = target.split(",")
            for i in range(0, len(target)):
                target[i]=math.trunc(float(target[i]))
            self.players[actionPlayerId].units[int(unitIndex)].changeFlag(t.Target([target[0],target[1],target[2]]),int(action))
        elif action == 'deleteAllUnits':
            self.players[actionPlayerId].units = []
        elif action == 'addunit':
            if unitIndex == 'Scout':
                self.players[actionPlayerId].units.append(u.Unit('Scout00'+str(len(self.players[actionPlayerId].units)),[50,100,0], moveSpeed=5.0))
        elif action == 'deleteUnit':
            self.players[actionPlayerId].units.pop(int(unitIndex))

if __name__ == '__main__':
    c = Controller()
