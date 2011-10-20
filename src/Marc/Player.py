import Unit as u
from Flag import *
import socket

#Represente un joueur
class Player():
    def __init__(self, name, id ,civilization=None):
        self.name = name
        self.civilization = civilization
        self.selectedObjects = [] #Liste des unites selectionnes
        self.units = [] #Liste de toute les unites
        self.id = id #Numero du joueur dans la liste de joueur
        self.startPos = [0,0,0] #Position de depart du joueur (pour le mothership)
        self.gaz = 0
        self.mineral = 0

    def addBaseUnits(self, startPos):
        self.units.append(u.Mothership('Mothership',startPos, self.id))
        self.units.append(u.Unit('Scout',[startPos[0] + 20, startPos[1] + 20 ,0], self.id, moveSpeed=4.0))
        self.units.append(u.Unit('Scout',[startPos[0] - 20, startPos[1] - 20 ,0], self.id, moveSpeed=4.0))
        self.units.append(u.SpaceAttackUnit('Attack',[startPos[0] + 30, startPos[1] - 30 ,0], self.id, moveSpeed=2.0, attackspeed=10.0,attackdamage=5.0,range=150.0))

    #Ajoute une camera au joueur seulement quand la partie commence    
    def addCamera(self, galaxy):
        pos = [0,0,0]
        for i in self.units:
            if i.name == 'Mothership':
                pos = i.position
        default = [pos[0],pos[1]]
        self.camera = Camera(default,galaxy)
        if default[0]-self.camera.screenCenter[0] < (self.camera.galaxy.width*-1)/2:
            self.camera.position[0] = (self.camera.galaxy.width*-1)/2+self.camera.screenCenter[0]
        if default[0]+self.camera.screenCenter[0] > self.camera.galaxy.width/2:
            self.camera.position[0] = (self.camera.galaxy.width)/2-self.camera.screenCenter[0]
        if default[1]-self.camera.screenCenter[1] < (self.camera.galaxy.height*-1)/2:
            self.camera.position[1] = (self.camera.galaxy.height*-1)/2+self.camera.screenCenter[1]
        if default[1]+self.camera.screenCenter[1] > self.camera.galaxy.height/2:
            self.camera.position[1] = (self.camera.galaxy.height)/2-self.camera.screenCenter[1]
        
    def inViewRange(self, position):
        x = position[0]
        y = position[1]
        for i in self.units:
            if x > i.position[0]-i.viewRange and x < i.position[0]+i.viewRange:
                if y > i.position[1]-i.viewRange and y < i.position[1]+i.viewRange:
                    return True
        return False
#Represente la camera            
class Camera():
    def __init__(self, defaultPos, galaxy):
        self.position = defaultPos
        self.screenCenter = (400,300)
        self.screenWidth = 800
        self.screenHeight = 600
        self.galaxy = galaxy #reference a la galaxie
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
    #Deplace la camera selon le contenu de la liste movingDirection
    def move(self):
        if 'LEFT' in self.movingDirection:
            if self.position[0] > (self.galaxy.width*-1)/2+self.screenCenter[0]:
                self.position[0]-=5
        elif 'RIGHT' in self.movingDirection:
            if self.position[0] < self.galaxy.width/2 - self.screenCenter[0]:
                self.position[0]+=5
        if 'UP' in self.movingDirection:
            if self.position[1] > (self.galaxy.height*-1)/2 + self.screenCenter[1]:
                self.position[1]-=5
        elif 'DOWN' in self.movingDirection:
            if self.position[1] < self.galaxy.height/2 - self.screenCenter[1]:
                self.position[1]+=5


