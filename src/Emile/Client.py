# -*- coding: UTF-8 -*-
import View as v
import World as w
import Player as p
import Target as t
import Pyro4
#import socket

class Controller():
    def __init__(self):
        self.playerId=0
        self.players = [] #La liste des joueurs
        self.playerId = 0 #Le id du joueur courant
        self.view = v.View(self, 'Orion')
        self.multiSelect = False
        self.view.root.mainloop()
        
    def setMovingFlag(self,x,y):
        pos = self.players[self.playerId].camera.calcPointInWorld(x,y)
        for i in self.players[self.playerId].selectedObjects:
            if i.__module__ == 'Unit':
                i.changeFlag(t.Target(pos),2)
            
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
            if j.position[0] >= posSelected[0]-5 and j.position[0] <= posSelected[0]+5:
                if j.position[1] >= posSelected[1]-5 and j.position[1] <= posSelected[1]+5: 
                    if self.multiSelect == False:
                        self.players[self.playerId].selectedObjects = []
                    if j not in self.players[self.playerId].selectedObjects:
                        self.players[self.playerId].selectedObjects.append(j)
        print('selected:',self.players[self.playerId].selectedObjects)
    
    def action(self):
        self.multiSelect = False
        for i in self.players[self.playerId].units:
            if i.flag.flagState == 2:
                i.move()
        self.view.drawWorld()
        self.view.root.after(50, self.action)
        
    def connectServer(self, login, serverIP):
        self.server=Pyro4.core.Proxy("PYRO:controleurServeur@"+serverIP+":54440")
        try:
            self.server.testConnect()
            self.players.append(p.Player(login))
            self.playerId=self.server.getNumSocket(self.players[0])
            self.galaxy=w.Galaxy(self.server.getNumberOfPlayers(), self.server.getSeed())
            self.players[self.playerId].startGame([0,0],self.galaxy)
            self.startGame()
        except:
            self.view.loginFailed()
            self.view.drawLogin()
        
    def startGame(self):
        self.view.startGame()
        self.view.root.after(50, self.action)

c = Controller()