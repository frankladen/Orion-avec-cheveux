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
                tempX=(random.random()*self.width)-self.width/2
                tempY=(random.random()*self.height)-self.height/2
                placeFound = True
                for j in self.solarSystemList:
                    if tempX > j.sunPosition[0]-150 and tempX < j.sunPosition[0]+150:
                        if tempY > j.sunPosition[1]-150 and tempY > j.sunPosition[1]+150:
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
                if tempX > self.sunPosition[0]+10 or tempX < self.sunPosition[0]-10:
                    if tempY > self.sunPosition[1]+10 or tempY < self.sunPosition[1]-10:
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
        