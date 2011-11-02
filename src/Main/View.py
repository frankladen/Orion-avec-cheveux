# -*- coding: UTF-8 -*-
from tkinter import *
from Unit import *

from Constants import *
from winsound import *
import tkinter.messagebox as mb
import subprocess

class View():
    ACTIONMENU_ICON_WIDTH=37
    ACTIONMENU_ICON_HEIGHT=34
    MAIN_MENU=1
    WAITING_FOR_RALLY_POINT_MENU=2
    MOTHERSHIP_BUILD_MENU=3
        
    def __init__(self, parent):
        self.parent = parent                  
        self.root=Tk()
        self.root.title("Orion")
        self.root.resizable(0,0)
        #la taille du jeu se resize selon la résolution de l'écran, niceshithum?
        self.taille=self.root.winfo_screenheight()-125
        if self.taille>800:
            self.taille=800
        self.root.geometry('+25+5')
        self.dragging = False
        self.hpBars=False
        self.selectStart = [0,0]
        self.selectEnd = [0,0]
        self.positionMouse = [0,0,0]
        self.mainMenuBG = PhotoImage(file='images/Menus/MainMenuBG.gif')
        self.mainMenu = self.fMainMenu()
        self.mainMenu.pack()
        self.pLobby = None
        self.currentFrame = self.mainMenu
        self.firstTime = True
        self.gameFrame = None
        self.joinGame = self.fJoinGame()
        self.createServer = self.fCreateServer()
        self.actionMenuType = self.MAIN_MENU
        self.Actionmenu = None
        self.unitsConstructionPanel = None
        self.isSettingRallyPointPosition = False
        self.sun=PhotoImage(file='images/Galaxy/sun.gif')
        self.sunFOW = PhotoImage(file='images/Galaxy/sunFOW.gif')
        self.planet=PhotoImage(file='images/Galaxy/planet.gif')
        self.planetFOW = PhotoImage(file='images/Galaxy/planetFOW.gif')
        self.nebula=PhotoImage(file='images/Galaxy/nebula.gif')
        self.nebulaFOW=PhotoImage(file='images/Galaxy/nebulaFOW.gif')
        self.explosion=PhotoImage(file='images/explosion.gif')
        self.attacking = False
        self.asteroid=PhotoImage(file='images/Galaxy/asteroid.gif')
        self.asteroidFOW=PhotoImage(file='images/Galaxy/asteroidFOW.gif')
        self.mineral = PhotoImage(file='images/Planet/crystal.gif')
        self.planetBackground = PhotoImage(file='images/Planet/background.gif')
        self.galaxyBackground = PhotoImage(file='images/Galaxy/night-sky.gif')
        self.gifStop = PhotoImage(file='images/icones/stop2.gif')
        self.gifMove = PhotoImage(file='images/icones/move2.gif')
        self.gifCancel = PhotoImage(file='images/icones/delete2.gif')
        self.gifAttack = PhotoImage(file='images/icones/attack2.gif')
        self.gifRallyPoint = PhotoImage(file='images/icones/icone2.gif')
        self.gifBuild = PhotoImage(file = 'images/icones/build.gif')
        self.gifCadreMenuAction = PhotoImage(file = 'images/cadreMenuAction2.gif')
        self.iconCancel = PhotoImage(file = 'images/icones/cancelUnit.gif')
        self.gifPatrol = PhotoImage(file='images/icones/patrol2.gif')
        self.gifChat = PhotoImage(file='images/icones/boutonChat.gif')
        self.gifTrade = PhotoImage(file='images/icones/boutonTrade.gif')
        self.gifTeam = PhotoImage(file='images/icones/boutonTeam.gif')
        self.gifTransport = PhotoImage(file='images/icones/transport.gif')
        self.gifCargo = PhotoImage(file='images/icones/cargo.gif')
        self.gifUnit = PhotoImage(file='images/icones/unit.gif')
        self.gifSelectedUnit = PhotoImage(file='images/icones/boutonSelectedUnit.gif')
        self.attacking = False
        self.selectAllUnits = False
        self.wantToCancelUnitBuild = False
        # Quand le user ferme la fenêtre et donc le jeu, il faut l'enlever du serveur
        self.root.protocol('WM_DELETE_WINDOW', self.parent.removePlayer)
    
    def changeFrame(self, frame):
        self.currentFrame.pack_forget()
        frame.pack()
        self.currentFrame = frame

    #Frame principal du jeu    
    def fGame(self):
        gameFrame = Frame(self.root, bg="black")
        self.scoutShips = []
        self.attackShips = []
        self.motherShips = []
        self.transportShips = []
        self.landedShips = []
        self.gatherShips = []
        self.landingZones = []
        for i in range(0,8):
            self.scoutShips.append(PhotoImage(file='images/Ships/Scoutships/Scoutship'+str(i)+'.gif'))
            self.attackShips.append(PhotoImage(file='images/Ships/Attackships/Attackship'+str(i)+'.gif'))
            self.motherShips.append(PhotoImage(file='images/Ships/Motherships/Mothership'+str(i)+'.gif'))
            self.transportShips.append(PhotoImage(file='images/Ships/Transport/Transport'+str(i)+'.gif'))
            self.landedShips.append(PhotoImage(file='images/Planet/LandedShips/landed'+str(i)+'.gif'))
            self.gatherShips.append(PhotoImage(file='images/Ships/Cargo/Cargo'+str(i)+'.gif'))
            self.landingZones.append(PhotoImage(file='images/Planet/LandingZones/landing'+str(i)+'.gif'))
        Label(gameFrame, text="Mineraux: ", bg="black", fg="white", width=10, anchor=E).grid(column=0, row=0)
        self.showMinerals=Label(gameFrame, text=self.parent.players[self.parent.playerId].mineral, fg="white", bg="black", anchor=W)
        self.showMinerals.grid(column=1,row=0)
        Label(gameFrame, text="Gaz: ", bg="black", fg="white", width=10, anchor=E).grid(column=2, row=0)
        self.showGaz=Label(gameFrame, text=self.parent.players[self.parent.playerId].gaz, fg="white", bg="black", anchor=W)
        self.showGaz.grid(column=3,row=0)
        self.gameArea=Canvas(gameFrame, width=self.taille, height=self.taille-200, background='Black', relief='ridge')
        self.gameArea.grid(column=0,row=1, columnspan=5)#place(relx=0, rely=0,width=taille,height=taille)
        self.minimap= Canvas(gameFrame, width=200,height=200, background='Black', relief='raised')
        self.minimap.grid(column=0,row=2, rowspan=4)
        self.menuModes=Canvas(gameFrame, width=self.taille, height=200, background='black', relief='ridge')
        self.menuModes.grid(row=2,column=2, rowspan=4)
        self.menuModes.chat = Label(gameFrame, anchor=W, justify=LEFT, width=75, background='black', fg='white', relief='raised')
        self.menuModes.entryMess = Entry(gameFrame, width=60)
        self.Actionmenu = Canvas(gameFrame,width=(self.taille/4),height=(self.taille/4),background='black')
        self.Actionmenu.grid(column=3,row=2, rowspan=4)
        self.changeBackground('GALAXY')
        self.drawWorld()
        self.createActionMenu(self.MAIN_MENU)
        self.unitsConstructionPanel = Canvas(gameFrame, width = self.taille/4, height = self.taille/2, background = 'black', relief = "ridge")
        self.unitsConstructionPanel.grid(column = 3, row = 1)
        self.ongletChat(gameFrame)
        self.assignControls()
        return gameFrame

    def ongletTeam(self):
        self.menuModesOnlets() 
        self.menuModes.create_text(150,50,text='voici le menu Team',fill='white')
        self.menuModes.chat.grid_forget()
        self.menuModes.entryMess.grid_forget()
        
    def ongletTrade(self):
        self.menuModesOnlets()
        self.menuModes.create_text(150,50,text='voici le menu Tradeeee',fill='red')
        self.menuModes.chat.grid_forget()
        self.menuModes.entryMess.grid_forget()
        
    def ongletSelectedUnit(self):
        self.menuModesOnlets()
        if len(self.parent.players[self.parent.playerId].selectedObjects) > 0:
            if isinstance(self.parent.players[self.parent.playerId].selectedObjects[0],Unit):
                unitList = self.parent.players[self.parent.playerId].selectedObjects
                countList = [0,0,0,0,0]
                frenchNameList = ["Vaisseau d'attaque", "Scout", "Cargo", "Vaisseau de transport", "Vaisseau mère"] #en attendant les constantes à jerôme...
                y = 30
                
                for i in unitList:
                    if i.type == i.ATTACK_SHIP:
                        countList[0] += 1
                    elif i.type == i.SCOUT:
                        countList[1] += 1
                    elif i.type == i.CARGO:
                        countList[2] += 1
                    elif i.type == i.TRANSPORT:
                        countList[3] += 1
                    elif i.type == i.MOTHERSHIP:
                        countList[4] += 1
                
                for u in range(0, len(countList)):
                    if countList[u] != 0:
                        self.menuModes.create_text(5, y, text = str(countList[u]) + " " + frenchNameList[u], anchor = NW, fill = 'white')
                        y+=20
        self.menuModes.chat.grid_forget()
        self.menuModes.entryMess.grid_forget()
        
    def ongletChat(self,gameFrame):
        self.menuModesOnlets()
        self.menuModes.chat.grid(row=3, column=2)
        self.menuModes.entryMess.grid(row=4, column=2)
        self.menuModes.entryMess.bind("<Return>",self.enter)
        self.parent.refreshMessages(self.menuModes.chat)
        
    # delete tout ce qu'il y a dans le canvas menuModes + affiche les 3 menus
    def menuModesOnlets(self):
        self.menuModes.delete(ALL)
        self.menuModes.create_image(0,0,image=self.gifChat,anchor = NW,tag='bouton_chat')
        self.menuModes.create_image(77,0,image=self.gifTrade,anchor = NW,tag='bouton_trade')
        self.menuModes.create_image(150,0,image=self.gifTeam,anchor = NW,tag='bouton_team')
        self.menuModes.create_image(227,0,image=self.gifSelectedUnit,anchor = NW,tag='bouton_selectedUnit')

    def createActionMenu(self, type):
        self.Actionmenu.delete(ALL)
        if(type == self.MAIN_MENU):
            self.Actionmenu.create_image(0,0,image=self.gifCadreMenuAction,anchor = NW, tag='actionMain')
            units = self.parent.players[self.parent.playerId].selectedObjects 
            if len(units) > 0:
                if isinstance(units[0], Unit):
                    self.Actionmenu.create_image(13,35,image=self.gifMove,anchor = NW, tags = 'Button_Move')
                    self.Actionmenu.create_image(76,35,image=self.gifStop,anchor = NW, tags = 'Button_Stop', tag='actionMenu')
                    if isinstance(units[0], SpaceAttackUnit):
                        self.Actionmenu.create_image(140,35,image=self.gifAttack,anchor = NW, tags = 'Button_Attack')
                    if isinstance(units[0], Mothership):
                        self.Actionmenu.create_image(140,35,image=self.gifRallyPoint,anchor = NW, tags = 'Button_RallyPoint')
                        self.Actionmenu.create_image(13,89,image = self.gifBuild, anchor = NW, tags = 'Button_Build')
        elif(type == self.MOTHERSHIP_BUILD_MENU):
            self.Actionmenu.create_image(0,0,image=self.gifCadreMenuAction,anchor = NW, tag='actionMain')
            self.Actionmenu.create_image(13,35,image = self.gifUnit, anchor = NW, tags = 'Button_Build_Scout')
            self.Actionmenu.create_image(76,35,image = self.gifAttack, anchor = NW, tags = 'Button_Build_Attack')
            self.Actionmenu.create_image(139,35,image = self.gifCargo, anchor = NW, tags = 'Button_Build_Gather')
            self.Actionmenu.create_image(13,89,image = self.gifTransport, anchor = NW, tags = 'Button_Build_Transport')
        elif(type == self.WAITING_FOR_RALLY_POINT_MENU):
            self.Actionmenu.create_text(0,0,text = "Cliquer a un endroit dans l'aire de jeu afin d'initialiser le point de ralliement du vaisseau mère.",anchor = NW, fill = 'white', width = 200)
            #self.Actionmenu.create_text("Cliquer sur un endroit dans le jeu afin de mettre en place votre point de ralliement")

    def createUnitsConstructionPanel(self):
        self.unitsConstructionPanel.delete(ALL)
        y = 5;
        ok = False;
        l = None;
        r = 1
        list = self.parent.players[self.parent.playerId].motherShip.unitBeingConstruct
        for i in list:
            if(list.index(i) != 0):
                if (list[list.index(i)].name == list[list.index(i) - 1].name):
                    ok = True
                    r += 1
                else:
                    r = 1
                    ok = False
                    self.unitsConstructionPanel.create_image(175,5 + y, image = self.iconCancel, anchor = NW, tags = ('cancelUnitButton', list.index(i)))
            else:
                if (self.wantToCancelUnitBuild == False):
                    self.unitsConstructionPanel.create_arc((175, 5, 195, 25), start=0, extent= (i.constructionProgress / i.buildTime)*360 , fill='blue', tags = 'arc')
                else:
                    self.unitsConstructionPanel.create_image(175,5, image = self.iconCancel, anchor = NW, tags = ('cancelUnitButton', list.index(i)))

            if (ok == True):
                self.unitsConstructionPanel.itemconfig(l, text = str(r) + " " + i.name)
            else:
                l = self.unitsConstructionPanel.create_text(5,y,text = str(r) + " " + i.name, anchor = NW, fill = 'white')
                y+=20

	#Frame du menu principal    
    def fMainMenu(self):
        mainMenuFrame = Frame(self.root, bg="black")
        panel1 = Label(mainMenuFrame, image=self.mainMenuBG)
        panel1.grid(row=0, column=0, rowspan=10)
        Button(mainMenuFrame, text='Créer une partie', command=lambda:self.changeFrame(self.createServer)).grid(row=7, column=0)
        Button(mainMenuFrame, text='Rejoindre une partie', command=lambda:self.changeFrame(self.joinGame)).grid(row=8, column=0)
        return mainMenuFrame
    
    #Frame permettant de rejoindre une partie
    def fJoinGame(self):
        joinGameFrame = Frame(self.root, bg="black")
        Label(joinGameFrame, text="Nom de joueur:", fg="white", bg="black").grid(row=0, column=0)
        self.entryLogin = Entry(joinGameFrame, width=20)
        self.entryLogin.focus_set()
        self.entryLogin.grid(row=0, column=1)
        Label(joinGameFrame, text="Adresse du serveur:", fg="white", bg="black").grid(row=1, column=0)
        self.entryServer = Entry(joinGameFrame, width=20)
        self.entryServer.grid(row=1, column=1)
        widget = Button(joinGameFrame, text='Connecter', command=lambda:self.lobbyEnter(0, self.entryLogin.get(), self.entryServer.get()))
        widget.grid(row=2, column=1)
		#Crée un bouton de retour au menu principal
        widget = Button(joinGameFrame, text='Retour', command=lambda:self.changeFrame(self.mainMenu), width=10)
        widget.grid(row=3, column=1, columnspan=2, pady=10)
        self.entryServer.bind("<Return>",self.lobbyEnter)
        return joinGameFrame
    
    #Frame de création de nouveau serveur
    def fCreateServer(self):
        #Crée le frame
        createServerFrame = Frame(self.root, bg="black")
        #Crée le label de l'IP du serveur
        Label(createServerFrame, text="Adresse du serveur:", fg="white", bg="black").grid(row=0, column=0)
        #Crée le champ texte pour l'IP du serveur
        self.entryCreateServer = Entry(createServerFrame, width=20)
        #On met l'adresse de l'hôte comme valeur par défaut
        self.entryCreateServer.insert(0,self.parent.playerIp)
        self.entryCreateServer.grid(row=0, column=1)
        #Crée le label du nom du joueur
        Label(createServerFrame, text="Nom de joueur:", fg="white", bg="black").grid(row=1, column=0)
        #Crée le champ texte pour le nom du joueur
        self.entryCreateLogin = Entry(createServerFrame, width=20)
        self.entryCreateLogin.focus_set()
        self.entryCreateLogin.grid(row=1, column=1)
        #Crée le bouton de confirmation
        widget = Button(createServerFrame, text='Créer', command=lambda:self.startServer(False))
        widget.grid(row=2, column=1)
        #Crée le bouton de confirmation et se connecte
        widget = Button(createServerFrame, text='Créer et connecter', command=lambda:self.startServer(True))
        widget.grid(row=3, column=1)
		#Crée un bouton de retour au menu principal
        widget = Button(createServerFrame, text='Retour', command=lambda:self.changeFrame(self.mainMenu), width=10)
        widget.grid(row=5, column=1, columnspan=2, pady=10)
        return createServerFrame

    def startServer(self, connect):
        serverAddress= self.entryCreateServer.get()
        #Démarre le serveur dans un autre processus avec l'adresse spécifiée
        child = subprocess.Popen("C:\python32\python.exe server.py " + serverAddress, shell=True)
        #On vérifie si le serveur s'est terminé en erreur et si oui, on affiche un message à l'utilisateur
        if child.poll():
            if child.returncode != None:
                child.terminate()
                self.serverNotCreated()
        else:
            self.serverCreated(serverAddress)
            #Si l'usager veut se connecter en créant le serveur, on le connecte
            if connect:
                self.parent.connectServer(self.entryCreateLogin.get(), self.entryCreateServer.get())
            else:
                self.changeFrame(self.mainMenu)

    
    #Frame du lobby
    def fLobby(self):
        self.entryServer.unbind("<Return>")
        lobbyFrame = Frame(self.root, bg="black")
        if self.parent.server != None:
            pNum = len(self.parent.server.getSockets())
            for i in range(0, pNum):
                Label(lobbyFrame, text=self.parent.server.getSockets()[i][1], fg="white", bg="black").grid(row=i,column=0)
            Label(lobbyFrame, text='Admin : '+self.parent.server.getSockets()[0][1], fg="white", bg="black").grid(row=37, column=1)
            if self.parent.playerId == 0:
                Button(lobbyFrame, text='Demarrer la partie', command=self.parent.startGame, bg="black", fg="white").grid(row=38, column=1)
        self.chatLobby = Label(lobbyFrame, anchor=W, justify=LEFT, width=45, background='black', fg='white', relief='raised')
        self.chatLobby.grid(row=39, column=1)
        self.entryMessLobby = Entry(lobbyFrame, width=35)
        self.entryMessLobby.grid(row=40, column=1)
        self.entryMessLobby.bind("<Return>", self.sendMessLobby)
        #Choix de couleur
        self.variableColor = StringVar(lobbyFrame)
        listOfColors = self.parent.server.getColorChoices()
        self.colorOPTIONS = ["Orange","Rouge","Bleu"]
        self.variableColor.set(self.colorOPTIONS[0]) # default value
        self.colorChoice = OptionMenu(lobbyFrame, self.variableColor, *self.colorOPTIONS, command=self.parent.choiceColor)
        self.colorChoice.grid(row=(self.parent.playerId), column=1)
        self.colorChoice['menu'].delete(0, END)
        for i in listOfColors:
            if i[1] == False or self.parent.server.getSockets()[self.parent.playerId][3] == listOfColors.index(i):
                self.colorChoice['menu'].add_command(label=i[0], command=lambda temp = i[0]: self.colorChoice.setvar(self.colorChoice.cget("textvariable"), value = temp))
        self.variableColor.trace('w',self.parent.choiceColor)
        return lobbyFrame

    def redrawLobby(self ,lobbyFrame):
        listOfColors = self.parent.server.getColorChoices()
        self.colorChoice['menu'].delete(0, END)
        for i in listOfColors:
            if i[1] == False or self.parent.server.getSockets()[self.parent.playerId][3] == listOfColors.index(i):
                self.colorChoice['menu'].add_command(label=i[0], command=lambda temp = i[0]: self.colorChoice.setvar(self.colorChoice.cget("textvariable"), value = temp))
        if self.parent.server != None:
            pNum = len(self.parent.server.getSockets())
            for i in range(0, pNum):
                Label(lobbyFrame, text=self.parent.server.getSockets()[i][1], fg="white", bg="black").grid(row=i,column=0)
                if self.parent.server.getSockets()[i][3] != -1 and i != self.parent.playerId:
                    Label(lobbyFrame, text=self.parent.server.getColorChoices()[self.parent.server.getSockets()[i][3]][0], fg="white", bg="black").grid(row=i, column=1)
                
    def sendMessLobby(self, eve):
        if self.entryMessLobby.get() != "":
            self.parent.sendMessageLobby(self.entryMessLobby.get(), self.parent.server.getSockets()[self.parent.playerId][1])
            self.entryMessLobby.delete(0,END)
     
        
    def loginFailed(self):
        mb.showinfo('Erreur de connection', 'Le serveur est introuvable. Veuillez reessayer.')

    def colorAlreadyChosen(self):
        mb.showinfo('Trop tard!', 'La couleur sélectionnée a déjà été choisie.')

    def gameHasBeenStarted(self):
        mb.showinfo('Erreur de connection', 'La partie a déjà débutée. Veuillez attendre sa fin.')
    
    def showGameIsFinished(self):
        mb.showinfo('Fin de la partie', 'L\'administrateur de la partie a quitté prématurément la partie, la partie est donc terminée.')

    def serverCreated(self, serverIP):
        mb.showinfo('Serveur créé', 'Le serveur a été créé à l\'adresse ' + serverIP + '.')
        
    def serverNotCreated(self):
        mb.showinfo('Serveur non créé', 'Une erreur est survenue lors de la création du serveur.\nVeuillez vérifier que les informations entrées sont exactes.')
    
    #Methode pour dessiner la vue d'un planete
    def drawPlanetGround(self, planet):
        self.gameArea.delete('deletable')
        for i in planet.minerals:
            if i in self.parent.players[self.parent.playerId].selectedObjects:
                self.gameArea.create_text(i.position[0], i.position[1]-40, fill="cyan", text="Mineral :" + str(i.nbMinerals), tag='deletable')
                self.gameArea.create_oval(i.position[0]-(i.WIDTH/2+3), i.position[1]-(i.HEIGHT/2+3), i.position[0]+(i.WIDTH/2+3), i.position[1]+(i.HEIGHT/2+3), outline='yellow', tag='deletable')
            self.gameArea.create_image(i.position[0], i.position[1], image=self.mineral, tag='deletable')
        for i in planet.gaz:
            if i in self.parent.players[self.parent.playerId].selectedObjects:
                self.gameArea.create_text(i.position[0], i.position[1]-20, fill="green", text="Mineral :" + str(i.nbGaz), tag='deletable')
                self.gameArea.create_oval(i.position[0]-(i.WIDTH/2+3), i.position[1]-(i.HEIGHT/2+3), i.position[0]+(i.WIDTH/2+3), i.position[1]+(i.HEIGHT/2+3), outline='yellow', tag='deletable')
            self.gameArea.create_oval(i.position[0]-(i.WIDTH/2+2), i.position[1]-(i.HEIGHT/2+2), i.position[0]+(i.WIDTH/2+2), i.position[1]+(i.HEIGHT/2+2), fill='green', tag='deletable')
        for i in planet.landingZones:
            if i in self.parent.players[self.parent.playerId].selectedObjects:
                self.gameArea.create_oval(i.position[0]-(i.WIDTH/2+3),i.position[1]-(i.HEIGHT/2+3),i.position[0]+(i.WIDTH/2+3),i.position[1]+(i.HEIGHT/2+3), outline='green', tag='deletable')
            self.gameArea.create_image(i.position[0], i.position[1], image=self.landingZones[i.ownerId], tag='deletable')
            if i.LandedShip != None:
                self.gameArea.create_image(i.position[0]+1, i.position[1], image=self.landedShips[i.ownerId], tag='deletable')
        for i in planet.units:
            self.gameArea.create_oval(i.position[0]-12, i.position[1]-12, i.position[0]+12,i.position[1]+12, fill='red', tag='deletable')

    def changeBackground(self, type):
        self.gameArea.delete('background')
        if type == 'PLANET':
            self.gameArea.create_image(0,0,image=self.planetBackground, anchor=NW, tag='background')		
        else:
            self.gameArea.create_image(0,0,image=self.galaxyBackground, anchor=NW, tag='background')

    #Methode pour dessiner la galaxie
    def drawWorld(self):
        self.gameArea.delete('deletable')
        sunList = self.parent.galaxy.solarSystemList
        players = self.parent.players 
        id = self.parent.playerId
        for i in sunList:
            if self.parent.players[self.parent.playerId].inViewRange(i.sunPosition):
                if not i.discovered:
                    i.discovered = True
                    self.redrawMinimap()
                self.drawSun(i.sunPosition, players[id], True)
            else:
                if i.discovered:
                    self.drawSun(i.sunPosition, players[id], False)
            for j in i.planets:
                if self.parent.players[self.parent.playerId].inViewRange(j.position) or j.alreadyLanded(id):
                    if not j.discovered:
                        j.discovered = True
                        self.redrawMinimap()
                    self.drawPlanet(j, players[id], True)
                else:
                    if j.discovered:
                        self.drawPlanet(j, players[id], False)
            for j in i.nebulas:
                if self.parent.players[self.parent.playerId].inViewRange(j.position):
                    if not j.discovered:
                        j.discovered = True
                        self.redrawMinimap()
                    self.drawNebula(j, players[id], True)
                else:
                    if j.discovered:
                        self.drawNebula(j, players[id], False)
            for j in i.asteroids:
                if self.parent.players[self.parent.playerId].inViewRange(j.position):
                    if not j.discovered:
                        j.discovered = True
                        self.redrawMinimap()
                    self.drawAsteroid(j, players[id], True)
                else:
                    if j.discovered:
                        self.drawAsteroid(j, players[id], False)
        for i in players:
            for j in i.units:
                if j.isAlive:
                    if self.parent.players[self.parent.playerId].inViewRange(j.position):
                        if j.type == j.MOTHERSHIP:
                            j.discovered = True
                        self.drawUnit(j, i, False)
        if self.dragging:
            self.drawSelectionBox()
        self.drawMinimap()
        self.createActionMenu(self.actionMenuType)
        
    #Pour dessiner un soleil     
    def drawSun(self, sunPosition, player, isInFOW):
        if player.camera.isInFOV(sunPosition):
            distance = player.camera.calcDistance(sunPosition)
            if isInFOW:
                self.gameArea.create_image(distance[0],distance[1], image=self.sun, tag='deletable')
            else:
                self.gameArea.create_image(distance[0],distance[1], image=self.sunFOW, tag='deletable')
    
    #pour dessiner une planete        
    def drawPlanet(self, planet, player, isInFOW):
        planetPosition = planet.position
        if player.camera.isInFOV(planetPosition):
            distance = player.camera.calcDistance(planetPosition)
            if isInFOW:
                if planet in player.selectedObjects:
                    if planet.alreadyLanded(player.id):
                        self.gameArea.create_oval(distance[0]-(planet.IMAGE_WIDTH/2+3), distance[1]-(planet.IMAGE_HEIGHT/2+3), distance[0]+(planet.IMAGE_WIDTH/2+3), distance[1]+(planet.IMAGE_HEIGHT/2+3),outline="green", tag='deletable')
                    else:
                        self.gameArea.create_oval(distance[0]-(planet.IMAGE_WIDTH/2+3), distance[1]-(planet.IMAGE_HEIGHT/2+3), distance[0]+(planet.IMAGE_WIDTH/2+3), distance[1]+(planet.IMAGE_HEIGHT/2+3),outline="yellow", tag='deletable')
                    mVariable = "Mineral :" + str(planet.mineralQte)
                    gVariable = "Gaz :" + str(planet.gazQte)
                    self.gameArea.create_text(distance[0], distance[1]-25,fill="cyan",text=mVariable, tag='deletable')
                    self.gameArea.create_text(distance[0], distance[1]-40,fill="green",text=gVariable, tag='deletable')
                self.gameArea.create_image(distance[0],distance[1],image=self.planet, tag='deletable')
            else:
                self.gameArea.create_image(distance[0], distance[1], image=self.planetFOW, tag='deletable')

    def drawNebula(self,nebula,player, isInFOW):
        nebulaPosition = nebula.position
        if nebula.gazQte > 0:
            if player.camera.isInFOV(nebulaPosition):
                distance = player.camera.calcDistance(nebulaPosition)
                if isInFOW:
                    if nebula in player.selectedObjects:
                        self.gameArea.create_oval(distance[0]-(nebula.NEBULA_WIDTH/2+3), distance[1]-(nebula.NEBULA_HEIGHT/2+3), distance[0]+(nebula.NEBULA_WIDTH/2+3), distance[1]+(nebula.NEBULA_HEIGHT/2+3),outline="yellow", tag='deletable')
                        mVariable = "Gaz :" + str(nebula.gazQte)
                        self.gameArea.create_text(distance[0], distance[1]-25,fill="green",text=mVariable, tag='deletable')
                    self.gameArea.create_image(distance[0],distance[1],image=self.nebula, tag='deletable')
                else:
                    self.gameArea.create_image(distance[0], distance[1], image=self.nebulaFOW, tag='deletable')

    def drawAsteroid(self,asteroid,player, isInFOW):
        asteroidPosition = asteroid.position
        if asteroid.mineralQte > 0:
            if player.camera.isInFOV(asteroidPosition):
                distance = player.camera.calcDistance(asteroidPosition)
                if isInFOW:
                    if asteroid in player.selectedObjects:
                        self.gameArea.create_oval(distance[0]-(asteroid.ASTEROID_WIDTH/2+3), distance[1]-(asteroid.ASTEROID_HEIGHT/2+3), distance[0]+(asteroid.ASTEROID_WIDTH/2+3), distance[1]+(asteroid.ASTEROID_HEIGHT/2+3),outline="yellow", tag='deletable')
                        mVariable = "Mineral :" + str(asteroid.mineralQte)
                        self.gameArea.create_text(distance[0], distance[1]+25,fill="cyan",text=mVariable, tag='deletable')
                    self.gameArea.create_image(distance[0],distance[1],image=self.asteroid, tag='deletable')
                else:
                    self.gameArea.create_image(distance[0],distance[1],image=self.asteroidFOW, tag='deletable')
    
    #pour dessiner un vaisseau        
    def drawUnit(self, unit, player, isInFOW):
        unitPosition = unit.position
        if self.parent.players[self.parent.playerId].camera.isInFOV(unitPosition):
            distance = self.parent.players[self.parent.playerId].camera.calcDistance(unitPosition)
            if not isInFOW:
                if unit.type == unit.SCOUT:
                    if unit in player.selectedObjects:
                        self.gameArea.create_oval(distance[0]-(unit.SIZE[unit.type][0]/2+3),distance[1]-(unit.SIZE[unit.type][1]/2+3),distance[0]+(unit.SIZE[unit.type][0]/2+3),distance[1]+(unit.SIZE[unit.type][1]/2+3), outline="green", tag='deletable')
                    self.gameArea.create_image(distance[0], distance[1], image=self.scoutShips[player.id],tag='deletable')#On prend l'image dependamment du joueur que nous sommes
                if unit.type == unit.ATTACK_SHIP:
                    if unit.attackcount <= 5:
                        d2 = self.parent.players[self.parent.playerId].camera.calcDistance(unit.flag.finalTarget.position)
                        self.gameArea.create_line(distance[0],distance[1], d2[0], d2[1], fill="yellow", tag='deletable')
                    if unit in player.selectedObjects:
                        self.gameArea.create_oval(distance[0]-(unit.SIZE[unit.type][0]/2+3),distance[1]-(unit.SIZE[unit.type][1]/2+3),distance[0]+(unit.SIZE[unit.type][0]/2+3),distance[1]+(unit.SIZE[unit.type][1]/2+3), outline="green", tag='deletable')
                    self.gameArea.create_image(distance[0], distance[1], image=self.attackShips[player.id], tag='deletable')#On prend l'image dependamment du joueur que nous sommes
                elif unit.type == unit.MOTHERSHIP:
                    if unit in player.selectedObjects:
                        self.gameArea.create_oval(distance[0]-(unit.SIZE[unit.type][0]/2+3),distance[1]-(unit.SIZE[unit.type][1]/2+3),distance[0]+(unit.SIZE[unit.type][0]/2+3),distance[1]+(unit.SIZE[unit.type][1]/2+3), outline="green", tag='deletable')
                    self.gameArea.create_image(distance[0], distance[1], image = self.motherShips[player.id], tag='deletable')
                elif unit.type == unit.TRANSPORT:
                    if not unit.landed:
                        if unit in player.selectedObjects:
                            self.gameArea.create_oval(distance[0]-(unit.SIZE[unit.type][0]/2+3),distance[1]-(unit.SIZE[unit.type][1]/2+3),distance[0]+(unit.SIZE[unit.type][0]/2+3),distance[1]+(unit.SIZE[unit.type][1]/2+3), outline="green", tag='deletable')
                        self.gameArea.create_image(distance[0], distance[1], image = self.transportShips[player.id], tag='deletable')
                elif unit.type == unit.CARGO:
                    if unit in player.selectedObjects:
                        self.gameArea.create_oval(distance[0]-(unit.SIZE[unit.type][0]/2+3),distance[1]-(unit.SIZE[unit.type][1]/2+3),distance[0]+(unit.SIZE[unit.type][0]/2+3),distance[1]+(unit.SIZE[unit.type][1]/2+3), outline="green", tag='deletable')
                    self.gameArea.create_image(distance[0], distance[1], image = self.gatherShips[player.colorId], tag='deletable')
                if unit.hitpoints <= 5:
                    self.gameArea.create_image(distance[0], distance[1], image=self.explosion, tag='deletable')
                if self.hpBars:
                    self.drawHPBars(distance, unit)
                else:
                    self.drawHPHoverUnit(unit, distance)
     
    def drawHPHoverUnit(self, unit, distance):
        posSelected=self.parent.players[self.parent.playerId].camera.calcPointInWorld(self.positionMouse[0],self.positionMouse[1])
        if unit.position[0] >= posSelected[0]-(unit.SIZE[unit.type][0]/2) and unit.position[0] <= posSelected[0]+(unit.SIZE[unit.type][0]/2):
            if unit.position[1] >= posSelected[1]-(unit.SIZE[unit.type][1]/2) and unit.position[1] <= posSelected[1]+(unit.SIZE[unit.type][1]/2):
                if unit.type == unit.TRANSPORT:
                    if not unit.landed:
                        hpLeft=((unit.hitpoints/unit.MAX_HP[unit.type])*(unit.SIZE[unit.type][0]))-(unit.SIZE[unit.type][0])/2
                        hpLost=(hpLeft+(((unit.MAX_HP[unit.type]-unit.hitpoints)/unit.MAX_HP[unit.type])*(unit.SIZE[unit.type][0])))
                        self.gameArea.create_rectangle(distance[0]-(unit.SIZE[unit.type][0])/2,distance[1]-(unit.SIZE[unit.type][1]/2+5),distance[0]+hpLeft,distance[1]-(unit.SIZE[unit.type][1]/2+5), outline="green", tag='deletable')
                        if int(unit.hitpoints) != int(unit.MAX_HP[unit.type]):
                            self.gameArea.create_rectangle(distance[0]+hpLeft,distance[1]-(unit.SIZE[unit.type][1]/2+5),distance[0]+hpLost,distance[1]-(unit.SIZE[unit.type][1]/2+5), outline="red", tag='deletable')
                else:
                    hpLeft=((unit.hitpoints/unit.MAX_HP[unit.type])*(unit.SIZE[unit.type][0]))-(unit.SIZE[unit.type][0])/2
                    hpLost=(hpLeft+(((unit.MAX_HP[unit.type]-unit.hitpoints)/unit.MAX_HP[unit.type])*(unit.SIZE[unit.type][0])))
                    self.gameArea.create_rectangle(distance[0]-(unit.SIZE[unit.type][0])/2,distance[1]-(unit.SIZE[unit.type][1]/2+5),distance[0]+hpLeft,distance[1]-(unit.SIZE[unit.type][1]/2+5), outline="green", tag='deletable')
                    if int(unit.hitpoints) != int(unit.MAX_HP[unit.type]):
                        self.gameArea.create_rectangle(distance[0]+hpLeft,distance[1]-(unit.SIZE[unit.type][1]/2+5),distance[0]+hpLost,distance[1]-(unit.SIZE[unit.type][1]/2+5), outline="red", tag='deletable')
    
    def drawHPBars(self, distance, unit):
        if unit.type == unit.TRANSPORT:
            if not unit.landed:
                hpLeft=((unit.hitpoints/unit.MAX_HP[unit.type])*(unit.SIZE[unit.type][0]))-(unit.SIZE[unit.type][0])/2
                hpLost=(hpLeft+(((unit.MAX_HP[unit.type]-unit.hitpoints)/unit.MAX_HP[unit.type])*(unit.SIZE[unit.type][0])))
                self.gameArea.create_rectangle(distance[0]-(unit.SIZE[unit.type][0])/2,distance[1]-(unit.SIZE[unit.type][1]/2+5),distance[0]+hpLeft,distance[1]-(unit.SIZE[unit.type][1]/2+5), outline="green", tag='deletable')
                if int(unit.hitpoints) != int(unit.MAX_HP[unit.type]):
                    self.gameArea.create_rectangle(distance[0]+hpLeft,distance[1]-(unit.SIZE[unit.type][1]/2+5),distance[0]+hpLost,distance[1]-(unit.SIZE[unit.type][1]/2+5), outline="red", tag='deletable')
        else:
            hpLeft=((unit.hitpoints/unit.MAX_HP[unit.type])*(unit.SIZE[unit.type][0]))-(unit.SIZE[unit.type][0])/2
            hpLost=(hpLeft+(((unit.MAX_HP[unit.type]-unit.hitpoints)/unit.MAX_HP[unit.type])*(unit.SIZE[unit.type][0])))
            self.gameArea.create_rectangle(distance[0]-(unit.SIZE[unit.type][0])/2,distance[1]-(unit.SIZE[unit.type][1]/2+5),distance[0]+hpLeft,distance[1]-(unit.SIZE[unit.type][1]/2+5), outline="green", tag='deletable')
            if int(unit.hitpoints) != int(unit.MAX_HP[unit.type]):
                self.gameArea.create_rectangle(distance[0]+hpLeft,distance[1]-(unit.SIZE[unit.type][1]/2+5),distance[0]+hpLost,distance[1]-(unit.SIZE[unit.type][1]/2+5), outline="red", tag='deletable')
          
    #Dessine la minimap
    def drawMinimap(self):
        self.minimap.delete('deletable')
        sunList = self.parent.galaxy.solarSystemList
        players = self.parent.players
        if self.firstTime:
            for i in sunList:
                self.drawMiniSun(i)
                for j in i.planets:
                    self.drawMiniPlanet(j)
                for n in i.nebulas:
                    self.drawMiniNebula(n)
                for q in i.asteroids:
                    self.drawMiniAsteroid(q)
            self.firstTime = False
        for i in players:
            for j in i.units:
                if j.isAlive:
                    if players[self.parent.playerId].inViewRange(j.position):
                        self.drawMiniUnit(j)
        self.drawMiniFOV()
        
    def redrawMinimap(self):
        self.minimap.delete(ALL)
        sunList = self.parent.galaxy.solarSystemList
        players = self.parent.players
        for i in sunList:
            self.drawMiniSun(i)
            for j in i.planets:
                self.drawMiniPlanet(j)
            for n in i.nebulas:
                self.drawMiniNebula(n)
            for q in i.asteroids:
                self.drawMiniAsteroid(q)
        for i in players:
            for j in i.units:
                if j.isAlive:
                    if players[self.parent.playerId].inViewRange(j.position):
                        self.drawMiniUnit(j)
        self.drawMiniFOV()

    #Dessine le carrer de la camera dans la minimap    
    def drawMiniFOV(self):
        cameraX = (self.parent.players[self.parent.playerId].camera.position[0]-(self.taille/2) + self.parent.galaxy.width/2) / self.parent.galaxy.width * (self.taille/4)
        cameraY = (self.parent.players[self.parent.playerId].camera.position[1]-((self.taille/2)-self.taille/8) + self.parent.galaxy.height/2) / self.parent.galaxy.height * (self.taille/4)
        width = self.taille / self.parent.galaxy.width * (self.taille/4)
        height = self.taille / self.parent.galaxy.height * ((self.taille/16)*3)
        self.minimap.create_rectangle(cameraX, cameraY, cameraX+width, cameraY+height, outline='GREEN', tag='deletable')

    #Dessine un soleil dans la minimap    
    def drawMiniSun(self, sun):
        sunPosition = sun.sunPosition
        sunX = (sunPosition[0] + self.parent.galaxy.width/2) / self.parent.galaxy.width * (self.taille/4)
        sunY = (sunPosition[1] + self.parent.galaxy.height/2) / self.parent.galaxy.height * (self.taille/4)
        if sun.discovered:
            self.minimap.create_oval(sunX-3, sunY-3, sunX+3, sunY+3, fill='ORANGE')

    #Dessine une planete dans la minimap        
    def drawMiniPlanet(self, planet):
        planetPosition = planet.position
        planetX = (planetPosition[0] + self.parent.galaxy.width/2) / self.parent.galaxy.width * (self.taille/4)
        planetY = (planetPosition[1] + self.parent.galaxy.height/2) / self.parent.galaxy.height * (self.taille/4)
        if planet.discovered:
            self.minimap.create_oval(planetX-1, planetY-1, planetX+1, planetY+1, fill='LIGHT BLUE')
            
    #dessine une nebula dans la minimap
    def drawMiniNebula(self, nebula):
        if nebula.gazQte > 0:
            nebulaPosition = nebula.position
            nebulaX = (nebulaPosition[0] + self.parent.galaxy.width/2) / self.parent.galaxy.width * (self.taille/4)
            nebulaY = (nebulaPosition[1] + self.parent.galaxy.height/2) / self.parent.galaxy.height * (self.taille/4)
            if nebula.discovered:
                self.minimap.create_oval(nebulaX-1, nebulaY-1, nebulaX+1, nebulaY+1, fill='PURPLE')
        
    #dessine un asteroid dans la minimap
    def drawMiniAsteroid(self, asteroid):
        if asteroid.mineralQte > 0:
            asteroidPosition = asteroid.position
            asteroidX = (asteroidPosition[0] + self.parent.galaxy.width/2) / self.parent.galaxy.width * (self.taille/4)
            asteroidY = (asteroidPosition[1] + self.parent.galaxy.height/2) / self.parent.galaxy.height * (self.taille/4)
            if asteroid.discovered:
                self.minimap.create_oval(asteroidX-1, asteroidY-1, asteroidX+1, asteroidY+1, fill='CYAN')
        
    #Dessine une unite dans la minimap        
    def drawMiniUnit(self, unit):
        unitX = (unit.position[0] + self.parent.galaxy.width/2) / self.parent.galaxy.width * (self.taille/4)
        planetY = (unit.position[1] + self.parent.galaxy.height/2) / self.parent.galaxy.height * (self.taille/4)
        if unit.name != "Mothership":
            if unit in self.parent.players[self.parent.playerId].units:
                if unit.name == 'Transport':
                    if not unit.landed:
                        self.minimap.create_polygon((unitX-2, planetY+2, unitX, planetY-2, unitX+2, planetY+2),fill='GREEN', tag='deletable')
                else:
                    self.minimap.create_polygon((unitX-2, planetY+2, unitX, planetY-2, unitX+2, planetY+2),fill='GREEN', tag='deletable')
            else:
                self.minimap.create_polygon((unitX-2, planetY+2, unitX, planetY-2, unitX+2, planetY+2),fill='RED', tag='deletable')
        else:
            if unit in self.parent.players[self.parent.playerId].units:
                self.minimap.create_polygon((unitX-4, planetY+2, unitX, planetY-2, unitX+4, planetY+2),fill='WHITE', tag='deletable')
            else:
                self.minimap.create_polygon((unitX-4, planetY+2, unitX, planetY-2, unitX+4, planetY+2),fill='RED', tag='deletable')

    #Dessine la boite de selection lors du clic-drag	
    def drawSelectionBox(self):
        self.gameArea.create_rectangle(self.selectStart[0], self.selectStart[1], self.selectEnd[0], self.selectEnd[1], outline='WHITE', tag='deletable')

    #Actions quand on clic sur les fleches du clavier
    def keyPressUP(self, eve):
        if 'UP' not in self.parent.players[self.parent.playerId].camera.movingDirection:
            if self.parent.players[self.parent.playerId].currentPlanet == None:
                self.parent.players[self.parent.playerId].camera.movingDirection.append('UP')
                self.drawWorld()

    def keyPressDown(self, eve):
        if 'DOWN' not in self.parent.players[self.parent.playerId].camera.movingDirection:
            if self.parent.players[self.parent.playerId].currentPlanet == None:
                self.parent.players[self.parent.playerId].camera.movingDirection.append('DOWN')
                self.drawWorld()

    def keyPressLeft(self, eve):
        if 'LEFT' not in self.parent.players[self.parent.playerId].camera.movingDirection:
            if self.parent.players[self.parent.playerId].currentPlanet == None:
                self.parent.players[self.parent.playerId].camera.movingDirection.append('LEFT')
                self.drawWorld()

    def keyPressRight(self, eve):
        if 'RIGHT' not in self.parent.players[self.parent.playerId].camera.movingDirection:
            if self.parent.players[self.parent.playerId].currentPlanet == None:
                self.parent.players[self.parent.playerId].camera.movingDirection.append('RIGHT')
                self.drawWorld()

    #Actions quand on lache les touches
    def keyReleaseUP(self, eve):
        if self.parent.players[self.parent.playerId].currentPlanet == None:
            self.parent.players[self.parent.playerId].camera.movingDirection.remove('UP')
            self.drawWorld()

    def keyReleaseDown(self, eve):
        if self.parent.players[self.parent.playerId].currentPlanet == None:
            self.parent.players[self.parent.playerId].camera.movingDirection.remove('DOWN')
            self.drawWorld()

    def keyReleaseLeft(self, eve):
        if self.parent.players[self.parent.playerId].currentPlanet == None:
            self.parent.players[self.parent.playerId].camera.movingDirection.remove('LEFT')
            self.drawWorld()

    def keyReleaseRight(self, eve):
        if self.parent.players[self.parent.playerId].currentPlanet == None:
            self.parent.players[self.parent.playerId].camera.movingDirection.remove('RIGHT')
            self.drawWorld()

    #Actions avec la souris    
    def rightclic(self, eve):
        self.attacking = False
        x = eve.x
        y = eve.y
        canva = eve.widget
        if x > 0 and x < self.taille:
            if y > 0 and y < self.taille-200:
                if canva == self.gameArea:
                    pos = self.parent.players[self.parent.playerId].camera.calcPointInWorld(x,y)
                    self.parent.rightClic(pos)
                elif canva == self.minimap and self.parent.players[self.parent.playerId].currentPlanet == None:
                    pos = self.parent.players[self.parent.playerId].camera.calcPointMinimap(x,y)
                    self.parent.setMovingFlag(pos[0], pos[1])
                    self.drawWorld()

    #Quand on fait un clic gauche (peu importe ou)
    def leftclic(self, eve):
        x = eve.x
        y = eve.y
        canva = eve.widget
        if(self.isSettingRallyPointPosition == False):
            if canva == self.gameArea:
                if self.parent.players[self.parent.playerId].currentPlanet == None:
                    pos = self.parent.players[self.parent.playerId].camera.calcPointInWorld(x,y)
                    if self.attacking:
                        self.parent.setAttackFlag(pos[0],pos[1])
                    else:
                        if not self.selectAllUnits:
                            self.parent.select(pos)
                            self.ongletSelectedUnit()
                        else:
                            self.parent.selectAll(pos)
                            self.ongletSelectedUnit()
                else:
                    self.parent.select([x,y])
                    self.ongletSelectedUnit()
            elif canva == self.minimap:
                self.parent.quickMove(x,y,canva)
        else:
            pos = self.parent.players[self.parent.playerId].camera.calcPointInWorld(x,y)
            self.parent.setMotherShipRallyPoint(pos)
            self.isSettingRallyPointPosition = False
            self.actionMenuType = self.MAIN_MENU

    def selectAll(self, eve):
        self.selectAllUnits = True
    def unSelectAll(self, eve):
        self.selectAllUnits = False

    #Quand on fait un clic gauche et qu'on bouge
    def clicDrag(self,eve):
        self.attacking = False
        if self.dragging == False:
            self.selectStart = [eve.x, eve.y]
            self.selectEnd = [eve.x, eve.y]
            self.dragging = True
        else:
            self.selectEnd = [eve.x, eve.y]

    #Quand on clicDrag et qu'on lache la souris
    def endDrag(self, eve):
        self.attacking = False
        if self.dragging:
            self.dragging = False
            self.selectEnd = [eve.x, eve.y]
            self.parent.boxSelect(self.selectStart, self.selectEnd)
            self.ongletSelectedUnit()

    def posMouse(self, eve):
        self.positionMouse[0] = eve.x
        self.positionMouse[1] = eve.y
    
    def ctrlPressed(self, eve):
        self.hpBars=True
    
    def ctrlDepressed(self, eve):
        self.hpBars=False

    #methode test attack
    def attack(self,eve):
        self.attacking = True
        
    #Quand on appui sur enter dans le chat		
    def enter(self, eve):
        self.parent.sendMessage(self.menuModes.entryMess.get())
        self.menuModes.entryMess.delete(0,END)
        self.gameArea.focus_set()

    #Quand on appui sur enter dans le login
    def lobbyEnter(self, eve, login="", server=""):
        if login=="" and server=="":
            login = self.entryLogin.get()
            server = self.entryServer.get()
        self.parent.connectServer(login,server)
			
    def stop(self, eve):
        self.attacking = False
        self.parent.setStandbyFlag()

    def delete(self, eve):
        self.attacking = False
        self.parent.eraseUnit()
        
    #Pour la selection multiple	
    def shiftPress(self, eve):
        self.parent.multiSelect = True

    def shiftRelease(self, eve):
        self.parent.multiSelect = False
	
    def checkMotherSip(self, eve):
        self.parent.players[self.parent.playerId].currentPlanet = None
        self.changeBackground('GALAXY')
        self.drawWorld()
        cam = self.parent.players[self.parent.playerId].camera
        cam.position = cam.defaultPos

    def clickMenuModes(self,eve):
        bp = (eve.widget.gettags(eve.widget.find_withtag('current')))
        if bp != ():
            Button_pressed = bp[0]
            if (Button_pressed == "bouton_chat"):
                self.ongletChat(self.gameFrame)
            elif (Button_pressed == "bouton_trade"):
                self.ongletTrade()
            elif (Button_pressed == "bouton_team"):
                self.ongletTeam()
            elif (Button_pressed == "bouton_selectedUnit"):
                self.ongletSelectedUnit()

    def takeOff(self, eve):
        planet = self.parent.players[self.parent.playerId].currentPlanet
        if planet != None:
            for i in planet.landingZones:
                if i.ownerId == self.parent.playerId and i.LandedShip != None:
                    if i in self.parent.players[self.parent.playerId].selectedObjects:
                        self.parent.takeOff(i.LandedShip, planet)

    def clickActionMenu(self,eve):
        bp = (eve.widget.gettags(eve.widget.find_withtag('current')))
        if bp != ():
            Button_pressed = bp[0]
            if (Button_pressed == "Button_Stop"):
                self.parent.setStandbyFlag()
            elif (Button_pressed == "Button_RallyPoint"):
                self.actionMenuType = self.WAITING_FOR_RALLY_POINT_MENU
                self.isSettingRallyPointPosition = True
            elif (Button_pressed == "Button_Build"):
                self.actionMenuType = self.MOTHERSHIP_BUILD_MENU
            elif (Button_pressed == "Button_Build_Scout"):
                self.parent.addUnit(Unit.SCOUT)
            elif (Button_pressed == "Button_Build_Attack"):
                self.parent.addUnit(Unit.ATTACK_SHIP)
            elif (Button_pressed == "Button_Build_Transport"):
                self.parent.addUnit(Unit.TRANSPORT)
            elif (Button_pressed == "Button_Build_Gather"):
                self.parent.addUnit(Unit.CARGO)
                
    def progressCircleMouseOver(self,eve):
        #if(posX >= self.unitsConstructionPanel.find_withtag('current')):
        tag = self.unitsConstructionPanel.gettags(self.unitsConstructionPanel.find_withtag('current'))
        if tag != ():
            if tag[0] == 'arc':
                self.wantToCancelUnitBuild = True
        else:
            self.wantToCancelUnitBuild = False
            
    def clicCancelUnit(self,eve):
        tag = self.unitsConstructionPanel.gettags(self.unitsConstructionPanel.find_withtag('current'))
        if tag != ():
            if tag[0] == 'cancelUnitButton':
                self.parent.cancelUnit(tag[1])
    
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
        self.gameArea.bind("<Delete>", self.delete)
        #self.gameArea.bind("a",self.attack)
        #self.gameArea.bind("A",self.attack)
        self.gameArea.bind("c", self.selectAll)
        self.gameArea.bind("t", self.takeOff)
        self.gameArea.bind("T", self.takeOff)
        self.gameArea.bind("<KeyRelease-c>", self.unSelectAll)
        self.gameArea.bind("1", self.checkMotherSip)
        self.gameArea.bind("<Control_L>",self.ctrlPressed)
        self.gameArea.bind("<KeyRelease-Control_L>",self.ctrlDepressed)
        #Bindings des boutons de la souris
        self.unitsConstructionPanel.bind("<Motion>", self.progressCircleMouseOver)
        self.unitsConstructionPanel.bind("<Button-1>", self.clicCancelUnit)
        self.gameArea.bind("<Button-3>", self.rightclic)
        self.gameArea.bind("<B3-Motion>", self.rightclic)
        self.minimap.bind("<Button-3>", self.rightclic)
        self.gameArea.bind("<Button-1>", self.leftclic)
        self.minimap.bind("<B1-Motion>",self.leftclic)
        self.minimap.bind("<Button-1>",self.leftclic)
        self.gameArea.bind("<B1-Motion>", self.clicDrag)
        self.gameArea.bind("<ButtonRelease-1>", self.endDrag)
        self.gameArea.bind("<Motion>", self.posMouse)
        self.menuModes.entryMess.bind("<Return>",self.enter)
        self.menuModes.bind("<Button-1>",self.clickMenuModes)
        self.Actionmenu.bind("<Button-1>", self.clickActionMenu)

