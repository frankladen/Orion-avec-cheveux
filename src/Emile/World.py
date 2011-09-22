# -*- coding: iso-8859-1 -*-
import random

#Echelle pour les objets de la galaxie:
#Grandeur: (1000x1000)xNbJoueur
#Un systeme solaire: 200x200
#Un soleil(étoile): 8x8
#une planète: 4x4
#Vaisseau mère: 3x3
#WayPoint: 2x2
#Autres vaisseau: 1x1
#Ceci n'est qu'une échelle donc n'importe quel grandeur dans la vue est bonne
#tant qu'on respecte cette échelle pour les grandeurs
class Galaxy():
    def __init__(self,nbPlayer):
    	self.width=(nbPlayer)*1000
    	self.height=(nbPlayer)*1000
    	self.depth=(nbPlayer)*1000
    	self.solarSystemList = []
    	for i in range(1,nbPlayer*6):
            tempX=""
            tempY=""
            placeFound = False
            while placeFound == False:
                tempX=random.random()*1000*i
                tempY=random.random()*1000*i
                placeFound = True
                for j in self.solarSystemList:
                    if tempX > j.sunPosition[0]-100 and tempX < j.sunPosition[0]+100:
                        if tempY > j.sunPosition[1]-100 and tempY > j.sunPosition[1]+100:
                            placeFound = False
            print(tempX,tempY)
            self.solarSystemList.append(SolarSystem(tempX,tempY,0))
                            
class SolarSystem():
    def __init__(self,sunX,sunY,sunZ):
        self.sunPosition = (sunX,sunY,sunZ)
        self.planets = []
        nPlanet = int(random.random()*6)+1
        for i in range(1,nPlanet):
            tempX=""
            tempY=""
            placeFound = False
            while placeFound == False:
                tempX = (random.random()*200)-100
                tempY = (random.random()*200)-100
                placeFound = True
            print("planet ",i,tempX,tempY)
            self.planets.append(AstronomicalObject('planet', (self.sunPosition[0]+tempX,self.sunPosition[1]+tempY)))
                                
class Target():
    def __init__(self, position):
        self.position = position

class AstronomicalObject(Target):
    def __init__(self, type, position):
        Target.__init__(self, position)
        self.type = type
        self.mineralQte = 100
        self.gazQte = 100
        if type == 'planet':
            self.landable = True
        else:
            self.landable = False
        

class Camera():
    def __init__(self, defaultPos):
        self.position = defaultPos
        self.screenCenter = (400,400)
        self.screenWidth = 800
        self.screenHeight = 800
    
    def calcDistance(self, position):
        distX = position[0] - self.position[0]
        distY = position[1] - self.position[1]
        return [distX+self.screenCenter[0], distY+self.screenCenter[1]]
    
    def isInFOV(self, position):
        if position[0] > self.position[0]-self.screenWidth/2-20 and position[0] < self.position[0]+self.screenWidth/2+20:
            if position[1] > self.position[1]-self.screenHeight/2-20 and position[1] < self.position[1]+self.screenHeight/2+20:
                return True
        return False
    
    def move(self, direction):
        if direction == 'LEFT':
            self.position[0]-=5
        elif direction == 'RIGHT':
            self.position[0]+=5
        elif direction == 'UP':
            self.position[1]-=5
        elif direction == 'DOWN':
            self.position[1]+=5
        print("CamPos: ", self.position)


