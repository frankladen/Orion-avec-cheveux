# -*- coding: UTF-8 -*-
from tkinter import *
import tkinter.messagebox as mb

class View():              
    def __init__(self, parent):
        self.parent = parent                  
        self.root=Tk()
        self.root.title("Orion")
        self.root.resizable(0,0)
        self.taille=800
        self.dragging = False
        self.selectStart = [0,0]
        self.selectEnd = [0,0]
        self.fLogin = self.fLogin()
        self.fLogin.pack()
        self.pLobby = None
        self.currentFrame = self.fLogin
        self.firstTime = True
        self.gameFrame = None
        self.sun=PhotoImage(file='images\sun.gif')
        self.greysun = PhotoImage(file='images\sunGREY.gif')
        self.planet=PhotoImage(file='images\planet.gif')
        self.greyplanet = PhotoImage(file='images\planetGREY.gif')
        self.motherShipSprite = PhotoImage(file = 'images\mothership.gif')
        self.nebula=PhotoImage(file='images\\nebula.gif')
        self.asteroid=PhotoImage(file='images\\asteroid.gif')
        # Quand le user ferme la fenêtre et donc le jeu, il faut l'enlever du serveur
        self.root.protocol('WM_DELETE_WINDOW', self.parent.removePlayer)
    
    def changeFrame(self, frame):
        self.currentFrame.pack_forget()
        frame.pack()
        self.currentFrame = frame
    #Frame principal du jeu    
    def fGame(self):
        gameFrame = Frame(self.root, bg="black")
        self.ships = []
        for i in range(0,8):
            self.ships.append(PhotoImage(file='images\ship'+str(i)+'.gif'))
        self.gameArea=Canvas(gameFrame, width=self.taille, height=self.taille-200, background='Black', relief='ridge')
        self.gameArea.grid(column=0,row=0, columnspan=5)#place(relx=0, rely=0,width=taille,height=taille)
        self.minimap= Canvas(gameFrame, width=200,height=200, background='Black', relief='raised')
        self.minimap.grid(column=0,row=1, rowspan=4)
        self.drawWorld()
        self.chat = Label(gameFrame, anchor=W, justify=LEFT, width=40, background='black', fg='white', relief='raised')
        self.chat.grid(row=1, column=1)
        self.entryMess = Entry(gameFrame, width=35)
        self.entryMess.grid(row=2, column=1)
        createScout = Button(gameFrame, text='Create Scout', command=lambda:self.parent.addUnit('Scout'))
        createScout.grid(row=1,column=3)
        stopSelectedUnits = Button(gameFrame, text='Stop', command=self.parent.setStandbyFlag)
        stopSelectedUnits.grid(row=2,column=3)
        deleteSelectedUnits = Button(gameFrame, text='Delete', command=self.parent.eraseUnit)
        deleteSelectedUnits.grid(row=2,column=4)
        self.assignControls()
        return gameFrame
    #Frame pour le login    
    def fLogin(self):
        loginFrame = Frame(self.root, bg="black")
        Label(loginFrame, text="Login:", fg="white", bg="black").grid(row=0, column=0)
        self.entryLogin = Entry(loginFrame, width=20)
        self.entryLogin.focus_set()
        self.entryLogin.grid(row=0, column=1)
        Label(loginFrame, text="Server:", fg="white", bg="black").grid(row=1, column=0)
        self.entryServer = Entry(loginFrame, width=20)
        self.entryServer.grid(row=1, column=1)
        widget = Button(loginFrame, text='Ok', command=lambda:self.lobbyEnter(0))
        widget.grid(row=2, column=1)
        self.entryServer.bind("<Return>",self.lobbyEnter)
        return loginFrame
    #Frame du lobby
    def fLobby(self):
        self.entryServer.unbind("<Return>")
        lobbyFrame = Frame(self.root, bg="black")
        if self.parent.server != None:
            pNum = len(self.parent.server.getSockets())
            for i in range(0, pNum):
                Label(lobbyFrame, text=self.parent.server.getSockets()[i][1], fg="white", bg="black").grid(row=i,column=0)
            Label(lobbyFrame, text='Admin : '+self.parent.server.getSockets()[0][1], fg="white", bg="black").grid(row=(pNum+1), column=1)
            if self.parent.playerId == 0:
                Button(lobbyFrame, text='Demarrer la partie', command=self.parent.startGame, bg="black", fg="white").grid(row=(pNum+2), column=1)
        return lobbyFrame
        
    def loginFailed(self):
        mb.showinfo('Erreur de connection', 'Le serveur est introuvable. Veuillez reessayer.')
    
    def gameHasBeenStarted(self):
        mb.showinfo('Erreur de connection', 'La partie a déjà débutée. Veuillez attendre sa fin.')
    
    def showGameIsFinished(self):
        mb.showinfo('Fin de la partie', 'L\'administrateur de la partie a quitté prématurément la partie, la partie est donc terminée.')

    #Methode pour dessiner
    def drawWorld(self):
        self.gameArea.delete(ALL)
        sunList = self.parent.galaxy.solarSystemList
        players = self.parent.players 
        id = self.parent.playerId
        for i in sunList:
            if self.parent.players[self.parent.playerId].inViewRange(i.sunPosition):
                i.discovered = True
                self.drawSun(i.sunPosition, players[id], True)
            else:
                if i.discovered:
                    self.drawSun(i.sunPosition, players[id], False)
            for j in i.planets:
                if self.parent.players[self.parent.playerId].inViewRange(j.position):
                    j.discovered = True
                    self.drawPlanet(j, players[id], True)
                else:
                    if j.discovered:
                        self.drawPlanet(j, players[id], False)
            for j in i.nebulas:
                self.drawNebula(j, players[id])
        for i in players:
            for j in i.units:
                if self.parent.players[self.parent.playerId].inViewRange(j.position):
                    j.discovered = True
                    self.drawUnit(j, i)
        if self.dragging:
            self.drawSelctionBox()
        self.drawMinimap()
        
    #Pour dessiner un soleil     
    def drawSun(self, sunPosition, player, isInFOW):
        if player.camera.isInFOV(sunPosition):
            distance = player.camera.calcDistance(sunPosition)
            if isInFOW:
                self.gameArea.create_image(distance[0],distance[1], image=self.sun)
            else:
                self.gameArea.create_image(distance[0],distance[1], image=self.greysun)
    
    #pour dessiner une planete        
    def drawPlanet(self, planet, player, isInFOW):
        planetPosition = planet.position
        if player.camera.isInFOV(planetPosition):
            distance = player.camera.calcDistance(planetPosition)
            if isInFOW:
                if planet in player.selectedObjects:
                    self.gameArea.create_oval(distance[0]-10, distance[1]-10, distance[0]+10, distance[1]+10,outline="green", tag="planet")
                    mVariable = "Mineral :" + str(planet.mineralQte)
                    gVariable = "Gaz :" + str(planet.gazQte)
                    self.gameArea.create_text(distance[0]-20, distance[1]-25,fill="cyan",text=mVariable)
                    self.gameArea.create_text(distance[0]-20, distance[1]-40,fill="green",text=gVariable)
                self.gameArea.create_image(distance[0],distance[1],image=self.planet)
            else:
                self.gameArea.create_image(distance[0], distance[1], image=self.greyplanet)

    #Pour dessiner une nebuleuse
    def drawNebula(self,nebula,player):
        nebulaPosition = nebula.position
        if player.camera.isInFOV(nebulaPosition):
            distance = player.camera.calcDistance(nebulaPosition)
            if nebula in player.selectedObjects:
                self.gameArea.create_oval(distance[0]-10, distance[1]-10, distance[0]+10, distance[1]+10,outline="green", tag="nebula")
                mVariable = "Gaz :" + str(nebula.gazQte)
                self.gameArea.create_text(distance[0]-20, distance[1]-25,fill="cyan",text=mVariable)
            self.gameArea.create_image(distance[0],distance[1],image=self.nebula) 
                
    #pour dessiner un vaisseau        
    def drawUnit(self, unit, player):
        ship=self.ships[player.id] #On prend l'image dependamment du joueur que nous sommes
        unitPosition = unit.position
        if self.parent.players[self.parent.playerId].camera.isInFOV(unitPosition):
            distance = self.parent.players[self.parent.playerId].camera.calcDistance(unitPosition)
            if unit in player.selectedObjects:
                self.gameArea.create_oval(distance[0]-8,distance[1]-8,distance[0]+8,distance[1]+8, outline="green")
            if unit.name.find('Scout') != -1:
                self.gameArea.create_image(distance[0]+1, distance[1], image=ship)
            elif unit.name.find('Mothership') != -1:
                self.gameArea.create_image(distance[0]+1, distance[1], image = self.motherShipSprite)
    #Dessine la minimap
    def drawMinimap(self):
        self.minimap.delete('deletable')
        sunList = self.parent.galaxy.solarSystemList
        players = self.parent.players
        if self.firstTime:
            for i in sunList:
                self.drawMiniSun(i.sunPosition)
                for j in i.planets:
                    self.drawMiniPlanet(j.position)
            self.firstTime = False
        for i in players:
            for j in i.units:
                self.drawMiniUnit(j)
        self.drawMiniFOV()  
    #Dessine le carrer de la camera dans la minimap    
    def drawMiniFOV(self):
        cameraX = (self.parent.players[self.parent.playerId].camera.position[0]-400 + self.parent.galaxy.width/2) / self.parent.galaxy.width * 200
        cameraY = (self.parent.players[self.parent.playerId].camera.position[1]-300 + self.parent.galaxy.height/2) / self.parent.galaxy.height * 200
        width = self.taille / self.parent.galaxy.width * 200
        height = self.taille / self.parent.galaxy.height * 150
        self.minimap.create_rectangle(cameraX, cameraY, cameraX+width, cameraY+height, outline='GREEN', tag='deletable')
    #Dessine un soleil dans la minimap    
    def drawMiniSun(self, sunPosition):
        sunX = (sunPosition[0] + self.parent.galaxy.width/2) / self.parent.galaxy.width * 200
        sunY = (sunPosition[1] + self.parent.galaxy.height/2) / self.parent.galaxy.height * 200
        self.minimap.create_oval(sunX-3, sunY-3, sunX+3, sunY+3, fill='ORANGE')
    #Dessine une planete dans la minimap        
    def drawMiniPlanet(self, planetPosition):
        planetX = (planetPosition[0] + self.parent.galaxy.width/2) / self.parent.galaxy.width * 200
        planetY = (planetPosition[1] + self.parent.galaxy.height/2) / self.parent.galaxy.height * 200
        self.minimap.create_oval(planetX-1, planetY-1, planetX+1, planetY+1, fill='LIGHT BLUE')
    #dessine une nebula dans la minimap
    def drawMiniNebula(self, nebulaPosition):
        nebulaX = (nebulaPosition[0] + self.parent.galaxy.width/2) / self.parent.galaxy.width * 200
        nebulaY = (nebulaPosition[1] + self.parent.galaxy.height/2) / self.parent.galaxy.height * 200
        self.minimap.create_oval(nebulaX-1, nebulaY-1, nebulaX+1, nebulaY+1, fill='PURPLE')
    #Dessine une unite dans la minimap        
    def drawMiniUnit(self, unit):
        unitX = (unit.position[0] + self.parent.galaxy.width/2) / self.parent.galaxy.width * 200
        planetY = (unit.position[1] + self.parent.galaxy.height/2) / self.parent.galaxy.height * 200
        if unit in self.parent.players[self.parent.playerId].units:
            self.minimap.create_polygon((unitX-2, planetY+1, unitX, planetY-1, unitX+2, planetY+1),fill='GREEN', tag='deletable')
        else:
            self.minimap.create_polygon((unitX-2, planetY+1, unitX, planetY-1, unitX+2, planetY+1),fill='RED', tag='deletable')
	#Dessine la boite de selection lors du clic-drag	
    def drawSelctionBox(self):
        self.gameArea.create_rectangle(self.selectStart[0], self.selectStart[1], self.selectEnd[0], self.selectEnd[1], outline='WHITE')

    #Actions quand on clic sur les fleches du clavier
    def keyPressUP(self, eve):
        if 'UP' not in self.parent.players[self.parent.playerId].camera.movingDirection:
            self.parent.players[self.parent.playerId].camera.movingDirection.append('UP')
            self.drawWorld()
    def keyPressDown(self, eve):
        if 'DOWN' not in self.parent.players[self.parent.playerId].camera.movingDirection:
            self.parent.players[self.parent.playerId].camera.movingDirection.append('DOWN')
            self.drawWorld()
    def keyPressLeft(self, eve):
        if 'LEFT' not in self.parent.players[self.parent.playerId].camera.movingDirection:
            self.parent.players[self.parent.playerId].camera.movingDirection.append('LEFT')
            self.drawWorld()
    def keyPressRight(self, eve):
        if 'RIGHT' not in self.parent.players[self.parent.playerId].camera.movingDirection:
            self.parent.players[self.parent.playerId].camera.movingDirection.append('RIGHT')
            self.drawWorld()
    #Actions quand on lache les touches
    def keyReleaseUP(self, eve):
        self.parent.players[self.parent.playerId].camera.movingDirection.remove('UP')
        self.drawWorld()
    def keyReleaseDown(self, eve):
        self.parent.players[self.parent.playerId].camera.movingDirection.remove('DOWN')
        self.drawWorld()
    def keyReleaseLeft(self, eve):
        self.parent.players[self.parent.playerId].camera.movingDirection.remove('LEFT')
        self.drawWorld()
    def keyReleaseRight(self, eve):
        self.parent.players[self.parent.playerId].camera.movingDirection.remove('RIGHT')
        self.drawWorld()
    #Actions avec la souris    
    def rightclic(self, eve):
        x = eve.x
        y = eve.y
        canva = eve.widget
        if x > 0 and x < self.taille:
            if y > 0 and y < self.taille-200:
                if canva == self.gameArea:
                    pos = self.parent.players[self.parent.playerId].camera.calcPointInWorld(x,y)
                    self.parent.setMovingFlag(pos[0],pos[1])
                elif canva == self.minimap:
                    pos = self.parent.players[self.parent.playerId].camera.calcPointMinimap(x,y)
                    self.parent.setMovingFlag(pos[0], pos[1])
                self.drawWorld()
    #Quand on fait un clic gauche (peu importe ou)
    def leftclic(self, eve):
        x = eve.x
        y = eve.y
        canva = eve.widget
        if canva == self.gameArea:     
            self.parent.select(x,y,canva)
        elif canva == self.minimap:
            self.parent.quickMove(x,y,canva)
    #Quand on fait un clic gauche et qu'on bouge
    def clicDrag(self,eve):
        if self.dragging == False:
            self.selectStart = [eve.x, eve.y]
            self.selectEnd = [eve.x, eve.y]
            self.dragging = True
        else:
            self.selectEnd = [eve.x, eve.y]
    #Quand on clicDrag et qu'on lache la souris
    def endDrag(self, eve):
        if self.dragging:
            self.dragging = False
            self.selectEnd = [eve.x, eve.y]
            self.parent.boxSelect(self.selectStart, self.selectEnd)    
    #Quand on appui sur enter dans le chat		
    def enter(self, eve):
        self.parent.sendMessage(self.entryMess.get())
        self.entryMess.delete(0,END)
        self.gameArea.focus_set()
    #Quand on appui sur enter dans le login
    def lobbyEnter(self, eve):
        self.parent.connectServer(self.entryLogin.get(), self.entryServer.get())
			
    def stop(self, eve):
        self.parent.setStandbyFlag()

    def delete(self, eve):
        self.parent.eraseUnit()
        
	#Pour la selection multiple	
    def shiftPress(self, eve):
        self.parent.multiSelect = True
    def shiftRelease(self, eve):
        self.parent.multiSelect = False
	
    #Assignation des controles	
    def assignControls(self):
        self.gameArea.focus_set()
        #Bindings des fleches
        self.gameArea.bind ("<Key-Up>", self.keyPressUP)
        self.gameArea.bind("<Key-Down>", self.keyPressDown)
        self.gameArea.bind("<Key-Left>", self.keyPressLeft)
        self.gameArea.bind("<Key-Right>", self.keyPressRight)
        self.gameArea.bind ("<KeyRelease-Up>", self.keyReleaseUP)
        self.gameArea.bind ("<KeyRelease-Down>", self.keyReleaseDown)
        self.gameArea.bind ("<KeyRelease-Left>", self.keyReleaseLeft)
        self.gameArea.bind ("<KeyRelease-Right>", self.keyReleaseRight)
        #Bindings de shift pour la multiselection
        self.gameArea.bind("<Shift_L>", self.shiftPress)
        self.gameArea.bind("<KeyRelease-Shift_L>", self.shiftRelease)
        #BINDINGS POUR LES SHORTCUTS CLAVIERS
        self.gameArea.bind("s", self.stop)
        self.gameArea.bind("S", self.stop)
        self.gameArea.bind("d", self.delete)
        self.gameArea.bind("D", self.delete)
        #Bindings des boutons de la souris
        self.gameArea.bind("<Button-3>", self.rightclic)
        self.gameArea.bind("<B3-Motion>", self.rightclic)
        self.minimap.bind("<Button-3>", self.rightclic)
        self.gameArea.bind("<Button-1>", self.leftclic)
        self.minimap.bind("<B1-Motion>",self.leftclic)
        self.minimap.bind("<Button-1>",self.leftclic)
        self.gameArea.bind("<B1-Motion>", self.clicDrag)
        self.gameArea.bind("<ButtonRelease-1>", self.endDrag)
        self.entryMess.bind("<Return>",self.enter)

