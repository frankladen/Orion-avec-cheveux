# -*- coding: UTF-8 -*-
from Unit import *
from Flag import *
import socket

#Represente un joueur
class Player():
    MINERAL = 0
    GAS = 1
    FOOD = 2
    def __init__(self, name, game, id , colorId):
        self.name = name
        self.game = game
        self.colorId = colorId
        self.selectedObjects = [] #Liste des unites selectionnes
        self.units = [] #Liste de toute les unites
        self.id = id #Numero du joueur dans la liste de joueur
        self.diplomacies=[]
        for i in range(8):
            self.diplomacies.append('Enemy')
        self.diplomacies[self.id] = 'Ally'
        self.startPos = [0,0,0] #Position de depart du joueur (pour le mothership)
        self.motherShip = None
        self.formation="carre"
        self.currentPlanet = None
        self.ressources = [100,100,10]
        self.isAlive = True

    def action(self):
        for i in self.units:
            if i.isAlive:
                i.action(self)
        
    def addBaseUnits(self, startPos):
        self.units.append(Mothership('Mothership', Unit.MOTHERSHIP,startPos, self.id))
        self.motherShip = self.units[0]
        self.units.append(Unit('Scout', Unit.SCOUT,[startPos[0] + 20, startPos[1] + 20 ,0], self.id))
        self.units.append(GatherShip('Gather ship', Unit.CARGO,[startPos[0] + 40, startPos[1]+40], self.id))
        
    #Ajoute une camera au joueur seulement quand la partie commence    
    def addCamera(self, galaxy, taille):
        pos = [0,0,0]
        for i in self.units:
            if i.type == i.MOTHERSHIP:
                pos = i.position
        default = [pos[0],pos[1]]
        self.camera = Camera(default, galaxy, self, taille)
        if default[0]-self.camera.screenCenter[0] < (self.camera.galaxy.width*-1)/2:
            self.camera.position[0] = (self.camera.galaxy.width*-1)/2+self.camera.screenCenter[0]
        if default[0]+self.camera.screenCenter[0] > self.camera.galaxy.width/2:
            self.camera.position[0] = (self.camera.galaxy.width)/2-self.camera.screenCenter[0]
        if default[1]-self.camera.screenCenter[1] < (self.camera.galaxy.height*-1)/2:
            self.camera.position[1] = (self.camera.galaxy.height*-1)/2+self.camera.screenCenter[1]
        if default[1]+self.camera.screenCenter[1] > self.camera.galaxy.height/2:
            self.camera.position[1] = (self.camera.galaxy.height)/2-self.camera.screenCenter[1]

    def moveCamera(self):
        self.camera.move()

    def changeDiplomacy(self, playerToChange, newStatus):
        self.diplomacies[playerToChange] = newStatus
    
    def inViewRange(self, position):
        x = position[0]
        y = position[1]
        for i in self.units:
            if i.isAlive and not isinstance(i, GroundUnit):
                if x > i.position[0]-i.viewRange and x < i.position[0]+i.viewRange:
                    if y > i.position[1]-i.viewRange and y < i.position[1]+i.viewRange:
                        if i.name == 'Transport':
                            if not i.landed:
                                return True
                        else:
                            return True
        for i in range(len(self.diplomacies)):
            if self.isAlly(i) and i != self.id:
                for i in self.game.players[i].units:
                    if i.isAlive and not isinstance(i, GroundUnit):
                        if x > i.position[0]-i.viewRange and x < i.position[0]+i.viewRange:
                            if y > i.position[1]-i.viewRange and y < i.position[1]+i.viewRange:
                                if i.name == 'Transport':
                                    if not i.landed:
                                        return True
                                else:
                                    return True
        return False
    
    def isAlly(self, playerId):
        if self.diplomacies[playerId] == "Ally":
            return self.game.isAllied(playerId, self.id)
        return False

    def killUnit(self, killedIndexes):
        if killedIndexes[1] == self.id:
            if self.units[killedIndexes[0]] in self.selectedObjects:
               self.selectedObjects.remove(self.units[killedIndexes[0]])
        self.game.killUnit(killedIndexes)

    def buildUnit(self):
        unit = self.motherShip.unitBeingConstruct.pop(0)
        if unit.type == u.Unit.TRANSPORT:
            pilot = u.GroundUnit('Builder', u.Unit.GROUND_UNIT, [-10000,-10000,-10000], self.id,-1,-1)
            unit.units.append(pilot)
            self.units.append(pilot)
        unit.changeFlag(t.Target(self.motherShip.rallyPoint), FlagState.MOVE)
        self.units.append(unit)

    def sendKill(self):
        self.parent.sendKillPlayer(self.id)

    def kill(self):
        self.isAlive = False
        for i in self.units:
            i.kill
            
    def adjustRessources(self, ressourceType, amount):
        self.ressources[ressourceType] += amount

    def cancelUnit(self, unitId):
        unit = self.motherShip.getUnitBeingConstructAt(unitId)
        self.adjustRessources(self.MINERAL, unit.buildCost[0])
        self.adjustRessources(self.GAS, unit.buildCost[1])
        self.motherShip.changeFlag(unitId, FlagState.CANCEL_UNIT)

    def canAfford(self, minerals, gas, food=0):
        return self.ressources[0] >= minerals and self.ressources[0] >= gas# and self.ressources[0] >= food

    def createUnit(self, unitType):
        self.motherShip.addUnitToQueue(unitType)
        self.ressources[self.MINERAL] -= Unit.BUILD_COST[unitType][Unit.MINERAL]
        self.ressources[self.GAS] -= Unit.BUILD_COST[unitType][Unit.GAS]
        self.motherShip.flag.flagState = FlagState.BUILD_UNIT

    def makeUnitsAttack(self, units, targetPlayer, targetUnit):
        for i in units:
            if i != '':
                self.units[int(i)].changeFlag(targetPlayer.units[targetUnit], FlagState.ATTACK)

    def makeUnitLand(self, unitId, planet):
        self.units[unitId].changeFlag(planet, FlagState.LAND)

    def makeUnitsGather(self, units, astroObject):
        for i in units:
            if i != '':
                self.units[int(i)].changeFlag(astroObject, FlagState.GATHER)

    def makeFormation(self, units, target = None, action = FlagState.MOVE):
        if target == None:
            target = self.units[int(units[0])].flag.finalTarget.position
        lineTaken=[]
        line=0
        targetorig=[0,0]
        targetorig[0]=target[0]
        targetorig[1]=target[1]
        widths = []
        heights = []
        for i in range(0,len(units)-1):
            unit = self.units[int(units[i])]
            widths.append(unit.SIZE[unit.type][0])
            heights.append(unit.SIZE[unit.type][1])
        width = max(widths)
        height = max(heights)
        #Formation en carré selon le nombre de unit qui se déplace, OH YEAH
        if self.formation == "carre":
            thatLine = []
            lineTaken = []
            numberOfLines = math.sqrt(len(units)-1)
            if str(numberOfLines).split('.')[1] != '0':
                numberOfLines+=1
            math.trunc(float(numberOfLines))
            numberOfLines = int(numberOfLines)
            for l in range(0,numberOfLines):
                thatLine = []
                for k in range(0,numberOfLines):
                    thatLine.append(False)
                lineTaken.append(thatLine)
            for i in range(0,len(units)-1):
                goodPlace=False
                line=0
                while goodPlace==False:
                    for p in range(0,len(lineTaken[line])):
                        if lineTaken[line][p]==False:
                            lineTaken[line][p]=True
                            target[0]=targetorig[0]+(p*20)
                            if target[0] < -1*(self.game.galaxy.width/2)+9:
                                target[0] = -1*(self.game.galaxy.width/2)+18
                            elif target[0] > (self.game.galaxy.width/2)-9:
                                target[0] = (self.game.galaxy.width/2)-18
                            target[1]=targetorig[1]-(line*20)
                            if target[1] < -1*(self.game.galaxy.height/2)+9:
                                target[1] = -1*(self.game.galaxy.height/2)+18
                            goodPlace=True
                            break
                    if goodPlace==False:
                        line+=1
                        if (len(lineTaken)-1)<line:
                            numberOfSpaces=1+line
                            thatLine=[]
                            for a in range(0,numberOfSpaces):
                                thatLine.append(False)
                            lineTaken.append(thatLine)
                self.units[int(units[i])].changeFlag(t.Target([target[0],target[1],target[2]]),int(action))
        #Formation en triangle, FUCK YEAH
        elif self.formation == "triangle":
            thatLine=[]
            xLineBefore=[0,0,0,0,0,0,0,0,0,0,0,0]
            thatLine.append([False])
            lineTaken.append(thatLine[False])
            for i in range(0,len(units)-1):
                goodPlace=False
                line=0
                while goodPlace==False:
                    for p in range(0,len(lineTaken[line])):
                        if lineTaken[line][p]==False:
                            lineTaken[line][p]=True
                            if line != 0:
                                if p==len(lineTaken[line-1]):
                                    target[0]=targetorig[0]+(p*width)
                                    #jerome ajoute ca ici la largeur du vaisseau
                                    if target[0] > (self.game.galaxy.width/2)-9:
                                        target[0] = target[0]-(target[0]-(self.game.galaxy.width/2)+18)
                                    xLineBefore[p] = target[0]
                                else:
                                    target[0]=xLineBefore[p]-width
                                    if target[0] < -1*(self.game.galaxy.width/2)+9:
                                        target[0] = xLineBefore[p]
                                    elif target[0] > (self.game.galaxy.width/2)-9:
                                        target[0] = target[0]-(target[0]-(self.game.galaxy.width/2)+18)
                                    xLineBefore[p] = target[0]
                            target[1]=targetorig[1]-(line*height)
                            if target[1] < -1*(self.galaxy.height/2)+9:
                                target[1] = targetorig[1]
                            goodPlace=True
                            break
                    if goodPlace==False:
                        line+=1
                        if (len(lineTaken)-1)<line:
                            numberOfSpaces=1+line
                            thatLine=[]
                            for a in range(0,numberOfSpaces):
                                thatLine.append(False)
                            lineTaken.append(thatLine)
                    if line == 0:
                        xLineBefore[0] = target[0]
                self.units[int(units[i])].changeFlag(t.Target([target[0],target[1],target[2]]),int(action))
        
