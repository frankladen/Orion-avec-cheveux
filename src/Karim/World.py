# -*- coding: iso-8859-1 -*-
import random
from Target import *
#Echelle pour les objets de la galaxie:
#Grandeur: (1000x1000)xNbJoueur
#Un systeme solaire: 200x200
#Un soleil(�toile): 8x8
#une plan�te: 4x4
#Vaisseau m�re: 3x3
#WayPoint: 2x2
#Autres vaisseau: 1x1
#Ceci n'est qu'une �chelle donc n'importe quel grandeur dans la vue est bonne
#tant qu'on respecte cette �chelle pour les grandeurs

#Classe qui represente la galaxie en entier.
class Galaxy():
    def __init__(self,nbPlayer, seed):
        self.width=(nbPlayer)*1000
        self.height=(nbPlayer)*1000
        self.depth=(nbPlayer)*1000
        random.seed(seed)
        self.solarSystemList = []
        for i in range(1,nbPlayer*(6+(nbPlayer-2))):
            tempX=""
            tempY=""
            placeFound = False
            while placeFound == False:
                tempX=(random.random()*self.width)-self.width/2
                tempY=(random.random()*self.height)-self.height/2
                placeFound = True
                #Conditions de placement des soleils
                if tempX < -1*(self.width/2)+150 or tempX > self.width/2-150:
                    placeFound = False
                if tempY < -1*(self.height/2)+150 or tempY > self.height/2-150: 
                    placeFound = False
                for j in self.solarSystemList:
                    if tempX > j.sunPosition[0]-250 and tempX < j.sunPosition[0]+250:
                        if tempY > j.sunPosition[1]-250 and tempY < j.sunPosition[1]+250:
                            placeFound = False
            self.solarSystemList.append(SolarSystem(tempX,tempY,0))
#Classe qui represente 1 seul systeme solaire                            
class SolarSystem():
    def __init__(self,sunX,sunY,sunZ):
        self.sunPosition = (sunX,sunY,sunZ)
        self.planets = []
        nPlanet = int(random.random()*6)+1
        for i in range(0,nPlanet):
            tempX=""
            tempY=""
            placeFound = False
            while placeFound == False:
                placeFound = True
                tempX = (random.random()*250)-125
                tempY = (random.random()*250)-125
                #Condition de placement des planetes
                if tempX > -40 and tempX < 40:
                    if tempY > -40 and tempY < 40:
                        placeFound = False
                for j in self.planets:
                    if self.sunPosition[0]+tempX > j.position[0]-20 and self.sunPosition[0]+tempX < j.position[0]+20:
                        if self.sunPosition[1]+tempY > j.position[1]-20 and self.sunPosition[1]+tempY < j.position[1]+20:
                            placeFound = False
            self.planets.append(AstronomicalObject('planet', (self.sunPosition[0]+tempX,self.sunPosition[1]+tempY)))
    
#Represente un objet spacial (Planete, Meteorite, Nebuleuse)
#Le type represente quel objet parmi les 3
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
        