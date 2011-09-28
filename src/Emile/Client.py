# -*- coding: UTF-8 -*-
import View as v
import World as w
import Player as p
import Target as t
import Pyro4
from time import time



class Controller():
    def __init__(self):
        self.playerId=0
        self.players = [] #La liste des joueurs
        self.playerId = 0 #Le id du joueur courant
        self.refresh = 0
        self.isStarted=False
        self.view = v.View(self)
        self.multiSelect = False
        self.currentFrame

        self.view.root.mainloop()
        
    def setMovingFlag(self,x,y):
        for i in self.players[self.playerId].selectedObjects:
            if i.__module__ == 'Unit':
                i.changeFlag(t.Target([x,y]),2)

    def select(self, x, y, canva):
        posSelected = self.players[self.playerId].camera.calcPointInWorld(x,y)
        for i in self.galaxy.solarSystemList:
            for j in i.planets:
                if j.position[0] >= posSelected[0]-10 and j.position[0] <= posSelected[0]+10:
                    if j.position[1] >= posSelected[1]-10 and j.position[1] <= posSelected[1]+10:
                        if j not in self.players[self.playerId].selectedObjects:
                            self.players[self.playerId].selectedObjects = []
                            self.players[self.playerId].selectedObjects.append(j)
                            
        for j in self.players[self.playerId].units:
            if j.position[0] >= posSelected[0]-8 and j.position[0] <= posSelected[0]+8:
                if j.position[1] >= posSelected[1]-8 and j.position[1] <= posSelected[1]+8: 
                    if self.multiSelect == False:
                        self.players[self.playerId].selectedObjects = []
                    if j not in self.players[self.playerId].selectedObjects:
                        self.players[self.playerId].selectedObjects.append(j)
    
    def quickMove(self, x,y, canva):
        posSelected = self.players[self.playerId].camera.calcPointOnMap(x,y)
        self.players[self.playerId].camera.position = posSelected
    
    def action(self, waitTime=50):
        if self.view.currentFrame != self.view.pLobby:
            self.multiSelect = False
            for i in self.players[self.playerId].units:
                if i.flag.flagState == 2:
                    i.move()
            #À chaque itération je pousse les nouveaux changements au serveur et je demande des nouvelles infos.
            self.pullChange()
            self.pushChange()
                    
            self.view.drawWorld()
             
        else:
            if self.server.isGameStarted == True:
                self.startGame()
            else:
                waitTime=500
                for i in range(len(self.players), len(self.server.getSockets())):
                    self.players[i].append(self.server.getSockets[i])
                self.view.pLobby = self.view.fLobby()
                self.view.changeFrame(self.view.pLobby)
        self.view.root.after(waitTime, self.action)  
				
    def connectServer(self, login, serverIP):
        self.server=Pyro4.core.Proxy("PYRO:controleurServeur@"+serverIP+":54440")
        try:
            self.server.testConnect()
            #J'initialise l'objet player et je le rajoute a sa liste
            self.players.append(p.Player(login))
            #Je fais chercher auprès du serveur l'ID de ce client et par le fais même, le serveur prend connaissance de mon existence
            self.playerId=self.server.getNumSocket(self.players[0])
            print("Mon Id :",self.playerId)

        except:
            self.view.loginFailed()
            self.view.changeFrame(self.view.fLogin)
            
        #Je vais au lobby, si la connection a fonctionner
        self.view.changeFrame(self.view.pLobby)
        self.action()
        
    def startGame(self):
        self.server.startGame()
        self.galaxy=w.Galaxy(self.server.getNumberOfPlayers(), self.server.getSeed())
        self.players[self.playerId].startGame([0,0],self.galaxy)
        self.view.changeFrame(self.view.fGame())
        self.view.root.after(50, self.action)
    
    #Méthode de mise à jour auprès du serveur, actionnée à chaque
    def pushChange(self):
        unitsState = []
        for i in self.players[self.playerId].units:
            unitsState.append(self.playerId,"/",self.server.getServerTime(),"/",i.__class__.__name__, "/" ,i.getFlag)
        
        self.server.addChange(unitsState, self.playerId, self.server.getServerTime())
    
    def pullChange(self):
        change = self.server.getChange(self.playerId,self.getCurrentFrame())
        #si le joueur est trop en avance
        if change[len(change)].find("*") != -1 :
            #j'isole le nombre de frame d'avance pour utilisation futurs
            frameTooHigh = int(change[len(change)].rstrip("*"))
            
    def getCurrentFrame(self):
        return self.currentFrame
        