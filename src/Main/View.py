# -*- coding: UTF-8 -*-
from tkinter import *
from Unit import *
from World import *
import time
import Building as b
from winsound import *
import tkinter.messagebox as mb



class View():
    ACTIONMENU_ICON_WIDTH=37
    ACTIONMENU_ICON_HEIGHT=34
    MAIN_MENU=1
    WAITING_FOR_RALLY_POINT_MENU=2
    MOTHERSHIP_BUILD_MENU=3
    WAITING_FOR_MOVE_POINT_MENU=4
    WAITING_FOR_ATTACK_POINT_MENU=5
    WAITING_FOR_PATROL_POINT_MENU=6
    WAITING_FOR_BUILDING_POINT_MENU=7
    UNIT_BUILD_MENU=8
    TECHNOLOGY_TREE_MENU = 9
    TECHTREE_UNIT_MENU = 10
    TECHTREE_BUILDING_MENU = 11
    TECHTREE_MOTHERSHIP_MENU = 12
    MINIMAP_WIDTH=200
    MINIMAP_HEIGHT=200
    SELECTED_TRADE = 20
    SELECTED_CHAT = 21
    SELECTED_UNIT_SELECTED = 22
    SELECTED_TEAM = 23
    SELECTED_UNIT = 24
        
    def __init__(self, parent, game):
        self.parent = parent
        self.game = game
        self.root=Tk()
        self.root.title("Orion")
        self.root.resizable(0,0)
        #la taille du jeu se resize selon la résolution de l'écran, niceshithum?
        #self.taille=self.root.winfo_screenheight()-125
        #if self.taille>800:
        self.taille=1200
        self.root.geometry('+5+5')
        self.selectStart = [0,0]
        self.selectEnd = [0,0]
        self.positionMouse = [0,0,0]
        self.sun=PhotoImage(file='images/Galaxy/sun.gif')
        self.sunFOW = PhotoImage(file='images/Galaxy/sunFOW.gif')
        self.planet=PhotoImage(file='images/Galaxy/planet.gif')
        self.planetFOW = PhotoImage(file='images/Galaxy/planetFOW.gif')
        self.nebula=PhotoImage(file='images/Galaxy/nebula.gif')
        self.nebulaFOW=PhotoImage(file='images/Galaxy/nebulaFOW.gif')
        self.explosion=PhotoImage(file='images/explosion.gif')
        self.asteroid=PhotoImage(file='images/Galaxy/asteroid.gif')
        self.asteroidFOW=PhotoImage(file='images/Galaxy/asteroidFOW.gif')
        self.mineral = PhotoImage(file='images/Planet/crystal.gif')
        self.gaz = PhotoImage(file='images/Planet/gaz.gif')
        self.nuclear = PhotoImage(file='images/Planet/rad.gif')
        self.planetBackground = PhotoImage(file='images/Planet/background.gif')
        self.galaxyBackground = PhotoImage(file='images/Galaxy/night-sky.gif')
        self.lobbyBackground = PhotoImage(file='images/Menus/lobby.gif')
        self.mainMenuBG = PhotoImage(file='images/Menus/MainMenuBG.gif')
        self.gifStop = PhotoImage(file='images/icones/stop.gif')
        self.gifMove = PhotoImage(file='images/icones/move.gif')
        self.gifAttack = PhotoImage(file='images/icones/attack.gif')
        self.gifAttackUnit = PhotoImage(file='images/icones/attackUnit.gif')
        self.gifRallyPoint = PhotoImage(file='images/icones/flag.gif')
        self.gifBuild = PhotoImage(file = 'images/icones/build.gif')
        self.gifTechTree = PhotoImage(file = 'images/icones/delete.gif')
        self.gifConstruction = PhotoImage(file='images/Building/construction.gif')        
        self.gifCadreMenuAction = PhotoImage(file = 'images/Menus/cadreMenuAction.gif')
        self.iconCancel = PhotoImage(file = 'images/icones/cancelUnit.gif')
        self.gifPatrol = PhotoImage(file='images/icones/patrol.gif')
        self.gifChat = PhotoImage(file='images/icones/boutonChat.gif')
        self.gifTrade = PhotoImage(file='images/icones/boutonTrade.gif')
        self.gifTeam = PhotoImage(file='images/icones/boutonTeam.gif')
        self.gifTransport = PhotoImage(file='images/icones/transport.gif')
        self.gifCargo = PhotoImage(file='images/icones/cargo.gif')
        self.gifUnit = PhotoImage(file='images/icones/scout.gif')
        self.gifSelectedUnit = PhotoImage(file='images/icones/boutonSelectedUnit.gif')
        self.gifTriangle = PhotoImage(file='images/icones/iconeFormationTriangle.gif')
        self.gifSquare = PhotoImage(file='images/icones/iconeFormationCarre.gif')
        self.gifReturn = PhotoImage(file='images/icones/return.gif')
        #fenetres
        self.mainMenu = self.fMainMenu()
        self.mainMenu.pack()
        self.pLobby = None
        self.currentFrame = self.mainMenu
        self.gameFrame = None
        self.joinGame = self.fJoinGame()
        self.createServer = self.fCreateServer()
        self.actionMenuType = self.MAIN_MENU
        self.Actionmenu = None
        self.unitsConstructionPanel = None
        #booleens d'actions
        self.firstTime = True
        self.attacking = False
        self.building = False
        self.selectAllUnits = False
        self.wantToCancelUnitBuild = False
        self.isSettingPatrolPosition = False
        self.isSettingRallyPointPosition = False
        self.isSettingMovePosition = False
        self.isSettingAttackPosition = False
        self.isSettingBuildingPosition = False
        self.dragging = False
        self.hpBars=False
        # Quand le user ferme la fenêtre et donc le jeu, il faut l'enlever du serveur
        self.root.protocol('WM_DELETE_WINDOW', self.parent.sendKillPlayer)
        self.selectedOnglet = self.SELECTED_CHAT

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
        self.waypoints = []
        self.landingZones = []
        self.groundUnits = []
        for i in range(0,8):
            self.scoutShips.append(PhotoImage(file='images/Ships/Scoutships/Scoutship'+str(i)+'.gif'))
            self.attackShips.append(PhotoImage(file='images/Ships/Attackships/Attackship'+str(i)+'.gif'))
            self.motherShips.append(PhotoImage(file='images/Ships/Motherships/Mothership'+str(i)+'.gif'))
            self.transportShips.append(PhotoImage(file='images/Ships/Transport/Transport'+str(i)+'.gif'))
            self.landedShips.append(PhotoImage(file='images/Planet/LandedShips/landed'+str(i)+'.gif'))
            self.gatherShips.append(PhotoImage(file='images/Ships/Cargo/Cargo'+str(i)+'.gif'))
            self.landingZones.append(PhotoImage(file='images/Planet/LandingZones/landing'+str(i)+'.gif'))
            self.waypoints.append(PhotoImage(file='images/Building/waypoint'+str(i)+'.gif'))
            self.groundUnits.append(PhotoImage(file='images/Planet/GroundUnit/ground'+str(i)+'.gif'))
        self.showMinerals = Label(gameFrame, text="Mineraux: "+str(self.game.players[self.game.playerId].ressources[0]), bg="black", fg="white", anchor=E)
        self.showMinerals.grid(column=2, row=0)
        self.showGaz = Label(gameFrame, text="Gaz: "+str(self.game.players[self.game.playerId].ressources[1]), bg="black", fg="white", anchor=E)
        self.showGaz.grid(column=3, row=0)
        self.gameArea=Canvas(gameFrame, width=self.taille, height=self.taille/2, background='Black', relief='ridge')
        self.gameArea.grid(column=0,row=1, columnspan=24)#place(relx=0, rely=0,width=taille,height=taille)
        self.minimap= Canvas(gameFrame, width=200,height=200, background='Black', relief='raised')
        self.minimap.grid(column=0,row=2, rowspan=5)
        self.menuModes=Canvas(gameFrame, width=800, height=200, background='black', relief='ridge')
        self.menuModes.grid(row=2,column=2, rowspan=5, columnspan=5)
        #OngletChat
        self.menuModes.chat = Label(gameFrame, anchor=W, justify=LEFT, width=75, background='black', fg='white', relief='raised')
        self.menuModes.entryMess = Entry(gameFrame, width=60)
        #Fenetres trade
        self.menuModes.variableTrade = StringVar(gameFrame)
        self.menuModes.tradeOPTIONS = []
        for i in self.game.players:
            self.menuModes.tradeOPTIONS.append(i.name)
        self.menuModes.variableTrade.set(self.menuModes.tradeOPTIONS[0])
        self.menuModes.tradeChoice = OptionMenu(gameFrame, self.menuModes.variableTrade, *self.menuModes.tradeOPTIONS, command=self.parent.askTrade)
        self.answerId=0
        self.answerId2=0
        self.menuModes.yesButton = Button(gameFrame, text="Oui", command=lambda:self.parent.startTrade(True, self.answerId))
        self.menuModes.noButton = Button(gameFrame, text="Non", command=lambda:self.parent.startTrade(False, self.answerId))
        self.menuModes.yesButtonConfirm = Button(gameFrame, text="Oui", command=lambda:self.parent.confirmTrade(True, self.answerId, min1, min2, gaz1, gaz2))
        self.menuModes.noButtonConfirm = Button(gameFrame, text="Non", command=lambda:self.parent.confirmTrade(False, self.answerId, min1, min2, gaz1, gaz2))
        self.menuModes.modifyButtonConfirm = Button(gameFrame, text="Contre-offre", command=lambda:self.parent.startTrade(True,self.game.playerId))
        self.menuModes.nomJoueur1 = Label(gameFrame, text=self.game.players[self.answerId].name, bg="black", fg="white")
        self.menuModes.etiqMenieral1 = Label(gameFrame,text='Minerals ', bg="black", fg="white")
        self.menuModes.etiqGaz1 = Label(gameFrame,text='Gaz ', bg="black", fg="white")
        self.menuModes.nomJoueur2 = Label(gameFrame, text=self.game.players[self.answerId2].name, bg="black", fg="white")
        self.menuModes.etiqMenieral2 = Label(gameFrame,text='Minerals ', bg="black", fg="white")
        self.menuModes.bEchange = Button(gameFrame,text="Échange",command=lambda:self.parent.confirmTradeQuestion(self.answerId2))
        self.menuModes.etiqGaz2 = Label(gameFrame,text='Gaz ', bg="black", fg="white")
        self.menuModes.spinMinerals1 = Spinbox(gameFrame, from_=0, to=self.game.players[self.answerId].ressources[0])
        self.menuModes.spinGaz1 = Spinbox(gameFrame, from_=0, to=self.game.players[self.answerId].ressources[1])
        self.menuModes.spinMinerals2 = Spinbox(gameFrame, from_=0, to=self.game.players[self.answerId2].ressources[0])
        self.menuModes.spinGaz2 = Spinbox(gameFrame, from_=0, to=self.game.players[self.answerId2].ressources[1])
        #Fenetre Team
        self.menuModes.listAllies = Listbox(gameFrame, width=40, height=7, background='black', fg='white', relief='raised', selectmode=BROWSE)
        self.menuModes.listEnnemies = Listbox(gameFrame, width=40, height=7, background='black', fg='white', relief='raised', selectmode=BROWSE)
        self.menuModes.labelAlly = Label(gameFrame, background='black', fg='Green', text="Alliés", font="Arial 12 bold")
        self.menuModes.labelEnnemy = Label(gameFrame, background='black', fg='Red', text="Ennemis", font="Arial 12 bold")
        self.menuModes.toAllyButton = Button(gameFrame, text="<", command=self.changeToAlly)
        self.menuModes.toEnnemyButton = Button(gameFrame, text=">", command=self.changeToEnnemy)
        self.menuModes.create_image(0,0,image=self.gifChat,anchor = NW,tag='bouton_chat')
        self.menuModes.create_image(77,0,image=self.gifTrade,anchor = NW,tag='bouton_trade')
        self.menuModes.create_image(150,0,image=self.gifTeam,anchor = NW,tag='bouton_team')
        self.menuModes.create_image(227,0,image=self.gifSelectedUnit,anchor = NW,tag='bouton_selectedUnit')
        #ActionMenu
        self.Actionmenu = Canvas(gameFrame,width=200,height=200,background='black')
        self.Actionmenu.grid(column=7,row=2, rowspan=5)
        self.changeBackground('GALAXY')
        self.drawWorld()
        self.createActionMenu(self.MAIN_MENU)
        self.ongletChat(gameFrame)
        self.assignControls()
        return gameFrame

    def ongletTeam(self):
        self.menuModesOnlets()
        self.selectedOnglet = self.SELECTED_TEAM
        self.menuModes.labelAlly.grid(row=3, column=3)
        self.menuModes.labelEnnemy.grid(row=3, column=5)
        self.menuModes.listAllies.grid(row=4, rowspan=2, column=3)
        self.menuModes.listEnnemies.grid(row=4, rowspan=2, column=5)
        self.menuModes.toAllyButton.grid(row=4, column=4)
        self.menuModes.toEnnemyButton.grid(row=5, column=4)
        self.fillListsAllies()
                    
    def fillListsAllies(self):
        for i in range(len(self.game.players)):
            if i != self.game.playerId:
                if self.game.isAllied(self.game.playerId, i):
                    if self.game.isAllied(i, self.game.playerId):
                        self.menuModes.listAllies.insert(END,self.game.players[i].name)
                    else:
                        self.menuModes.listAllies.insert(END,self.game.players[i].name + ' ?')
                else:
                    self.menuModes.listEnnemies.insert(END,self.game.players[i].name)
                    
    def changeToAlly(self):
        self.gameArea.focus_set()
        selected = self.menuModes.listEnnemies.curselection()
        if len(selected) > 0:
            playerName = self.menuModes.listEnnemies.get(selected)
            playerId = self.game.getPlayerId(playerName)
            if self.game.isAllied(playerId, self.game.playerId):
                self.menuModes.listAllies.insert(END, self.menuModes.listEnnemies.get(selected))
            else:
                self.menuModes.listAllies.insert(END, self.menuModes.listEnnemies.get(selected) +  ' ?')
            self.menuModes.listEnnemies.delete(int(selected[0]))
            self.parent.changeAlliance(playerId, "Ally")
        
    def changeToEnnemy(self):
        self.gameArea.focus_set()
        selected = self.menuModes.listAllies.curselection()
        if len(selected) > 0:
            playerName = self.menuModes.listAllies.get(selected)
            playerName = playerName.replace(" ?", "")
            playerId = self.game.getPlayerId(playerName)
            self.menuModes.listEnnemies.insert(END, playerName)
            self.menuModes.listAllies.delete(int(selected[0]))
            self.parent.changeAlliance(playerId, "Ennemy")
            
    def refreshAlliances(self):
        if self.selectedOnglet == self.SELECTED_TEAM:
            self.menuModes.listAllies.delete(0, END)
            self.menuModes.listEnnemies.delete(0, END)
            self.fillListsAllies()
        
    def ongletTradeChoicePlayer(self):
        self.menuModesOnlets()
        self.selectedOnglet = self.SELECTED_TRADE

        self.menuModes.tradeChoice.grid(row=3, column=2)

    def ongletTradeWaiting(self):
        self.menuModesOnlets()
        self.selectedOnglet = self.SELECTED_TRADE

        self.menuModes.create_text(150,50,text='En attente de la réponse de l\'autre joueur.',fill='white')

    def ongletTradeNoAnswer(self):
        self.selectedOnglet = self.SELECTED_TRADE
        self.menuModesOnlets()
        self.menuModes.create_text(150,50,text='L\'autre joueur a refusé l\'échange.',fill='white')

    def ongletTradeYesAnswer(self):
        self.menuModesOnlets()
        self.menuModes.create_text(150,50,text='L\'échange a été conclue.',fill='white')

    def ongletTradeYesNoQuestion(self, id1):
        self.menuModesOnlets()
        self.selectedOnglet = self.SELECTED_TEAM

        self.answerId = id1
        self.menuModes.create_text(150,50,text='Voulez-vous accepter la demande d\'échange avec '+self.game.players[id1].name+'?',fill='white')
        self.menuModes.yesButton.grid(row=3,column=2)
        self.menuModes.noButton.grid(row=3,column=3)

    def ongletTradeAskConfirm(self, id1, min1, min2, gaz1, gaz2):
        self.menuModesOnlets()
        self.selectedOnglet = self.SELECTED_TEAM

        self.answerId = id1
        self.menuModes.create_text(165,50,text=''+self.game.players[self.answerId].name+' vous offre '+min1+' unités de ses minéraux et '+gaz1+' unités de son gaz',fill='white')
        self.menuModes.create_text(160,65,text='contre '+min2+' unités de vos minéraux et '+gaz2+' unités de votre gaz',fill='white')
        self.menuModes.yesButtonConfirm.config(command=lambda:self.parent.confirmTrade(True, self.answerId, min1, min2, gaz1, gaz2))
        self.menuModes.noButtonConfirm.config(command=lambda:self.parent.confirmTrade(False, self.answerId, min1, min2, gaz1, gaz2))
        self.menuModes.yesButtonConfirm.grid(row=4,column=2)
        self.menuModes.noButtonConfirm.grid(row=4,column=3)
        self.menuModes.modifyButtonConfirm.grid(row=4,column=4)

    def ongletTrade(self, id1, id2):
        self.menuModesOnlets()
        self.selectedOnglet = self.SELECTED_TEAM
        self.answerId = id1
        self.answerId2 = id2
        if self.game.isMasterTrade==True:
            #Fenetre trade spins
            self.menuModes.nomJoueur1.config(text=self.game.players[self.answerId].name)
            self.menuModes.nomJoueur2.config(text=self.game.players[self.answerId2].name)
            self.menuModes.spinGaz2.config(to=self.game.players[self.answerId2].ressources[1])
            self.menuModes.spinGaz1.config(to=self.game.players[self.answerId].ressources[1])
            self.menuModes.spinMinerals1.config(to=self.game.players[self.answerId].ressources[0])
            self.menuModes.spinMinerals2.config(to=self.game.players[self.answerId2].ressources[0])
            self.menuModes.nomJoueur1.grid(row=3,column=3)
            self.menuModes.etiqMenieral1.grid(row=4,column=2)
            self.menuModes.spinMinerals1.grid(row=4,column=3)
            # gaz Joueurs 1
            self.menuModes.etiqGaz1.grid(row=5,column=2)
            self.menuModes.spinGaz1.grid(row=5,column=3)
            # Bouton ECHANGE
            self.menuModes.bEchange.grid(column=4,row=2)
            # minerals Joueurs 2
            self.menuModes.nomJoueur2.grid(row=3,column=5)
            self.menuModes.etiqMenieral2.grid(row=4,column=5)
            self.menuModes.spinMinerals2.grid(row=4,column=6)
            # gaz Joueurs 2
            self.menuModes.etiqGaz2.grid(row=5,column=5)
            self.menuModes.spinGaz2.grid(row=5,column=6)
        else:
            self.menuModes.create_text(150,50,text='Attente de l\'offre de l\'autre joueur.',fill='white')
        
    def ongletSelectedUnit(self):
        self.menuModesOnlets()
        self.selectedOnglet = self.SELECTED_UNIT_SELECTED
        unitList = self.game.players[self.game.playerId].selectedObjects
        countList = [0,0,0,0,0,0,0]
        if len(unitList) == 1:
            self.showInfo(unitList[0])

        elif len(unitList) > 1 : 
            if isinstance(self.game.players[self.game.playerId].selectedObjects[0],u.Mothership) == False:
                x = 20
                y = 50
                for i in unitList:
                    if isinstance(i, u.SpaceAttackUnit):
                        self.menuModes.create_image(x, y, image = self.gifAttackUnit, tags = ('selected_unit',i.position[0],i.position[1]))
                    elif isinstance(i, u.GatherShip):
                        self.menuModes.create_image(x,y, image = self.gifCargo, tags = ('selected_unit',i.position[0],i.position[1]))
                    elif isinstance(i, u.TransportShip):
                        self.menuModes.create_image(x,y, image = self.gifTransport, tags =  ('selected_unit',i.position[0],i.position[1]))
                    elif isinstance(i, u.Unit):
                        self.menuModes.create_image(x,y, image = self.gifUnit, tags = ('selected_unit',i.position[0],i.position[1]))      
                    countList[i.type] += 1
                               
                    #Ca sert à créer une nouvelle ligne lorsque le nombre de units selectionné le requiert
                    x += 52
                    if x > 600:
                        x = 20
                        y+= 46
                
                y = 0
                for i in range(0,len(countList)):
                    if countList[i] > 0:

                        self.menuModes.create_text(700,y + 20,text= str(countList[i]) +'X' ,fill='white')

                        if i == Unit.SCOUT:
                            self.menuModes.create_image(800,y, anchor = NE, image = self.gifUnit,tags = ('selected_all_units',i))
                            
                        elif i == Unit.CARGO: 
                            self.menuModes.create_image(800,y,anchor = NE, image = self.gifCargo,tags = ('selected_all_units',i))
                        elif i == Unit.TRANSPORT: 
                            self.menuModes.create_image(800,y,anchor = NE, image = self.gifTransport,tags = ('selected_all_units',i))                                
                        elif i == Unit.ATTACK_SHIP: 
                            self.menuModes.create_image(800,y, anchor = NE,image = self.gifAttackUnit,tags = ('selected_all_units',i))    
                        
                        y+=46

    def showInfo(self, unit):
        if isinstance(unit, Planet) == False and isinstance(unit, AstronomicalObject) == False and isinstance(unit, Unit):
            self.menuModes.create_text(20,80, text = 'Type : ' + Unit.FRENCHNAME[unit.type], anchor = NW, fill = 'white')
            self.menuModes.create_text(20,100, text = "HP : " + str(math.trunc(unit.hitpoints)) + "/" + str(unit.maxHP),anchor = NW, fill = 'white')
            self.menuModes.create_text(20,120, text = "Vitesse de déplacement : " + str(unit.moveSpeed) + " années lumière à l'heure.", anchor = NW, fill = 'white')
            self.menuModes.create_text(20,140, text = "Champ de vision : " + str(unit.viewRange) + " années lumière", anchor = NW, fill = 'white')
            #Ces images seront remplacer par de plus grandes et plus belles ! (aghi on t'attends ! )

            if isinstance(unit, u.Mothership) == False :
                if isinstance(self.game.players[self.game.playerId].selectedObjects[0], u.SpaceAttackUnit):
                    self.menuModes.create_image(20, 50, image = self.gifAttackUnit)
                    self.menuModes.create_text(20,160, text = "Vitesse d'attaque : " + str(unit.AttackSpeed),anchor = NW, fill = 'white')
                    self.menuModes.create_text(20,180, text = "Force d'attaque : " + str(unit.AttackDamage),anchor = NW, fill = 'white')
                elif isinstance(self.game.players[self.game.playerId].selectedObjects[0], u.GatherShip):
                    self.menuModes.create_image(20,50, image = self.gifCargo)
                    self.menuModes.create_text(20,160, text = "Chargement : gaz = " + str(unit.container[1]) + " mineral = " + str(unit.container[0]), anchor = NW, fill = 'white')
                    self.menuModes.create_text(20,180, text = "Taille du réservoir : " + str(unit.maxGather), anchor = NW, fill = 'white')
                    self.menuModes.create_text(20,200, text = "Vitesse de minage : " + str(unit.gatherSpeed), anchor = NW, fill = 'white')
                elif isinstance(self.game.players[self.game.playerId].selectedObjects[0], u.TransportShip):
                    self.menuModes.create_image(20,50, image = self.gifTransport)
                elif isinstance(self.game.players[self.game.playerId].selectedObjects[0], u.Unit):
                    self.menuModes.create_image(20,50, image = self.gifUnit)

                if self.game.players[self.game.playerId].selectedObjects[0].hitpoints != self.game.players[self.game.playerId].selectedObjects[0].maxHP:
                    self.menuModes.create_arc((675, 190,500,10), start=0, extent= (self.game.players[self.game.playerId].selectedObjects[0].hitpoints / self.game.players[self.game.playerId].selectedObjects[0].maxHP)*359.99999999 , fill='green', tags = 'arc', outline ='green')
                else:
                    self.menuModes.create_oval((675, 190,500,10), fill='green', tags = 'arc', outline ='green')

            else:
                if len(self.game.players[self.game.playerId].motherShip.unitBeingConstruct) > 0:
                    self.menuModes.create_text(20,160, text = str(len(self.game.players[self.game.playerId].motherShip.unitBeingConstruct)) + " unités actuellement en contruction", anchor = NW, fill = 'white')
                    self.createUnitsConstructionMenu()
                else:
                    self.menuModes.create_text(20,160, text = "Aucune unité n'est actuellement en contruction", anchor = NW, fill = 'white')
                    if self.game.players[self.game.playerId].selectedObjects[0].hitpoints != self.game.players[self.game.playerId].selectedObjects[0].maxHP:
                        self.menuModes.create_arc((675, 190,500,10), start=0, extent= (self.game.players[self.game.playerId].selectedObjects[0].hitpoints / self.game.players[self.game.playerId].selectedObjects[0].maxHP)*359.99999999 , fill='green', tags = 'arc')
                    else:
                        self.menuModes.create_oval((675, 190,500,10), fill='green', tags = 'arc', outline ='green')

    def refreshGame(self, isOnPlanet):
        self.showMinerals.config(text="Mineraux: "+str(self.game.players[self.game.playerId].ressources[0]))
        self.showGaz.config(text="Gaz: "+str(self.game.players[self.game.playerId].ressources[1]))
        if self.selectedOnglet == self.SELECTED_UNIT_SELECTED:
            self.ongletSelectedUnit()
        if not isOnPlanet:
            self.drawWorld()
        else:
            self.drawPlanetGround(self.game.getCurrentPlanet())
            self.redrawMinimap()
        
    def ongletChat(self,gameFrame):
        self.menuModesOnlets()
        self.selectedOnglet = self.SELECTED_CHAT
        self.menuModes.chat.grid(row=3, column=3, columnspan=3)
        self.menuModes.entryMess.grid(row=4, column=3, columnspan=3)
        self.menuModes.entryMess.bind("<Return>",self.enter)
        self.parent.refreshMessages(self.menuModes.chat)
        
    # delete tout ce qu'il y a dans le canvas menuModes + affiche les 3 menus
    def menuModesOnlets(self):
        self.menuModes.delete(ALL)
        self.menuModes.chat.grid_forget()
        self.menuModes.entryMess.grid_forget()
        self.menuModes.yesButton.grid_forget()
        self.menuModes.noButton.grid_forget()
        self.menuModes.yesButtonConfirm.grid_forget()
        self.menuModes.noButtonConfirm.grid_forget()
        self.menuModes.tradeChoice.grid_forget()
        self.menuModes.etiqMenieral1.grid_forget()
        self.menuModes.etiqMenieral2.grid_forget()
        self.menuModes.nomJoueur1.grid_forget()
        self.menuModes.nomJoueur2.grid_forget()
        self.menuModes.spinMinerals1.grid_forget()
        self.menuModes.spinMinerals2.grid_forget()
        self.menuModes.etiqGaz1.grid_forget()
        self.menuModes.etiqGaz2.grid_forget()
        self.menuModes.spinGaz1.grid_forget()
        self.menuModes.spinGaz2.grid_forget()
        self.menuModes.bEchange.grid_forget()
        self.menuModes.modifyButtonConfirm.grid_forget()
        self.menuModes.listAllies.grid_forget()
        self.menuModes.listAllies.delete(0, END)
        self.menuModes.listEnnemies.grid_forget()
        self.menuModes.listEnnemies.delete(0, END)
        self.menuModes.labelEnnemy.grid_forget()
        self.menuModes.labelAlly.grid_forget()
        self.menuModes.toEnnemyButton.grid_forget()
        self.menuModes.toAllyButton.grid_forget()
        self.gameArea.focus_set()
        self.menuModes.create_image(0,0,image=self.gifChat,anchor = NW,tag='bouton_chat')
        self.menuModes.create_image(77,0,image=self.gifTrade,anchor = NW,tag='bouton_trade')
        self.menuModes.create_image(150,0,image=self.gifTeam,anchor = NW,tag='bouton_team')
        self.menuModes.create_image(227,0,image=self.gifSelectedUnit,anchor = NW,tag='bouton_selectedUnit')

    def createActionMenu(self, type):
        self.Actionmenu.delete(ALL)
        if(type == self.MAIN_MENU):
            self.Actionmenu.create_image(0,0,image=self.gifCadreMenuAction,anchor = NW, tag='actionMain')
            units = self.game.players[self.game.playerId].selectedObjects 
            if len(units) > 0:
                if isinstance(units[0], Mothership):
                        self.Actionmenu.create_image(13,35,image=self.gifRallyPoint,anchor = NW, tags = 'Button_RallyPoint')
                        self.Actionmenu.create_image(76,35,image = self.gifBuild, anchor = NW, tags = 'Button_Build')
                        self.Actionmenu.create_image(140,35,image = self.gifTechTree, anchor = NW, tags = 'Button_Tech')
                elif isinstance(units[0], Unit):
                    self.Actionmenu.create_image(13,35,image=self.gifMove,anchor = NW, tags = 'Button_Move')
                    self.Actionmenu.create_image(76,35,image=self.gifStop,anchor = NW, tags = 'Button_Stop')
                    self.Actionmenu.create_image(140,35,image=self.gifPatrol,anchor = NW, tags = 'Button_Patrol')
                    if units[0].type == units[0].SCOUT:
                        self.Actionmenu.create_image(13,89,image=self.gifBuild,anchor = NW, tags = 'Button_Build_Waypoint')
                    elif isinstance(units[0], SpaceAttackUnit):
                        self.Actionmenu.create_image(13,89,image=self.gifAttack,anchor = NW, tags = 'Button_Attack')
                if len(self.game.players[self.game.playerId].selectedObjects) > 1:
                    self.Actionmenu.create_image(76,143,image=self.gifTriangle,anchor = NW, tags = 'Button_Triangle')
                    self.Actionmenu.create_image(140,143,image=self.gifSquare,anchor = NW, tags = 'Button_Square')
        elif(type == self.MOTHERSHIP_BUILD_MENU):
            self.Actionmenu.create_image(0,0,image=self.gifCadreMenuAction,anchor = NW, tag='actionMain')
            self.Actionmenu.create_image(13,35,image = self.gifUnit, anchor = NW, tags = 'Button_Build_Scout')
            self.Actionmenu.create_image(76,35,image = self.gifAttackUnit, anchor = NW, tags = 'Button_Build_Attack')
            self.Actionmenu.create_image(140,35,image = self.gifCargo, anchor = NW, tags = 'Button_Build_Gather')
            self.Actionmenu.create_image(13,89,image = self.gifTransport, anchor = NW, tags = 'Button_Build_Transport')
            self.Actionmenu.create_image(140,143,image = self.gifReturn, anchor = NW, tags = 'Button_Return')
        elif(type == self.WAITING_FOR_RALLY_POINT_MENU):
            self.Actionmenu.create_text(5,5,text = "Cliquez à un endroit dans l'aire de jeu afin d'initialiser le point de ralliement du vaisseau mère.",anchor = NW, fill = 'white', width = 200)
            self.Actionmenu.create_image(140,143,image = self.gifReturn, anchor = NW, tags = 'Button_Return')
        elif(type == self.WAITING_FOR_ATTACK_POINT_MENU):
            self.Actionmenu.create_text(5,5,text = "Cliquez à un endroit dans l'aire de jeu afin d'initialiser le unit / building que vous voulez attaquer.",anchor = NW, fill = 'white', width = 200)
            self.Actionmenu.create_image(140,143,image = self.gifReturn, anchor = NW, tags = 'Button_Return')
        elif(type == self.WAITING_FOR_MOVE_POINT_MENU):
            self.Actionmenu.create_text(5,5,text = "Cliquez à un endroit dans l'aire de jeu afin d'initialiser le mouvement de vos units sélectionnés.",anchor = NW, fill = 'white', width = 200)
            self.Actionmenu.create_image(140,143,image = self.gifReturn, anchor = NW, tags = 'Button_Return')
        elif(type == self.WAITING_FOR_PATROL_POINT_MENU):
            self.Actionmenu.create_text(5,5,text = "Cliquez à un endroit dans l'aire de jeu afin d'initialiser le mouvement de patrouille de vos units d'attaques sélectionnés",anchor = NW, fill = 'white', width = 200)
            self.Actionmenu.create_image(140,143,image = self.gifReturn, anchor = NW, tags = 'Button_Return')
        elif(type == self.WAITING_FOR_BUILDING_POINT_MENU):
            self.Actionmenu.create_text(5,5,text = "Cliquez à un endroit dans l'aire de jeu afin d'initialiser le lieu où la construction du bâtiment va s'effectuer",anchor = NW, fill = 'white', width = 200)
        elif(type == self.TECHNOLOGY_TREE_MENU):
            self.Actionmenu.create_image(0,0,image=self.gifCadreMenuAction,anchor = NW, tag='actionMain')
            self.Actionmenu.create_image(13,35,image = self.gifAttackUnit, anchor = NW, tags = 'Button_Tech_Units')
            self.Actionmenu.create_image(76,35,image = self.gifUnit, anchor = NW, tags = 'Button_Tech_Buildings')
            self.Actionmenu.create_image(140,35,image = self.gifTransport, anchor = NW, tags = 'Button_Tech_Mothership')
            self.Actionmenu.create_image(140,143,image = self.gifReturn, anchor = NW, tags = 'Button_Return')
        elif(type == self.TECHTREE_UNIT_MENU):
            techTree = self.game.players[self.game.playerId].techTree
            techs = techTree.getTechs(techTree.UNITS)
            y=5
            for i in techs:
                self.Actionmenu.create_text(5,y,text = i.name,anchor = NW, fill = 'white', width = 200, tag='Button_Buy_Unit_Tech/'+str(techs.index(i)))
                self.Actionmenu.create_text(5,y+13,text = "Minéraux: "+str(i.costMine)+"   Gaz: "+str(i.costGaz),anchor = NW, fill = 'white', width = 200, tag='Button_Buy_Unit_Tech/'+str(techs.index(i)))
                y+=28
            self.Actionmenu.create_image(140,143,image = self.gifReturn, anchor = NW, tags = 'Button_Return')
        elif(type == self.TECHTREE_BUILDING_MENU):
            techTree = self.game.players[self.game.playerId].techTree
            techs = techTree.getTechs(techTree.BUILDINGS)
            y=5
            for i in techs:
                self.Actionmenu.create_text(5,y,text = i.name,anchor = NW, fill = 'white', width = 200, tag='Button_Buy_Building_Tech/'+str(techs.index(i)))
                self.Actionmenu.create_text(5,y+13,text = "Minéraux: "+str(i.costMine)+"   Gaz: "+str(i.costGaz),anchor = NW, fill = 'white', width = 200, tag='Button_Buy_Building_Tech/'+str(techs.index(i)))
                y+=28
            self.Actionmenu.create_image(140,143,image = self.gifReturn, anchor = NW, tags = 'Button_Return')
        elif(type == self.TECHTREE_MOTHERSHIP_MENU):
            techTree = self.game.players[self.game.playerId].techTree
            techs = techTree.getTechs(techTree.MOTHERSHIP)
            y=5
            for i in techs:
                self.Actionmenu.create_text(5,y,text = i.name,anchor = NW, fill = 'white', width = 200, tag='Button_Buy_Mothership_Tech/'+str(techs.index(i)))
                self.Actionmenu.create_text(5,y+13,text = "Minéraux: "+str(i.costMine)+"   Gaz: "+str(i.costGaz),anchor = NW, fill = 'white', width = 200, tag='Button_Buy_Mothership_Tech/'+str(techs.index(i)))
                y+=28
            self.Actionmenu.create_image(140,143,image = self.gifReturn, anchor = NW, tags = 'Button_Return')

    def createUnitsConstructionMenu(self):
        y = 35;
        
        ok = False;
        l = None;
        r = 1
        list = self.game.players[self.game.playerId].motherShip.unitBeingConstruct
        for i in list:
            if(list.index(i) != 0):
                if (list[list.index(i)].name == list[list.index(i) - 1].name):
                    ok = True
                    r += 1
                else:
                    r = 1
                    ok = False
                    self.menuModes.create_image(675, y, image = self.iconCancel, anchor = NW, tags = ('cancelUnitButton', list.index(i)))
            else:
                    if (self.wantToCancelUnitBuild == False):
                        self.menuModes.create_arc((675, y, 695, 55), start=0, extent= (i.constructionProgress / i.buildTime)*360 , fill='blue' , tags = 'arc', outline="cyan")
                    else:
                        self.menuModes.create_image(675,y, image = self.iconCancel, anchor = NW, tags = ('cancelUnitButton', list.index(i)))

            if (ok == True):
                self.menuModes.itemconfig(l, text = str(r) + " " + i.name)
            else:
                l = self.menuModes.create_text(575,y,text = str(r) + " " + i.name, anchor = NW, fill = 'white')
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
        Label(joinGameFrame, image=self.lobbyBackground).grid(row=0,column=0,rowspan=10,columnspan=4)
        Label(joinGameFrame, text="Nom de joueur:", fg="white", bg="black").grid(row=3, column=1)
        self.entryLogin = Entry(joinGameFrame, width=20)
        self.entryLogin.focus_set()
        self.entryLogin.grid(row=3, column=2)
        Label(joinGameFrame, text="Adresse du serveur:", fg="white", bg="black").grid(row=4, column=1)
        self.entryServer = Entry(joinGameFrame, width=20)
        self.entryServer.grid(row=4, column=2)
        widget = Button(joinGameFrame, text='Connecter', command=lambda:self.lobbyEnter(0, self.entryLogin.get(), self.entryServer.get()))
        widget.grid(row=5, column=2)
		#Crée un bouton de retour au menu principal
        widget = Button(joinGameFrame, text='Retour', command=lambda:self.changeFrame(self.mainMenu), width=10)
        widget.grid(row=6, column=2, pady=10)
        self.entryServer.bind("<Return>",self.lobbyEnter)
        return joinGameFrame
    
    #Frame de création de nouveau serveur
    def fCreateServer(self):
        #Crée le frame
        createServerFrame = Frame(self.root, bg="black")
        #Background
        Label(createServerFrame, image=self.lobbyBackground).grid(row=0,column=0,rowspan=10,columnspan=4)
        #Crée le label de l'IP du serveur
        Label(createServerFrame, text="Adresse du serveur:", fg="white", bg="black").grid(row=3, column=1)
        #Crée le champ texte pour l'IP du serveur
        self.entryCreateServer = Entry(createServerFrame, width=20)
        #On met l'adresse de l'hôte comme valeur par défaut
        self.entryCreateServer.insert(0,self.parent.playerIp)
        self.entryCreateServer.grid(row=3, column=2)
        #Crée le label du nom du joueur
        Label(createServerFrame, text="Nom de joueur:", fg="white", bg="black").grid(row=4, column=1)
        #Crée le champ texte pour le nom du joueur
        self.entryCreateLogin = Entry(createServerFrame, width=20)
        self.entryCreateLogin.focus_set()
        self.entryCreateLogin.grid(row=4, column=2)
        #Crée le bouton de confirmation
        widget = Button(createServerFrame, text='Créer', command=lambda:self.startServer(False))
        widget.grid(row=5, column=2)
        #Crée le bouton de confirmation et se connecte
        widget = Button(createServerFrame, text='Créer et connecter', command=lambda:self.startServer(True))
        widget.grid(row=6, column=2)
		#Crée un bouton de retour au menu principal
        widget = Button(createServerFrame, text='Retour', command=lambda:self.changeFrame(self.mainMenu), width=10)
        widget.grid(row=7, column=2, pady=10)
        return createServerFrame

    def startServer(self, connect):
        serverAddress = self.entryCreateServer.get()
        userName = self.entryCreateLogin.get()
        self.parent.startServer(serverAddress, connect, userName)
    
    #Frame du lobby
    def fLobby(self):
        self.entryServer.unbind("<Return>")
        lobbyFrame = Frame(self.root, bg="black")
        Label(lobbyFrame, image=self.lobbyBackground).grid(row=0,column=0,rowspan=15,columnspan=8)
        if self.parent.server != None:
            pNum = len(self.parent.server.getSockets())
            for i in range(0, pNum):
                Label(lobbyFrame, text=self.parent.server.getSockets()[i][1], fg="white", bg="black", width=10).grid(row=i+3,column=0)
            Label(lobbyFrame, text='Admin : '+self.parent.server.getSockets()[0][1], fg="white", bg="black").grid(row=12, column=0)
            if self.game.playerId == 0:
                Button(lobbyFrame, text='Demarrer la partie', command=self.parent.startGame, bg="black", fg="white").grid(row=12, column=1)
        self.chatLobby = Label(lobbyFrame, anchor=W, justify=LEFT, width=45, background='black', fg='white', relief='raised')
        self.chatLobby.grid(row=2, column=5, rowspan=5)
        self.entryMessLobby = Entry(lobbyFrame, width=35)
        self.entryMessLobby.grid(row=6, column=5)
        self.entryMessLobby.bind("<Return>", self.sendMessLobby)
        #Choix de couleur
        self.variableColor = StringVar(lobbyFrame)
        listOfColors = self.parent.server.getColorChoices()
        self.colorOPTIONS = ["Orange","Rouge","Bleu"]
        self.variableColor.set(self.colorOPTIONS[0]) # default value
        self.colorChoice = OptionMenu(lobbyFrame, self.variableColor, *self.colorOPTIONS, command=self.parent.choiceColor)
        self.colorChoice.grid(row=(self.game.playerId)+3, column=1)
        self.colorChoice['menu'].delete(0, END)
        for i in listOfColors:
            if i[1] == False or self.parent.server.getSockets()[self.game.playerId][3] == listOfColors.index(i):
                self.colorChoice['menu'].add_command(label=i[0], command=lambda temp = i[0]: self.colorChoice.setvar(self.colorChoice.cget("textvariable"), value = temp))
        self.variableColor.trace('w',self.parent.choiceColor)
        return lobbyFrame

    def redrawLobby(self ,lobbyFrame):
        listOfColors = self.parent.server.getColorChoices()
        self.colorChoice['menu'].delete(0, END)
        for i in listOfColors:
            if i[1] == False or self.parent.server.getSockets()[self.game.playerId][3] == listOfColors.index(i):
                self.colorChoice['menu'].add_command(label=i[0], command=lambda temp = i[0]: self.colorChoice.setvar(self.colorChoice.cget("textvariable"), value = temp))
        if self.parent.server != None:
            pNum = len(self.parent.server.getSockets())
            for i in range(0, pNum):
                Label(lobbyFrame, text=self.parent.server.getSockets()[i][1], fg="white", bg="black", width=10).grid(row=i+3,column=0)
                if self.parent.server.getSockets()[i][3] != -1 and i != self.game.playerId:
                    Label(lobbyFrame, text=self.parent.server.getColorChoices()[self.parent.server.getSockets()[i][3]][0], fg="white", bg="black").grid(row=i+3, column=1)
                
    def sendMessLobby(self, eve):
        if self.entryMessLobby.get() != "":
            self.parent.sendMessageLobby(self.entryMessLobby.get(), self.parent.server.getSockets()[self.game.playerId][1])
            self.entryMessLobby.delete(0,END)
     
        
    def loginFailed(self):
        mb.showinfo('Erreur de connection', 'Le serveur est introuvable. Veuillez reessayer.')

    def colorAlreadyChosen(self):
        mb.showinfo('Trop tard!', 'La couleur sélectionnée a déjà été choisie.')

    def gameHasBeenStarted(self):
        mb.showinfo('Erreur de connection', 'La partie a déjà débutée. Veuillez attendre sa fin.')
    
    def showAdminLeft(self):
        mb.showinfo('Fin de la partie', 'L\'administrateur de la partie a quitté prématurément la partie, la partie est donc terminée.')

    def showGameIsFinished(self):
        mb.showinfo('Fin de la partie', 'Vous avez perdu.')

    def serverCreated(self, serverIP):
        mb.showinfo('Serveur créé', 'Le serveur a été créé à l\'adresse ' + serverIP + '.')
        
    def serverNotCreated(self):
        mb.showinfo('Serveur non créé', 'Une erreur est survenue lors de la création du serveur.\nVeuillez vérifier que les informations entrées sont exactes,\nou qu\'un autre serveur n\'est pas en cours d\'exécution.')
    
    #Methode pour dessiner la vue d'un planete
    def drawPlanetGround(self, planet):
        self.gameArea.delete('deletable')
        self.drawPlanetBackground()
        color = self.game.players[self.game.playerId].colorId
        for i in planet.minerals:
            distance = self.game.players[self.game.playerId].camera.calcDistance(i.position)
            if i in self.game.players[self.game.playerId].selectedObjects:
                self.gameArea.create_text(distance[0], distance[1]-40, fill="cyan", text="Mineral :" + str(i.nbMinerals), tag='deletable')
                self.gameArea.create_oval(distance[0]-(i.WIDTH/2+3), distance[1]-(i.HEIGHT/2+3), distance[0]+(i.WIDTH/2+3), distance[1]+(i.HEIGHT/2+3), outline='yellow', tag='deletable')
            self.gameArea.create_image(distance[0], distance[1], image=self.mineral, tag='deletable')
        for i in planet.gaz:
            distance = self.game.players[self.game.playerId].camera.calcDistance(i.position)
            if i in self.game.players[self.game.playerId].selectedObjects:
                self.gameArea.create_text(distance[0], distance[1]-(i.HEIGHT/2+8), fill="green", text="Gaz :" + str(i.nbGaz), tag='deletable')
                self.gameArea.create_oval(distance[0]-(i.WIDTH/2+3), distance[1]-(i.HEIGHT/2+3), distance[0]+(i.WIDTH/2+3), distance[1]+(i.HEIGHT/2+3), outline='yellow', tag='deletable')
            self.gameArea.create_image(distance[0], distance[1],image=self.gaz, tag='deletable')
        if planet.nuclearSite != None:
            site = planet.nuclearSite
            distance = self.game.players[self.game.playerId].camera.calcDistance(site.position)
            if site in self.game.players[self.game.playerId].selectedObjects:
                self.gameArea.create_text(distance[0], distance[1]-(site.HEIGHT/2+10), fill="yellow", text="Nuclear!", tag='deletable')
                self.gameArea.create_oval(distance[0]-(site.WIDTH/2+3), distance[1]-(site.WIDTH/2+3),distance[0]+(site.WIDTH/2+3),distance[1]+(site.WIDTH/2+3), outline='purple', tag='deletable')
            self.gameArea.create_image(distance[0], distance[1], image=self.nuclear, tag='deletable')
        for i in planet.landingZones:
            distance = self.game.players[self.game.playerId].camera.calcDistance(i.position)
            if i in self.game.players[self.game.playerId].selectedObjects:
                self.gameArea.create_oval(distance[0]-(i.WIDTH/2+3),distance[1]-(i.HEIGHT/2+3),distance[0]+(i.WIDTH/2+3),distance[1]+(i.HEIGHT/2+3), outline='green', tag='deletable')
            self.gameArea.create_image(distance[0], distance[1], image=self.landingZones[color], tag='deletable')
            if i.LandedShip != None:
                self.gameArea.create_image(distance[0]+1, distance[1], image=self.landedShips[color], tag='deletable')
        for i in planet.units:
            distance = self.game.players[self.game.playerId].camera.calcDistance(i.position)
            if i in self.game.players[self.game.playerId].selectedObjects:
                self.gameArea.create_oval(distance[0]-(i.SIZE[i.type][0]/2+3), distance[1]-(i.SIZE[i.type][1]/2+3), distance[0]+(i.SIZE[i.type][0]/2+3),distance[1]+(i.SIZE[i.type][1]/2+3),outline='green', tag='deletable')
            self.gameArea.create_image(distance[0], distance[1], image=self.groundUnits[color], tag='deletable')
        if self.dragging:
            self.drawSelectionBox()

    def drawPlanetBackground(self):
        self.gameArea.delete('background')
        camera = self.game.players[self.game.playerId].camera
        pos = camera.calcDistance([0,0])
        self.gameArea.create_image(pos[0],pos[1],image=self.planetBackground, anchor=NW, tag='background')

    def changeBackground(self, type):
        self.gameArea.delete('background')
        if type == 'PLANET':
            camera = self.game.players[self.game.playerId].camera
            pos = camera.calcDistance([0,0])
            self.gameArea.create_image(pos[0],pos[1],image=self.planetBackground, anchor=NW, tag='background')		
        else:
            self.gameArea.create_image(0,0,image=self.galaxyBackground, anchor=NW, tag='background')

    #Methode pour dessiner la galaxie
    def drawWorld(self):
        self.gameArea.delete('deletable')
        sunList = self.game.galaxy.solarSystemList
        players = self.game.players 
        id = self.game.playerId
        for i in sunList:
            if self.game.players[self.game.playerId].inViewRange(i.sunPosition):
                if not i.discovered:
                    i.discovered = True
                    self.redrawMinimap()
                self.drawSun(i.sunPosition, players[id], True)
            else:
                if i.discovered:
                    self.drawSun(i.sunPosition, players[id], False)
            for j in i.planets:
                if self.game.players[self.game.playerId].inViewRange(j.position) or j.alreadyLanded(id):
                    if not j.discovered:
                        j.discovered = True
                        self.redrawMinimap()
                    self.drawPlanet(j, players[id], True)
                else:
                    if j.discovered:
                        self.drawPlanet(j, players[id], False)
            for j in i.nebulas:
                if self.game.players[self.game.playerId].inViewRange(j.position):
                    if not j.discovered:
                        j.discovered = True
                        self.redrawMinimap()
                    self.drawNebula(j, players[id], True)
                else:
                    if j.discovered:
                        self.drawNebula(j, players[id], False)
            for j in i.asteroids:
                if self.game.players[self.game.playerId].inViewRange(j.position):
                    if not j.discovered:
                        j.discovered = True
                        self.redrawMinimap()
                    self.drawAsteroid(j, players[id], True)
                else:
                    if j.discovered:
                        self.drawAsteroid(j, players[id], False)
        for i in players:
            if i.isAlive:
                if self.game.players[self.game.playerId].isAlly(i.id):
                    for j in i.buildings:
                        if j.isAlive:
                            if self.game.players[self.game.playerId].inViewRange(j.position):
                                j.discovered = True
                                self.drawBuilding(j,i,False)
                    for j in i.units:
                        if j.isAlive:
                            if j.type == j.MOTHERSHIP:
                                j.discovered = True
                            self.drawUnit(j, i, False)
                else:
                    for j in i.buildings:
                        if j.isAlive:
                            if self.game.players[self.game.playerId].inViewRange(j.position):
                                j.discovered = True
                                self.drawBuilding(j,i,False)
                    for j in i.units:
                        if j.isAlive:
                            if self.game.players[self.game.playerId].inViewRange(j.position):
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
                    
    def drawBuilding(self, building,  player, isInFOW):
        buildingPosition = building.position
        if self.game.players[self.game.playerId].camera.isInFOV(buildingPosition):
            distance = self.game.players[self.game.playerId].camera.calcDistance(buildingPosition)
            if not isInFOW:
                if building.type == b.Building.WAYPOINT:
                    if building.buildingTimer < building.TIME[building.type]:
                        if building in player.selectedObjects:
                            self.gameArea.create_oval(distance[0]-(building.SIZE[building.type][0]/2+15),distance[1]-(building.SIZE[building.type][1]/2+15),distance[0]+(building.SIZE[building.type][0]/2+15),distance[1]+(building.SIZE[building.type][1]/2+15), outline="purple", tag='deletable')
                        self.gameArea.create_image(distance[0]+1, distance[1], image=self.gifConstruction,tag='deletable')  
                    else:
                        if building in player.selectedObjects:
                            self.gameArea.create_oval(distance[0]-(building.SIZE[building.type][0]/2),distance[1]-(building.SIZE[building.type][1]/2),distance[0]+(building.SIZE[building.type][0]/2),distance[1]+(building.SIZE[building.type][1]/2), outline="purple", tag='deletable')    
                        self.gameArea.create_image(distance[0]+1, distance[1], image=self.waypoints[player.colorId],tag='deletable')
                if building.hitpoints <= 5:
                    self.gameArea.create_image(distance[0], distance[1], image=self.explosion, tag='deletable')
                if self.hpBars:
                    self.drawHPBars(distance, building)
                else:
                    self.drawHPHoverUnit(building, distance)
    
    #pour dessiner un vaisseau        
    def drawUnit(self, unit, player, isInFOW):
        unitPosition = unit.position
        if self.game.players[self.game.playerId].camera.isInFOV(unitPosition):
            distance = self.game.players[self.game.playerId].camera.calcDistance(unitPosition)
            if not isInFOW:
                if unit.type == unit.SCOUT:
                    if unit in player.selectedObjects:
                        self.gameArea.create_oval(distance[0]-(unit.SIZE[unit.type][0]/2+3),distance[1]-(unit.SIZE[unit.type][1]/2+3),distance[0]+(unit.SIZE[unit.type][0]/2+3),distance[1]+(unit.SIZE[unit.type][1]/2+3), outline="green", tag='deletable')
                    self.gameArea.create_image(distance[0], distance[1], image=self.scoutShips[player.colorId],tag='deletable')#On prend l'image dependamment du joueur que nous sommes
                if unit.type == unit.ATTACK_SHIP:
                    if unit.attackcount <= 5:
                        d2 = self.game.players[self.game.playerId].camera.calcDistance(unit.flag.finalTarget.position)
                        self.gameArea.create_line(distance[0],distance[1], d2[0], d2[1], fill="yellow", tag='deletable')
                    if unit in player.selectedObjects:
                        self.gameArea.create_oval(distance[0]-(unit.SIZE[unit.type][0]/2+3),distance[1]-(unit.SIZE[unit.type][1]/2+3),distance[0]+(unit.SIZE[unit.type][0]/2+3),distance[1]+(unit.SIZE[unit.type][1]/2+3), outline="green", tag='deletable')
                    self.gameArea.create_image(distance[0], distance[1], image=self.attackShips[player.colorId], tag='deletable')#On prend l'image dependamment du joueur que nous sommes
                elif unit.type == unit.MOTHERSHIP:
                    if unit in player.selectedObjects:
                        self.gameArea.create_oval(distance[0]-(unit.SIZE[unit.type][0]/2+3),distance[1]-(unit.SIZE[unit.type][1]/2+3),distance[0]+(unit.SIZE[unit.type][0]/2+3),distance[1]+(unit.SIZE[unit.type][1]/2+3), outline="green", tag='deletable')
                    self.gameArea.create_image(distance[0], distance[1], image = self.motherShips[player.colorId], tag='deletable')
                elif unit.type == unit.TRANSPORT:
                    if not unit.landed:
                        if unit in player.selectedObjects:
                            self.gameArea.create_oval(distance[0]-(unit.SIZE[unit.type][0]/2+3),distance[1]-(unit.SIZE[unit.type][1]/2+3),distance[0]+(unit.SIZE[unit.type][0]/2+3),distance[1]+(unit.SIZE[unit.type][1]/2+3), outline="green", tag='deletable')
                        self.gameArea.create_image(distance[0], distance[1], image = self.transportShips[player.colorId], tag='deletable')
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
        posSelected=self.game.players[self.game.playerId].camera.calcPointInWorld(self.positionMouse[0],self.positionMouse[1])
        if unit.position[0] >= posSelected[0]-(unit.SIZE[unit.type][0]/2) and unit.position[0] <= posSelected[0]+(unit.SIZE[unit.type][0]/2):
            if unit.position[1] >= posSelected[1]-(unit.SIZE[unit.type][1]/2) and unit.position[1] <= posSelected[1]+(unit.SIZE[unit.type][1]/2):
                if unit.owner != self.game.playerId:
                    self.gameArea.create_text(distance[0]-(len(self.game.players[unit.owner].name)/2),distance[1]+((unit.SIZE[unit.type][1]/2)+5), text=self.game.players[unit.owner].name, fill="white", tag='deletable')
                self.drawHPBars(distance,unit)
                            
    
    def drawHPBars(self, distance, unit):
        if isinstance(unit, Unit):
            if self.game.players[self.game.playerId].currentPlanet == None and not isinstance(unit, GroundUnit):
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
        else:
                hpLeft=((unit.hitpoints/unit.MAX_HP[unit.type])*(unit.SIZE[unit.type][0]))-(unit.SIZE[unit.type][0])/2
                hpLost=(hpLeft+(((unit.MAX_HP[unit.type]-unit.hitpoints)/unit.MAX_HP[unit.type])*(unit.SIZE[unit.type][0])))
                self.gameArea.create_rectangle(distance[0]-(unit.SIZE[unit.type][0])/2,distance[1]-(unit.SIZE[unit.type][1]/2+5),distance[0]+hpLeft,distance[1]-(unit.SIZE[unit.type][1]/2+5), outline="green", tag='deletable')
                if int(unit.hitpoints) != int(unit.MAX_HP[unit.type]):
                    self.gameArea.create_rectangle(distance[0]+hpLeft,distance[1]-(unit.SIZE[unit.type][1]/2+5),distance[0]+hpLost,distance[1]-(unit.SIZE[unit.type][1]/2+5), outline="red", tag='deletable')
        if unit.owner != self.game.playerId:
            self.gameArea.create_text(distance[0]-(len(self.game.players[unit.owner].name)/2),distance[1]+((unit.SIZE[unit.type][1]/2)+5), text=self.game.players[unit.owner].name, fill="white", tag='deletable')
          
    #Dessine la minimap
    def drawMinimap(self):
        self.minimap.delete('deletable')
        if self.game.players[self.game.playerId].currentPlanet == None:
            sunList = self.game.galaxy.solarSystemList
            players = self.game.players
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
                if self.game.players[self.game.playerId].isAlly(i.id):
                    for j in i.units:
                        if j.isAlive:
                                self.drawMiniUnit(j)
                else:
                    for j in i.units:
                        if j.isAlive:
                            if players[self.game.playerId].inViewRange(j.position):
                                self.drawMiniUnit(j)

        else:
            self.minimap.create_rectangle(0,0,200,200, fill='#009900', tag='deletable')
            planet = self.game.players[self.game.playerId].currentPlanet
            for i in planet.minerals:
                self.drawMiniMinerals(i, planet)
            for i in planet.gaz:
                self.drawMiniGaz(i, planet)
            for i in planet.landingZones:
                self.drawMiniLandingZone(i, planet)
            for i in planet.units:
                self.drawMiniGroundUnit(i, planet)
            if planet.nuclearSite != None:
                self.drawMiniNuclear(planet.nuclearSite, planet)
        self.drawMiniFOV()
        
    def redrawMinimap(self):
        self.minimap.delete(ALL)
        if self.game.players[self.game.playerId].currentPlanet == None:
            sunList = self.game.galaxy.solarSystemList
            players = self.game.players
            for i in sunList:
                self.drawMiniSun(i)
                for j in i.planets:
                    self.drawMiniPlanet(j)
                for n in i.nebulas:
                    self.drawMiniNebula(n)
                for q in i.asteroids:
                    self.drawMiniAsteroid(q)
            for i in players:
                if self.game.players[self.game.playerId].isAlly(i.id):
                    for j in i.units:
                        if j.isAlive:
                                self.drawMiniUnit(j)
                else:
                    for j in i.units:
                        if j.isAlive:
                            if players[self.game.playerId].inViewRange(j.position):
                                self.drawMiniUnit(j)
        else:
            self.minimap.create_rectangle(0,0,200,200, fill='#009900', tag='deletable')
            planet = self.game.players[self.game.playerId].currentPlanet
            for i in planet.minerals:
                self.drawMiniMinerals(i, planet)
            for i in planet.gaz:
                self.drawMiniGaz(i, planet)
            for i in planet.landingZones:
                self.drawMiniLandingZone(i, planet)
            for i in planet.units:
                self.drawMiniGroundUnit(i, planet)
            if planet.nuclearSite != None:
                self.drawMiniNuclear(planet.nuclearSite, planet)
        self.drawMiniFOV()

    #Dessine le carrer de la camera dans la minimap	
    def drawMiniFOV(self):
        camera = self.game.players[self.game.playerId].camera
        if self.game.players[self.game.playerId].currentPlanet == None:
            cameraX = (camera.position[0]-(self.taille/2) + self.game.galaxy.width/2) / self.game.galaxy.width * (self.taille/6)
            cameraY = (camera.position[1]-((self.taille/2)-self.taille/4) + self.game.galaxy.height/2) / self.game.galaxy.height * (self.taille/6)
            width = self.taille / self.game.galaxy.width * (self.taille/6)
            height = self.taille / self.game.galaxy.height * ((self.taille/12))
            self.minimap.create_rectangle(cameraX, cameraY, cameraX+width, cameraY+height, outline='GREEN', tag='deletable')
        else:
            planet = self.game.players[self.game.playerId].currentPlanet
            cameraX = (camera.position[0] * (self.MINIMAP_WIDTH)) / planet.WIDTH
            cameraY = (camera.position[1] * (self.MINIMAP_HEIGHT)) / planet.HEIGHT
            width = camera.screenWidth * (self.MINIMAP_WIDTH) / planet.WIDTH
            height = camera.screenHeight * (self.MINIMAP_HEIGHT) / planet.HEIGHT
	    #width = self.taille / planet.WIDTH * (self.taille/4)
            #height = self.taille / planet.HEIGHT * ((self.taille/16)*3)
            self.minimap.create_rectangle(cameraX-width/2, cameraY-height/2, cameraX+width/2, cameraY+height/2, outline='GREEN', tag='deletable')

    #Dessine un soleil dans la minimap    
    def drawMiniSun(self, sun):
        sunPosition = sun.sunPosition
        sunX = (sunPosition[0] + self.game.galaxy.width/2) / self.game.galaxy.width * (self.taille/6)
        sunY = (sunPosition[1] + self.game.galaxy.height/2) / self.game.galaxy.height * (self.taille/6)
        if sun.discovered:
            self.minimap.create_oval(sunX-3, sunY-3, sunX+3, sunY+3, fill='ORANGE')

    #Dessine une planete dans la minimap        
    def drawMiniPlanet(self, planet):
        planetPosition = planet.position
        planetX = (planetPosition[0] + self.game.galaxy.width/2) / self.game.galaxy.width * (self.taille/6)
        planetY = (planetPosition[1] + self.game.galaxy.height/2) / self.game.galaxy.height * (self.taille/6)
        if planet.discovered:
            self.minimap.create_oval(planetX-1, planetY-1, planetX+1, planetY+1, fill='LIGHT BLUE')
            
    #dessine une nebula dans la minimap
    def drawMiniNebula(self, nebula):
        if nebula.gazQte > 0:
            nebulaPosition = nebula.position
            nebulaX = (nebulaPosition[0] + self.game.galaxy.width/2) / self.game.galaxy.width * (self.taille/6)
            nebulaY = (nebulaPosition[1] + self.game.galaxy.height/2) / self.game.galaxy.height * (self.taille/6)
            if nebula.discovered:
                self.minimap.create_oval(nebulaX-1, nebulaY-1, nebulaX+1, nebulaY+1, fill='PURPLE')
        
    #dessine un asteroid dans la minimap
    def drawMiniAsteroid(self, asteroid):
        if asteroid.mineralQte > 0:
            asteroidPosition = asteroid.position
            asteroidX = (asteroidPosition[0] + self.game.galaxy.width/2) / self.game.galaxy.width * (self.taille/6)
            asteroidY = (asteroidPosition[1] + self.game.galaxy.height/2) / self.game.galaxy.height * (self.taille/6)
            if asteroid.discovered:
                self.minimap.create_oval(asteroidX-1, asteroidY-1, asteroidX+1, asteroidY+1, fill='CYAN')
        
    #Dessine une unite dans la minimap        
    def drawMiniUnit(self, unit):
        unitX = (unit.position[0] + self.game.galaxy.width/2) / self.game.galaxy.width * (self.taille/6)
        unitY = (unit.position[1] + self.game.galaxy.height/2) / self.game.galaxy.height * (self.taille/6)
        if unit.owner == self.game.playerId:
            color = 'GREEN'
        elif self.game.players[self.game.playerId].isAlly(unit.owner):
            color = 'YELLOW'
        else:
            color ='RED'
        if not isinstance(unit, GroundGatherUnit):
            if unit.type != unit.MOTHERSHIP:
                if unit.type == unit.TRANSPORT:
                    if not unit.landed:
                        self.minimap.create_polygon((unitX-2, unitY+2, unitX, unitY-2, unitX+2, unitY+2),fill=color, tag='deletable')
                else:
                    self.minimap.create_polygon((unitX-2, unitY+2, unitX, unitY-2, unitX+2, unitY+2),fill=color, tag='deletable')
            else:
                width = self.MINIMAP_WIDTH / self.game.galaxy.width * unit.SIZE[unit.type][0]
                height = self.MINIMAP_HEIGHT / self.game.galaxy.height * unit.SIZE[unit.type][1]
                self.minimap.create_oval((unitX-width/2, unitY-height/2, unitX+width/2, unitY+height/2),fill=color, tag='deletable')

    def drawMiniMinerals(self, mineral, planet):
        if mineral.nbMinerals > 0:
            x = int(mineral.position[0] * 200 / planet.WIDTH)
            y = int(mineral.position[1] * 200 / planet.HEIGHT)
            self.minimap.create_polygon(x-mineral.WIDTH/8, y, x, y-mineral.HEIGHT/8 ,x+mineral.WIDTH/8, y, x, y+mineral.HEIGHT/8, outline="black", fill='CYAN', width=2)

    def drawMiniGaz(self, gaz, planet):
        if gaz.nbGaz > 0:
            x = int(gaz.position[0] * 200 / planet.WIDTH)
            y = int(gaz.position[1] * 200 / planet.HEIGHT)
            self.minimap.create_oval(x-gaz.WIDTH/8, y-gaz.HEIGHT/8, x+gaz.WIDTH/8, y+gaz.HEIGHT/8,fill='GREEN')

    def drawMiniLandingZone(self, zone, planet):
        x = int(zone.position[0] * 200 / planet.WIDTH)
        y = int(zone.position[1] * 200 / planet.HEIGHT)
        if zone.ownerId == self.game.playerId:
            self.minimap.create_rectangle(x-zone.WIDTH/8, y-zone.HEIGHT/8, x+zone.WIDTH/8, y+zone.HEIGHT/8, fill='WHITE')
        else:
            self.minimap.create_rectangle(x-zone.WIDTH/8, y-zone.HEIGHT/8, x+zone.WIDTH/8, y+zone.HEIGHT/8, fill='RED')

    def drawMiniNuclear(self, site, planet):
        if site.nbRessource > 0:
            x = int(site.position[0] * 200 / planet.WIDTH)
            y = int(site.position[1] * 200 / planet.HEIGHT)
            self.minimap.create_oval(x-site.WIDTH/8, y-site.HEIGHT/8, x+site.WIDTH/8, y+site.HEIGHT/8,fill='YELLOW')

    def drawMiniGroundUnit(self, unit, planet):
        x = int(unit.position[0] * 200 / planet.WIDTH)
        y = int(unit.position[1] * 200 / planet.HEIGHT)
        if unit.owner == self.game.playerId:
            self.minimap.create_oval(x-unit.SIZE[unit.type][0]/8, y-unit.SIZE[unit.type][1]/8, x+unit.SIZE[unit.type][0]/8, y+unit.SIZE[unit.type][1]/8, fill='WHITE', outline='black', tag='deletable')
        else:
            self.minimap.create_oval(x-unit.SIZE[unit.type][0]/8, y-unit.SIZE[unit.type][1]/8, x+unit.SIZE[unit.type][0]/8, y+unit.SIZE[unit.type][1]/8, fill='RED', outline='black', tag='deletable')

    #Dessine la boite de selection lors du clic-drag	
    def drawSelectionBox(self):
        self.gameArea.create_rectangle(self.selectStart[0], self.selectStart[1], self.selectEnd[0], self.selectEnd[1], outline='WHITE', tag='deletable')

    #Actions quand on clic sur les fleches du clavier
    def keyPressUP(self, eve):
        if 'UP' not in self.game.players[self.game.playerId].camera.movingDirection:
            self.game.players[self.game.playerId].camera.movingDirection.append('UP')
            if self.game.players[self.game.playerId].currentPlanet == None:
                self.drawWorld()
            else:
                self.drawPlanetGround(self.game.players[self.game.playerId].currentPlanet)

    def keyPressDown(self, eve):
        if 'DOWN' not in self.game.players[self.game.playerId].camera.movingDirection:
            self.game.players[self.game.playerId].camera.movingDirection.append('DOWN')
            if self.game.players[self.game.playerId].currentPlanet == None:
                self.drawWorld()
            else:
                self.drawPlanetGround(self.game.players[self.game.playerId].currentPlanet)

    def keyPressLeft(self, eve):
        if 'LEFT' not in self.game.players[self.game.playerId].camera.movingDirection:
            self.game.players[self.game.playerId].camera.movingDirection.append('LEFT')
            if self.game.players[self.game.playerId].currentPlanet == None:
                self.drawWorld()
            else:
                self.drawPlanetGround(self.game.players[self.game.playerId].currentPlanet)

    def keyPressRight(self, eve):
        if 'RIGHT' not in self.game.players[self.game.playerId].camera.movingDirection:
            self.game.players[self.game.playerId].camera.movingDirection.append('RIGHT')
            if self.game.players[self.game.playerId].currentPlanet == None:
                self.drawWorld()
            else:
                self.drawPlanetGround(self.game.players[self.game.playerId].currentPlanet)

    #Actions quand on lache les touches
    def keyReleaseUP(self, eve):
        self.game.players[self.game.playerId].camera.movingDirection.remove('UP')
        if self.game.players[self.game.playerId].currentPlanet == None:
            self.drawWorld()
        else:
            self.drawPlanetGround(self.game.players[self.game.playerId].currentPlanet)

    def keyReleaseDown(self, eve):
        self.game.players[self.game.playerId].camera.movingDirection.remove('DOWN')
        if self.game.players[self.game.playerId].currentPlanet == None:
            self.drawWorld()
        else:
            self.drawPlanetGround(self.game.players[self.game.playerId].currentPlanet)

    def keyReleaseLeft(self, eve):
        self.game.players[self.game.playerId].camera.movingDirection.remove('LEFT')
        if self.game.players[self.game.playerId].currentPlanet == None:
            self.drawWorld()
        else:
            self.drawPlanetGround(self.game.players[self.game.playerId].currentPlanet)

    def keyReleaseRight(self, eve):
        self.game.players[self.game.playerId].camera.movingDirection.remove('RIGHT')
        if self.game.players[self.game.playerId].currentPlanet == None:
            self.drawWorld()
        else:
            self.drawPlanetGround(self.game.players[self.game.playerId].currentPlanet)

    #Actions avec la souris    
    def rightclic(self, eve):
        self.attacking = False
        x = eve.x
        y = eve.y
        canva = eve.widget
        if x > 0 and x < self.taille:
            if y > 0 and y < self.taille-200:
                if canva == self.gameArea:
                    pos = self.game.players[self.game.playerId].camera.calcPointInWorld(x,y)
                    self.game.rightClic(pos)
                elif canva == self.minimap and self.game.getCurrentPlanet() == None:
                    pos = self.game.players[self.game.playerId].camera.calcPointMinimap(x,y)
                    self.game.setMovingFlag(pos[0], pos[1])
                    self.drawWorld()

    #Quand on fait un clic gauche (peu importe ou)
    def leftclic(self, eve):
        x = eve.x
        y = eve.y
        canva = eve.widget
        if canva == self.gameArea:
            pos = self.game.players[self.game.playerId].camera.calcPointInWorld(x,y)
            if self.attacking or self.isSettingAttackPosition:
                self.game.selectUnitEnemy(pos)
                self.isSettingAttackPosition = False
                self.actionMenuType = self.MAIN_MENU
                    
            elif self.isSettingRallyPointPosition:
                self.game.setMotherShipRallyPoint(pos)
                self.isSettingRallyPointPosition = False
                self.actionMenuType = self.MAIN_MENU
                    
            elif self.isSettingPatrolPosition:
                self.game.setPatrolFlag(pos)
                self.isSettingPatrolPosition = False
                self.actionMenuType = self.MAIN_MENU
                    
            elif self.isSettingMovePosition:
                self.game.setMovingFlag(pos[0],pos[1])
                self.isSettingMovePosition = False
                self.actionMenuType = self.MAIN_MENU
                
            elif self.isSettingBuildingPosition or self.building:
                self.game.setBuildingFlag(pos[0],pos[1])
                self.isSettingBuildingPosition = False
                self.actionMenuType = self.MAIN_MENU
                    
            else:
                if not self.selectAllUnits:
                    self.game.select(pos)
                    self.ongletSelectedUnit()
                    self.selectedOnglet = self.SELECTED_UNIT_SELECTED
                else:
                    self.game.selectAll(pos)
                    self.ongletSelectedUnit()
                    self.selectedOnglet = self.SELECTED_UNIT_SELECTED
        elif canva == self.minimap:
            self.game.quickMove(x,y)

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
            self.game.boxSelect(self.selectStart, self.selectEnd)
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
        self.game.setStandbyFlag()

    def delete(self, eve):
        self.attacking = False
        self.game.eraseUnit()
        
    #Pour la selection multiple	
    def shiftPress(self, eve):
        self.game.multiSelect = True

    def shiftRelease(self, eve):
        self.game.multiSelect = False

    def checkMotherShip(self, eve):
        self.game.players[self.game.playerId].currentPlanet = None
        cam = self.game.players[self.game.playerId].camera
        cam.position = [cam.defaultPos[0], cam.defaultPos[1]]
        self.game.players[self.game.playerId].selectedObjects = []
        self.game.players[self.game.playerId].selectedObjects.append(self.game.players[self.game.playerId].motherShip)
        self.changeBackground('GALAXY')
        self.drawWorld()
        self.redrawMinimap()
        self.ongletSelectedUnit()

    def clickMenuModes(self,eve):
        bp = (eve.widget.gettags(eve.widget.find_withtag('current')))
        if bp != ():
            Button_pressed = bp[0]
            if (Button_pressed == "bouton_chat"):
                self.ongletChat(self.gameFrame)
            elif (Button_pressed == "bouton_trade"):
                if self.game.tradePage==-1:
                    self.ongletTradeChoicePlayer()
                elif self.game.tradePage==1:
                    self.ongletTradeWaiting()
                elif self.game.tradePage==2:
                    if self.game.isMasterTrade == True:
                        self.ongletTrade(self.game.playerId,self.game.idTradeWith)
                    else:
                        self.ongletTrade(self.game.idTradeWith,self.game.playerId)
                elif self.game.tradePage==3:
                    self.ongletTradeYesNoQuestion(self.game.idTradeWith)
                elif self.game.tradePage==4:
                    self.ongletTradeAskConfirm(self.game.idTradeWith,self.game.toTrade[0],self.game.toTrade[1],self.game.toTrade[2],self.game.toTrade[3])
            elif (Button_pressed == "bouton_team"):
                self.ongletTeam()
            elif (Button_pressed == "bouton_selectedUnit"):
                self.ongletSelecteUdnit()
            elif (Button_pressed == "selected_unit"):
                self.game.select((float(bp[1]), float(bp[2])))
                self.ongletSelectedUnit()
            elif (Button_pressed == 'cancelUnitButton'):
                self.game.sendCancelUnit(bp[1])
            elif (Button_pressed == 'selected_all_units'):
                self.game.selectUnitByType(int(bp[1]))


    def takeOff(self, eve):
        planet = self.game.players[self.game.playerId].currentPlanet
        if planet != None:
            for i in planet.landingZones:
                if i.ownerId == self.game.playerId and i.LandedShip != None:
                    if i in self.game.players[self.game.playerId].selectedObjects:
                        self.game.setTakeOffFlag(i.LandedShip, planet)

    def clickActionMenu(self,eve):
        bp = (eve.widget.gettags(eve.widget.find_withtag('current')))
        if bp != ():
            Button_pressed = bp[0]
            if (Button_pressed == "Button_Stop"):
                self.game.setStandbyFlag()
            elif (Button_pressed == "Button_RallyPoint"):
                self.actionMenuType = self.WAITING_FOR_RALLY_POINT_MENU
                self.isSettingRallyPointPosition = True
            elif (Button_pressed == "Button_Build"):
                self.actionMenuType = self.MOTHERSHIP_BUILD_MENU
            elif (Button_pressed == "Button_Patrol"):
                self.actionMenuType = self.WAITING_FOR_PATROL_POINT_MENU
                self.isSettingPatrolPosition = True
            elif (Button_pressed == "Button_Attack"):
                self.actionMenuType = self.WAITING_FOR_ATTACK_POINT_MENU
                self.isSettingAttackPosition = True
            elif (Button_pressed == "Button_Build_Waypoint"):
                self.actionMenuType = self.WAITING_FOR_BUILDING_POINT_MENU
                self.isSettingBuildingPosition = True;
            elif (Button_pressed == "Button_Move"):
                self.actionMenuType = self.WAITING_FOR_MOVE_POINT_MENU
                self.isSettingMovePosition = True
            elif (Button_pressed == "Button_Tech"):
                self.actionMenuType = self.TECHNOLOGY_TREE_MENU
            elif (Button_pressed == "Button_Tech_Units"):
                self.actionMenuType = self.TECHTREE_UNIT_MENU
            elif (Button_pressed == "Button_Tech_Buildings"):
                self.actionMenuType = self.TECHTREE_BUILDING_MENU
            elif (Button_pressed == "Button_Tech_Mothership"):
                self.actionMenuType = self.TECHTREE_MOTHERSHIP_MENU
            elif (Button_pressed == "Button_Return"):
                self.actionMenuType = self.MAIN_MENU
            elif (Button_pressed == "Button_Build_Scout"):
                self.game.addUnit(Unit.SCOUT)
            elif (Button_pressed == "Button_Build_Attack"):
                self.game.addUnit(Unit.ATTACK_SHIP)
            elif (Button_pressed == "Button_Build_Transport"):
                self.game.addUnit(Unit.TRANSPORT)
            elif (Button_pressed == "Button_Build_Gather"):
                self.game.addUnit(Unit.CARGO)
            elif (Button_pressed == "Button_Triangle"):
                self.game.setChangeFormationFlag('t')
            elif (Button_pressed == "Button_Square"):
                self.game.setChangeFormationFlag('c')
            elif len(Button_pressed.split("/")) == 2:
                #Si on achète une nouvelle technologie
                Button_pressed = Button_pressed.split("/")
                self.game.setBuyTech(Button_pressed[0], Button_pressed[1])
                
    def progressCircleMouseOver(self,eve):
        tag = self.menuModes.gettags(self.menuModes.find_withtag('current'))
        if tag != ():
            if tag[0] == 'arc':
                self.wantToCancelUnitBuild = True
        else:
            self.wantToCancelUnitBuild = False

    def enterChat(self,eve):
        self.ongletChat(self.gameFrame)
        self.selectedOnglet = self.SELECTED_CHAT
        self.menuModes.entryMess.focus_set()

    def deleteAll(self):
        self.gameArea.delete(ALL)
    
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
        self.gameArea.bind("a",self.attack)
        self.gameArea.bind("A",self.attack)
        self.gameArea.bind("c", self.selectAll)
        self.gameArea.bind("t", self.takeOff)
        self.gameArea.bind("T", self.takeOff)
        self.gameArea.bind("<KeyRelease-c>", self.unSelectAll)
        self.gameArea.bind("1", self.checkMotherShip)
        self.gameArea.bind("<Control_L>",self.ctrlPressed)
        self.gameArea.bind("<KeyRelease-Control_L>",self.ctrlDepressed)
        self.gameArea.bind("<Tab>",self.enterChat)
        #Bindings des boutons de la souris
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
        self.menuModes.bind("<Motion>", self.progressCircleMouseOver)
        self.Actionmenu.bind("<Button-1>", self.clickActionMenu)

