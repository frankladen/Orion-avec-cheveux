from tkinter import *

class View():              
    def __init__(self, parent ,title, taille=800):
        self.parent = parent                  
        self.root=Tk()
        self.root.title = title
        self.taille=taille
        self.gameArea=Canvas(self.root, width=taille, height=taille, background='Black')
        self.gameArea.pack()
        self.drawWorld()
        self.assignControls()
        
    
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
         
    def drawSun(self, sunPosition, player):
        if player.camera.isInFOV(sunPosition):
            distance = player.camera.calcDistance(sunPosition)
            self.gameArea.create_oval(distance[0]-20, distance[1]-20, distance[0]+20, distance[1]+20, fill='RED')
            
    def drawPlanet(self, planetPosition, player):
        if player.camera.isInFOV(planetPosition):
            distance = player.camera.calcDistance(planetPosition)
            self.gameArea.create_oval(distance[0]-10, distance[1]-10, distance[0]+10, distance[1]+10, fill='BLUE')
            
    def drawUnit(self, unitPosition, player):
        if player.camera.isInFOV(unitPosition):
            distance = player.camera.calcDistance(unitPosition)
            self.gameArea.create_polygon((distance[0], distance[1]-5,distance[0]-5,distance[1]+5,distance[0]+5,distance[1]+5),fill='YELLOW')
        
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
        self.drawWorld()
        
    def clic(self, eve):
        x = eve.x
        y = eve.y
        self.parent.setMovingFlag(x,y)
        self.drawWorld()
         
    def assignControls(self):
        self.gameArea.focus_set()
        self.gameArea.bind ("<Key>", self.keyPress)
        self.gameArea.bind("<Button-3>", self.clic)