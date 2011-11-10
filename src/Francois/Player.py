# -*- coding: UTF-8 -*-
from Unit import *
from Flag import *
import socket

#Represente un joueur
class Player():
    def __init__(self, name, id , colorId, parent):
        self.name = name
        self.id = id #Numero du joueur dans la liste de joueur
        self.parent = parent
        self.colorId = colorId
        self.selectedObjects = [] #Liste des unites selectionnes
        self.units = [] #Liste de toute les unites
        self.diplomacies=[]
        for i in range(8):
            self.diplomacies.append('Enemy')
        self.diplomacies[self.id] = 'Ally'
        self.startPos = [0,0,0] #Position de depart du joueur (pour le mothership)
        self.motherShip = None
        self.formation="carre"
        self.currentPlanet = None
        self.gaz = 100
        self.mineral = 100

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
        
    def changeDiplomacy(self, playerToChange, newStatus):
        self.diplomacies[playerToChange] = newStatus
            
    def inViewRange(self, position):
        x = position[0]
        y = position[1]
        for i in self.units:
            if i.isAlive:
                if x > i.position[0]-i.viewRange and x < i.position[0]+i.viewRange:
                    if y > i.position[1]-i.viewRange and y < i.position[1]+i.viewRange:
                        if i.name == 'Transport':
                            if not i.landed:
                                return True
                        else:
                            return True
        for i in range(len(self.diplomacies)):
            if self.isAlly(i) and i != self.id:
                for i in self.parent.players[i].units:
                    if i.isAlive:
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
            return self.parent.isAllied(playerId, self.id)
        return False

#Represente la camera            
class Camera():
    def __init__(self, defaultPos, galaxy, player, taille):
        self.defaultPos = defaultPos
        self.position = defaultPos
        self.screenCenter = (taille/2,(taille/2)-100)
        self.screenWidth = taille
        self.screenHeight = taille-200
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


