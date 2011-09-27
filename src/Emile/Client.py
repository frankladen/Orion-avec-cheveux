# -*- coding: UTF-8 -*-
import View as v
import World as w
import Player as p
import Target as t
import Pyro4

class Controller():
    def __init__(self):
        self.playerId=0
        self.players = [] #La liste des joueurs
        self.playerId = 0 #Le id du joueur courant
        self.refresh = 0
        self.view = v.View(self)
        self.multiSelect = False
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
            self.view.changeFrame(self.view.fLogin)
        
    def startGame(self):
        self.view.changeFrame(self.view.fGame())
        self.view.root.after(50, self.action)
        
    def sendActionsToServer(self, flag, unit=None):
        #if isinstance(flag.finalTarget, t.PlayerObject):
        #    if unit is not None:
        #        actionToSend=playerId+'/'+self.refresh+'/'+'unit'+'/'+flag.flagState+'/'+unit
        #else:
        actionToSend=playerId+'/'+self.refresh+'/'+'point'+'/'+flag.flagState+'/'+flag.finalTarget.position
        self.server.sendAction(actionToSend)
        refresh+=1
        

c = Controller()