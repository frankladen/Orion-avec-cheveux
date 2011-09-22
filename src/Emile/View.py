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
        self.root.mainloop()
        
    
    def drawWorld(self):
        self.gameArea.delete(ALL)
        sunList = self.parent.galaxy.solarSystemList
        for i in sunList:
            self.drawSun(i.sunPosition)
            for j in i.planets:
                self.drawPlanet(j.position)
         
    def drawSun(self, sunPosition):
        if self.parent.cam.isInFOV(sunPosition):
            distance = self.parent.cam.calcDistance(sunPosition)
            self.gameArea.create_oval(distance[0]-20, distance[1]-20, distance[0]+20, distance[1]+20, fill='RED')
    def drawPlanet(self, planetPosition):
        if self.parent.cam.isInFOV(planetPosition):
            distance = self.parent.cam.calcDistance(planetPosition)
            self.gameArea.create_oval(distance[0]-10, distance[1]-10, distance[0]+10, distance[1]+10, fill='BLUE')
            
    def keyPress(self, eve):
        code = eve.keycode
        if code == 37:
            self.parent.cam.move('LEFT')
        elif code == 38:
            self.parent.cam.move('UP')
        elif code == 39:
            self.parent.cam.move('RIGHT')
        elif code == 40:
            self.parent.cam.move('DOWN')
        self.drawWorld()
        
    def assignControls(self):
        self.gameArea.focus_set()
        self.gameArea.bind ("<Key>", self.keyPress)