#Represente la camera            
class Camera():
    def __init__(self, defaultPos, galaxy, player, taille):
        self.defaultPos = defaultPos
        self.position = defaultPos
        self.screenCenter = (taille/2,(taille/2)-300)
        self.screenWidth = taille
        self.screenHeight = taille/2
        self.galaxy = galaxy #reference a la galaxie
        self.player = player
        self.movingDirection = []
        
    #Pour calculer la distance entre la camera et un point
    def calcDistance(self, position):
        distX = position[0] - self.position[0]
        distY = position[1] - self.position[1]
        return [distX+self.screenCenter[0], distY+self.screenCenter[1]]
    
    #Pour calculer un point dans la galaxie a partir d'un point dans l'ecran
    def calcPointInWorld(self, x,y):
        dist = self.calcDistance([x,y])
        rX = self.position[0]-self.screenCenter[0]+x
        rY = self.position[1]-self.screenCenter[1]+y
        return [rX,rY,0]
    
    #Pour calculer un point sur la minimap a partir d'un point dans l'espace
    def calcPointOnMap(self, x, y):
        rX = x/200 * self.galaxy.width - self.galaxy.width/2
        rY = y/200 * self.galaxy.height - self.galaxy.height/2
        if rX < 0-self.galaxy.width/2+self.screenWidth/2:
            rX = 0-self.galaxy.width/2+self.screenWidth/2
        elif rX > self.galaxy.width/2-self.screenWidth/2:
            rX = self.galaxy.width/2-self.screenWidth/2
            
        if rY < 0-self.galaxy.height/2+self.screenHeight/2:
            rY = 0-self.galaxy.height/2+self.screenHeight/2
        elif rY > self.galaxy.height/2-self.screenHeight/2:
            rY = self.galaxy.height/2-self.screenHeight/2
        return [rX, rY]
		
    def calcPointOnPlanetMap(self, x, y):
        rX = x * self.player.currentPlanet.WIDTH / 200
        rY = y * self.player.currentPlanet.HEIGHT / 200
        if rX < 0 + self.screenWidth/2:
            rX = 0 + self.screenWidth/2
        elif rX > self.player.currentPlanet.WIDTH - self.screenWidth/2:
            rX = self.player.currentPlanet.WIDTH - self.screenWidth/2
        if rY < 0 + self.screenHeight/2:
            rY = 0 + self.screenHeight/2
        elif rY > self.player.currentPlanet.HEIGHT - self.screenHeight/2:
            rY = self.player.currentPlanet.HEIGHT - self.screenHeight/2
        return [rX, rY]
    
    #Pour calculer un point dans la galaxie a partir d'un point dans la minimap
    def calcPointMinimap(self,x ,y ):
        rX = x/200 * self.galaxy.width - self.galaxy.width/2
        rY = y/200 * self.galaxy.height - self.galaxy.height/2
        return [rX, rY]
    
    #Retourne Vrai si la position est visible par la camera en ce moment
    def isInFOV(self, position):
        if position[0] > self.position[0]-self.screenWidth/2-20 and position[0] < self.position[0]+self.screenWidth/2+20:
            if position[1] > self.position[1]-self.screenHeight/2-20 and position[1] < self.position[1]+self.screenHeight/2+20:
                return True
        return False

    def placeOnLanding(self):
        planet = self.player.currentPlanet
        if self.position[0]-self.screenCenter[0] < 0:
            self.position[0] = 0 + self.screenCenter[0]
        if self.position[0] + self.screenCenter[0] > planet.WIDTH:
            self.position[0] = planet.WIDTH-self.screenCenter[0]
        if self.position[1] - self.screenCenter[1] < 0:
            self.position[1] = 0+self.screenCenter[1]
        if self.position[1] + self.screenCenter[1] > planet.HEIGHT:
            self.position[1] = planet.HEIGHT - self.screenCenter[1]

    def placeOverPlanet(self):
        if self.position[0]-self.screenCenter[0] < (self.galaxy.width*-1)/2:
            self.position[0] = (self.galaxy.width*-1)/2+self.screenCenter[0]
        if self.position[0]+self.screenCenter[0] > self.galaxy.width/2:
            self.position[0] = (self.galaxy.width)/2-self.screenCenter[0]
        if self.position[1]-self.screenCenter[1] < (self.galaxy.height*-1)/2:
            self.position[1] = (self.galaxy.height*-1)/2+self.screenCenter[1]
        if self.position[1]+self.screenCenter[1] > self.galaxy.height/2:
            self.position[1] = (self.galaxy.height)/2-self.screenCenter[1]

    #Deplace la camera selon le contenu de la liste movingDirection
    def move(self):
        if self.player.currentPlanet == None:
            if 'LEFT' in self.movingDirection:
                if self.position[0] > (self.galaxy.width*-1)/2+self.screenCenter[0]:
                    self.position[0]-=10
            elif 'RIGHT' in self.movingDirection:
                if self.position[0] < self.galaxy.width/2 - self.screenCenter[0]:
                    self.position[0]+=10
            if 'UP' in self.movingDirection:
                if self.position[1] > (self.galaxy.height*-1)/2 + self.screenCenter[1]:
                    self.position[1]-=10
            elif 'DOWN' in self.movingDirection:
                if self.position[1] < self.galaxy.height/2 - self.screenCenter[1]:
                    self.position[1]+=10
        else:
            planet = self.player.currentPlanet
            if 'LEFT' in self.movingDirection:
                if self.position[0] > 0 + self.screenCenter[0]:
                    self.position[0]-=20
                else:
                    self.position[0] = self.screenCenter[0]
            elif 'RIGHT' in self.movingDirection:
                if self.position[0] < planet.WIDTH - self.screenCenter[0]:
                    self.position[0]+=20
                else:
                    self.position[0] = planet.WIDTH - self.screenCenter[0]
            if 'UP' in self.movingDirection:
                if self.position[1] > 0 + self.screenCenter[1]:
                    self.position[1]-=20
                else:
                    self.position[1] = self.screenCenter[1]
            elif 'DOWN' in self.movingDirection:
                if self.position[1] < planet.HEIGHT - self.screenCenter[1]:
                    self.position[1]+=20
                else:
                    self.position[1] = planet.HEIGHT - self.screenCenter[1]


