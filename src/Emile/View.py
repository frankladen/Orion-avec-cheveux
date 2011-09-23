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
        players = [self.parent.player] 
        for i in sunList:
            self.drawSun(i.sunPosition)
            for j in i.planets:
                self.drawPlanet(j.position)
        for i in players:
            for j in i.units:
                self.drawUnit(j.position)
         
    def drawSun(self, sunPosition):
        if self.parent.player.camera.isInFOV(sunPosition):
            distance = self.parent.player.camera.calcDistance(sunPosition)
            self.gameArea.create_oval(distance[0]-20, distance[1]-20, distance[0]+20, distance[1]+20, fill='RED')
    def drawPlanet(self, planetPosition):
        if self.parent.player.camera.isInFOV(planetPosition):
            distance = self.parent.player.camera.calcDistance(planetPosition)
            self.gameArea.create_oval(distance[0]-10, distance[1]-10, distance[0]+10, distance[1]+10, fill='BLUE')
            
    def drawUnit(self, unitPosition):
        if self.parent.player.camera.isInFOV(unitPosition):
            distance = self.parent.player.camera.calcDistance(unitPosition)
            self.gameArea.create_polygon((distance[0], distance[1]-5,distance[0]-5,distance[1]+5,distance[0]+5,distance[1]+5),fill='YELLOW')
        
    def keyPress(self, eve):
        code = eve.keycode
        if code == 37:
            self.parent.player.camera.move('LEFT')
        elif code == 38:
            self.parent.player.camera.move('UP')
        elif code == 39:
            self.parent.player.camera.move('RIGHT')
        elif code == 40:
            self.parent.player.camera.move('DOWN')
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