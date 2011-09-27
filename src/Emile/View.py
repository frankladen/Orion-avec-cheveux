from tkinter import *

class View():              
    def __init__(self, parent ,title, taille=800):
        self.parent = parent                  
        self.root=Tk()
        self.root.title = title
        self.mainFrame = Frame(self.root)
        self.mainFrame.pack()
        self.taille=taille
        self.miniMapPosition = [0,0]
        self.gameArea=Canvas(self.mainFrame, width=taille, height=taille-200, background='Black')
        self.gameArea.grid(column=0,row=0, columnspan=5)#place(relx=0, rely=0,width=taille,height=taille)
        self.minimap= Canvas(self.mainFrame, width=200,height=200, background='Black')
        self.minimap.grid(column=0,row=1)
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
                self.drawPlanet(j, players[id])
        for i in players:
            for j in i.units:
                self.drawUnit(j, players[id])
        self.drawMinimap()
         
    def drawSun(self, sunPosition, player):
        if player.camera.isInFOV(sunPosition):
            distance = player.camera.calcDistance(sunPosition)
            self.gameArea.create_oval(distance[0]-20, distance[1]-20, distance[0]+20, distance[1]+20, fill='RED')
            
    def drawPlanet(self, planet, player):
        planetPosition = planet.position
        if player.camera.isInFOV(planetPosition):
            distance = player.camera.calcDistance(planetPosition)
            if planet in player.selectedObjects:
                self.gameArea.create_oval(distance[0]-10, distance[1]-10, distance[0]+10, distance[1]+10, fill='BLUE',outline="green", tag="planet")
            else:
                self.gameArea.create_oval(distance[0]-10, distance[1]-10, distance[0]+10, distance[1]+10, fill='BLUE', tag="planet")
            
    def drawUnit(self, unit, player):
        unitPosition = unit.position
        if player.camera.isInFOV(unitPosition):
            distance = player.camera.calcDistance(unitPosition)
            if unit in player.selectedObjects:
                self.gameArea.create_oval(distance[0]-8,distance[1]-8,distance[0]+8,distance[1]+8, outline="green")
            self.gameArea.create_polygon((distance[0], distance[1]-5,distance[0]-5,distance[1]+5,distance[0]+5,distance[1]+5),fill='YELLOW', tag="unit")
    
    def drawMinimap(self,):
        self.minimap.delete(ALL)
        #self.gameArea.create_rectangle(self.miniMapPosition[0],self.miniMapPosition[1],self.miniMapPosition[0]+200,self.miniMapPosition[1]+200, fill="BLACK", outline="YELLOW", tag="miniMap")
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
        cameraX = (self.parent.players[self.parent.playerId].camera.position[0]-400 + self.parent.galaxy.width/2) / self.parent.galaxy.width * 200
        cameraY = (self.parent.players[self.parent.playerId].camera.position[1]-300 + self.parent.galaxy.height/2) / self.parent.galaxy.height * 200
        width = self.taille / self.parent.galaxy.width * 200
        height = self.taille / self.parent.galaxy.height * 150
        self.minimap.create_rectangle(cameraX, cameraY, cameraX+width, cameraY+height, outline="GREEN")
        
    def drawMiniSun(self, sunPosition):
        sunX = (sunPosition[0] + self.parent.galaxy.width/2) / self.parent.galaxy.width * 200
        sunY = (sunPosition[1] + self.parent.galaxy.height/2) / self.parent.galaxy.height * 200
        self.minimap.create_oval(sunX-4, sunY-4, sunX+4, sunY+4, fill='RED')
            
    def drawMiniPlanet(self, planetPosition):
        planetX = (planetPosition[0] + self.parent.galaxy.width/2) / self.parent.galaxy.width * 200
        planetY = (planetPosition[1] + self.parent.galaxy.height/2) / self.parent.galaxy.height * 200
        self.minimap.create_oval(planetX-2, planetY-2, planetX+2, planetY+2, fill='BLUE')
            
    def drawMiniUnit(self, unitPosition):
        unitX = (unitPosition[0] + self.parent.galaxy.width/2) / self.parent.galaxy.width * 200
        planetY = (unitPosition[1] + self.parent.galaxy.height/2) / self.parent.galaxy.height * 200
        self.minimap.create_polygon((unitX-2, planetY+1, unitX, planetY-1, unitX+2, planetY+1),fill='YELLOW')
        
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
        print(canva)
        if canva == self.gameArea:     
            self.parent.select(x,y,canva)
        elif canva == self.minimap:
            self.parent.quickMove(x,y,canva)
         
    def assignControls(self):
        self.gameArea.focus_set()
        self.gameArea.bind ("<Key>", self.keyPress)
        self.gameArea.bind("<Button-3>", self.rightclic)
        self.gameArea.bind("<Button-1>", self.leftclic)
        self.minimap.bind("<Button-1>",self.leftclic)