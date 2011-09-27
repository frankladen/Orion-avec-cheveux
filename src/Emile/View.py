# -*- coding: UTF-8 -*-
from tkinter import *
import tkinter.messagebox as mb

class View():              
    def __init__(self, parent ,title, taille=800):
        self.parent = parent                  
        self.root=Tk()
        self.root.title = title
        self.taille=taille
        self.drawLogin()
        
    def startGame(self):
        self.miniMapPosition = [0,self.taille-200]
        self.gameArea=Canvas(self.root, width=self.taille, height=self.taille, background='Black')
        self.gameArea.pack()
        self.drawWorld()
        self.assignControls()
        
    def drawLogin(self):
        Label(self.root, text="Login:").grid(row=0, column=0)
        login = Entry(self.root, width=20)
        login.grid(row=0, column=1)
        Label(self.root, text="Server:").grid(row=1, column=0)
        server = Entry(self.root, width=20)
        server.grid(row=1, column=1)
        widget = Button(self.root, text='Ok', command=lambda:self.parent.connectServer(login.get(), server.get()))
        widget.grid(row=2, column=1)
        
    def loginFailed(self):
        mb.showinfo('Erreur de connection', 'Le serveur est introuvable. Veuillez reessayer.')
    
    def drawWorld(self):
        self.gameArea.delete(ALL)
        sunList = self.parent.galaxy.solarSystemList
        players = self.parent.players 
        id = self.parent.playerId
        for i in sunList:
            self.drawSun(i.sunPosition, players[id])
            for j in i.planets:
                self.drawPlanet(j.position, players[id])
        for i in players:
            for j in i.units:
                self.drawUnit(j.position, players[id])
        self.drawMinimap()
         
    def drawSun(self, sunPosition, player):
        if player.camera.isInFOV(sunPosition):
            distance = player.camera.calcDistance(sunPosition)
            self.gameArea.create_oval(distance[0]-20, distance[1]-20, distance[0]+20, distance[1]+20, fill='RED')
            
    def drawPlanet(self, planetPosition, player):
        if player.camera.isInFOV(planetPosition):
            distance = player.camera.calcDistance(planetPosition)
            self.gameArea.create_oval(distance[0]-10, distance[1]-10, distance[0]+10, distance[1]+10, fill='BLUE', tag="planet")
            
    def drawUnit(self, unitPosition, player):
        if player.camera.isInFOV(unitPosition):
            distance = player.camera.calcDistance(unitPosition)
            self.gameArea.create_polygon((distance[0], distance[1]-5,distance[0]-5,distance[1]+5,distance[0]+5,distance[1]+5),fill='YELLOW', tag="unit")
    
    def drawMinimap(self,):
        self.gameArea.create_rectangle(self.miniMapPosition[0],self.miniMapPosition[1],self.miniMapPosition[0]+200,self.miniMapPosition[1]+200, fill="BLACK", outline="YELLOW", tag="miniMap")
        sunList = self.parent.galaxy.solarSystemList
        players = self.parent.players 
        for i in sunList:
            self.drawMiniSun(i.sunPosition)
            for j in i.planets:
                self.drawMiniPlanet(j.position)
        for i in players:
            for j in i.units:
                self.drawMiniUnit(j.position)
        self.drawMiniFOV()
        
    def drawMiniFOV(self):
        cameraX = (self.parent.players[self.parent.playerId].camera.position[0]-400 + self.parent.galaxy.width/2) / self.parent.galaxy.width * 200 + self.miniMapPosition[0]
        cameraY = (self.parent.players[self.parent.playerId].camera.position[1]-400 + self.parent.galaxy.height/2) / self.parent.galaxy.height * 200 + self.miniMapPosition[1]
        width = self.taille / self.parent.galaxy.width * 200
        height = self.taille / self.parent.galaxy.height * 200
        self.gameArea.create_rectangle(cameraX, cameraY, cameraX+width, cameraY+height, outline="GREEN")
        
    def drawMiniSun(self, sunPosition):
        sunX = (sunPosition[0] + self.parent.galaxy.width/2) / self.parent.galaxy.width * 200 + self.miniMapPosition[0]
        sunY = (sunPosition[1] + self.parent.galaxy.height/2) / self.parent.galaxy.height * 200 + self.miniMapPosition[1]
        self.gameArea.create_oval(sunX-4, sunY-4, sunX+4, sunY+4, fill='RED')
            
    def drawMiniPlanet(self, planetPosition):
        planetX = (planetPosition[0] + self.parent.galaxy.width/2) / self.parent.galaxy.width * 200 + self.miniMapPosition[0]
        planetY = (planetPosition[1] + self.parent.galaxy.height/2) / self.parent.galaxy.height * 200 + self.miniMapPosition[1]
        self.gameArea.create_oval(planetX-2, planetY-2, planetX+2, planetY+2, fill='BLUE')
            
    def drawMiniUnit(self, unitPosition):
        unitX = (unitPosition[0] + self.parent.galaxy.width/2) / self.parent.galaxy.width * 200 + self.miniMapPosition[0]
        planetY = (unitPosition[1] + self.parent.galaxy.height/2) / self.parent.galaxy.height * 200 + self.miniMapPosition[1]
        self.gameArea.create_polygon((unitX-2, planetY+1, unitX, planetY-1, unitX+2, planetY+1),fill='YELLOW')
        
    def keyPress(self, eve):
        code = eve.keycode
        if code == 37:
            self.parent.players[self.parent.playerId].camera.move('LEFT')
        elif code == 38:
            self.parent.players[self.parent.playerId].camera.move('UP')
        elif code == 39:
            self.parent.players[self.parent.playerId].camera.move('RIGHT')
        elif code == 40:
            self.parent.players[self.parent.playerId].camera.move('DOWN')
        elif code == 16:
            self.parent.multiSelect = True
        self.drawWorld()
        
    def rightclic(self, eve):
        x = eve.x
        y = eve.y
        self.parent.setMovingFlag(x,y)
        self.drawWorld()
    
    def leftclic(self, eve):
        x = eve.x
        y = eve.y
        canva = eve.widget
        self.parent.select(x,y,canva)
         
    def assignControls(self):
        self.gameArea.focus_set()
        self.gameArea.bind ("<Key>", self.keyPress)
        self.gameArea.bind("<Button-3>", self.rightclic)
        self.gameArea.bind("<Button-1>", self.leftclic)
