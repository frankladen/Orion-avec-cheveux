# -*- coding: UTF-8 -*-
import random
from Target import *
import math
from Constants import *
#Echelle pour les objets de la galaxie:
#Grandeur: (1000x1000)xNbJoueur
#Un systeme solaire: 200x200
#Un soleil(ï¿½toile): 8x8
#une planï¿½te: 4x4
#Vaisseau mï¿½re: 3x3
#WayPoint: 2x2
#Autres vaisseau: 1x1
#Ceci n'est qu'une ï¿½chelle donc n'importe quel grandeur dans la vue est bonne
#tant qu'on respecte cette ï¿½chelle pour les grandeurs

#Classe qui represente la galaxie en entier.
class Galaxy():
    def __init__(self,nbPlayer, seed):
        self.width=(nbPlayer)*GalaxySize.WORLD_SIZE_MULTIPLIER
        self.height=(nbPlayer)*GalaxySize.WORLD_SIZE_MULTIPLIER
        self.depth=(nbPlayer)*GalaxySize.WORLD_SIZE_MULTIPLIER
        self.seed  = random.seed(seed)
        self.spawnPoints = []
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
                if tempX < -1*(self.width/2)+GalaxySize.SUN_MIN_SPACING_FROM_BORDER or tempX > self.width/2-GalaxySize.SUN_MIN_SPACING_FROM_BORDER:
                    placeFound = False
                if tempY < -1*(self.height/2)+GalaxySize.SUN_MIN_SPACING_FROM_BORDER or tempY > self.height/2-GalaxySize.SUN_MIN_SPACING_FROM_BORDER: 
                    placeFound = False
                for j in self.solarSystemList:
                    if tempX > j.sunPosition[0]-GalaxySize.SOLAR_SYSTEM[Constants.WIDTH]/2 and tempX < j.sunPosition[0]+GalaxySize.SOLAR_SYSTEM[Constants.WIDTH]/2:
                        if tempY > j.sunPosition[1]-GalaxySize.SOLAR_SYSTEM[Constants.HEIGHT]/2 and tempY < j.sunPosition[1]+GalaxySize.SOLAR_SYSTEM[Constants.HEIGHT]/2:
                            placeFound = False
            self.solarSystemList.append(SolarSystem(tempX,tempY,0))

    def getSpawnPoint(self):
        find = False
        while(find == False):
            x =(random.random()*self.width)-self.width/2
            y = (random.random()*self.height)-self.height/2
            find = True
            if x < (self.width/2*-1)+UnitSize.MOTHERSHIP[Constants.WIDTH] or x > self.width/2-UnitSize.MOTHERSHIP[Constants.WIDTH]:
                find = False
            if y < (self.height/2*-1)+UnitSize.MOTHERSHIP[Constants.HEIGHT] or y > self.height/2-UnitSize.MOTHERSHIP[Constants.HEIGHT]:
                find = False
            if find == True:
                for i in self.solarSystemList:
                    if((x > i.sunPosition[0] - GalaxySize.SOLAR_SYSTEM[Constants.WIDTH]/2 and x < i.sunPosition[0] + GalaxySize.SOLAR_SYSTEM[Constants.WIDTH]/2)
                        and (y > i.sunPosition[1] - GalaxySize.SOLAR_SYSTEM[Constants.HEIGHT]/2) and y < i.sunPosition[1]+GalaxySize.SOLAR_SYSTEM[Constants.HEIGHT]/2):
                        find = False
                        break
            if find == True:
                for i in self.spawnPoints:
                    if((x > i[0] - GalaxySize.SPAWN_POINT_MIN_SPACING and x < i[0] + GalaxySize.SPAWN_POINT_MIN_SPACING)
                        and (y > i[1] - GalaxySize.SPAWN_POINT_MIN_SPACING) and (y < i[1] + GalaxySize.SPAWN_POINT_MIN_SPACING)):
                        find = False
                        break
        self.spawnPoints.append((x,y,0))
        return [x,y,0]

#Classe qui represente 1 seul systeme solaire                            
class SolarSystem():
    def __init__(self,sunX,sunY,sunZ):
        self.sunPosition = (sunX,sunY,sunZ)
        self.planets = []
        self.nebulas = []
        self.asteroids = []
        self.discovered = False
        nPlanet = int(random.random()*GalaxySize.MAX_PLANETS_PER_SOLAR_SYSTEM)+1
        nRes = int(random.random()*GalaxySize.MAX_ATRONOMICAL_OBJECTS_PER_SOLAR_SYSTEM)+1
        nNebu = 0
        nAstero = 0
        for i  in range(0,nRes):
            if i%2==1:
                nNebu +=1
            else:
                nAstero +=1
        for i in range(0,nPlanet):
            tempX=""
            tempY=""
            placeFound = False
            while placeFound == False:
                placeFound = True
                tempX = (random.random()*GalaxySize.SOLAR_SYSTEM[Constants.WIDTH]/2)-GalaxySize.PLANET_MAX_SPACING_FROM_SUN
                tempY = (random.random()*GalaxySize.SOLAR_SYSTEM[Constants.HEIGHT]/2)-GalaxySize.PLANET_MAX_SPACING_FROM_SUN
                #Condition de placement des planetes
                if tempX > -40 and tempX < 40:
                    if tempY > -40 and tempY < 40:
                        placeFound = False
                for j in self.planets:
                    if self.sunPosition[0]+tempX > j.position[0]-20 and self.sunPosition[0]+tempX < j.position[0]+20:
                        if self.sunPosition[1]+tempY > j.position[1]-20 and self.sunPosition[1]+tempY < j.position[1]+20:
                            placeFound = False
            self.planets.append(Planet([self.sunPosition[0]+tempX,self.sunPosition[1]+tempY],int(random.random()*3),int(random.random()*3)))
            #self.planets.append(AstronomicalObject('planet', (self.sunPosition[0]+tempX,self.sunPosition[1]+tempY)))
        for i in range(0,nNebu):
            tempX=""
            tempY=""
            placeFound = False
            while placeFound == False:
                placeFound = True
                tempX = (random.random()*GalaxySize.SOLAR_SYSTEM[Constants.WIDTH]/2)-GalaxySize.PLANET_MAX_SPACING_FROM_SUN
                tempY = (random.random()*GalaxySize.SOLAR_SYSTEM[Constants.HEIGHT]/2)-GalaxySize.PLANET_MAX_SPACING_FROM_SUN
                #Condition de placement des nebuleuses
                if tempX > -40 and tempX < 40:
                    if tempY > -40 and tempY < 40:
                        placeFound = False
                for j in self.planets:
                    if self.sunPosition[0]+tempX > j.position[0]-20 and self.sunPosition[0]+tempX < j.position[0]+20:
                        if self.sunPosition[1]+tempY > j.position[1]-20 and self.sunPosition[1]+tempY < j.position[1]+20:
                            placeFound = False
                for k in self.nebulas:
                    if self.sunPosition[0]+tempX > k.position[0]-20 and self.sunPosition[0]+tempX < k.position[0]+20:
                        if self.sunPosition[1]+tempY > k.position[1]-20 and self.sunPosition[1]+tempY < k.position[1]+20:
                            placeFound = False
            self.nebulas.append(AstronomicalObject('nebula', (self.sunPosition[0]+tempX,self.sunPosition[1]+tempY)))
        for i in range(0,nAstero):
            tempX=""
            tempY=""
            placeFound = False
            while placeFound == False:
                placeFound = True
                tempX = (random.random()*GalaxySize.SOLAR_SYSTEM[Constants.WIDTH]/2)-GalaxySize.PLANET_MAX_SPACING_FROM_SUN
                tempY = (random.random()*GalaxySize.SOLAR_SYSTEM[Constants.HEIGHT]/2)-GalaxySize.PLANET_MAX_SPACING_FROM_SUN
                #Condition de placement des asteroïdes
                if tempX > -40 and tempX < 40:
                    if tempY > -40 and tempY < 40:
                        placeFound = False
                for j in self.planets:
                    if self.sunPosition[0]+tempX > j.position[0]-20 and self.sunPosition[0]+tempX < j.position[0]+20:
                        if self.sunPosition[1]+tempY > j.position[1]-20 and self.sunPosition[1]+tempY < j.position[1]+20:
                            placeFound = False
                for k in self.nebulas:
                    if self.sunPosition[0]+tempX > k.position[0]-20 and self.sunPosition[0]+tempX < k.position[0]+20:
                        if self.sunPosition[1]+tempY > k.position[1]-20 and self.sunPosition[1]+tempY < k.position[1]+20:
                            placeFound = False
                for q in self.asteroids:
                    if self.sunPosition[0]+tempX > q.position[0]-20 and self.sunPosition[0]+tempX < q.position[0]+20:
                        if self.sunPosition[1]+tempY > q.position[1]-20 and self.sunPosition[1]+tempY < q.position[1]+20:
                            placeFound = False
            self.asteroids.append(AstronomicalObject('asteroid', (self.sunPosition[0]+tempX,self.sunPosition[1]+tempY)))

#Represente un objet spacial (Planete, Meteorite, Nebuleuse)
#Le type represente quel objet parmi les 3
class AstronomicalObject(Target):
    def __init__(self, type, position):
        Target.__init__(self, position)
        self.type = type
        self.discovered = False
        #self.mineralQte = 100
        #self.gazQte = 100
        #if type == 'planet':
            #self.landable = True
        #else:
            #self.landable = False
        if type == 'nebula':
            self.gazQte = math.trunc((random.random()*RessourcesQuantity.MAX_NEBULA_GAS/2)+RessourcesQuantity.MAX_NEBULA_GAS/2)
            self.mineralQte = 0
        elif type == 'asteroid':
            self.mineralQte = math.trunc((random.random()*RessourcesQuantity.MAX_ASTEROID_MINERALS/2)+RessourcesQuantity.MAX_ASTEROID_MINERALS/2)
            self.gazQte = 0 
            
class Planet(Target):
    def __init__(self, planetPosition, nMineralStack, nGazStack):
        Target.__init__(self, planetPosition)
        self.discovered = False
        self.minerals = []
        self.mineralQte = 0
        self.gazQte = 0
        self.gaz = []
        self.nMineralStack = nMineralStack + 1
        self.nGazStack = nGazStack + 1
        self.landingZones = []
        for i in range(0, self.nMineralStack):
            nMinerals = int(random.random()*RessourcesQuantity.MAX_MINERAL_STACK/2+RessourcesQuantity.MAX_MINERAL_STACK/2)
            posFound = False
            while not posFound:
                posFound = True
                position = [random.random()*PlanetSize.WIDTH, random.random()*PlanetSize.HEIGHT]
                if position[0] < 0 or position[0] > PlanetSize.WIDTH-PlanetSize.PADDING:
                    if position[1] < 0 or position[0] > PlanetSize.HEIGHT-PlanetSize.PADDING:
                        posFound = False
                for i in self.minerals:
                    if position[0] > i.position[0] and position[0] < i.position[0]+PlanetSize.PADDING:
                        if position[1] > i.position[1] and position[1] < i.position[1]+PlanetSize.PADDING:
                            posFound = False
            self.minerals.append(MineralStack(nMinerals,position))
        for i in range(0, self.nGazStack):
            nGaz = int(random.random()*RessourcesQuantity.MAX_GAS_STACK/2 + RessourcesQuantity.MAX_GAS_STACK/2)
            posFound = False
            while not posFound:
                posFound = True
                position = [random.random()*PlanetSize.WIDTH, random.random()*PlanetSize.HEIGHT]
                if position[0] < 0 or position[0] > PlanetSize.WIDTH-PlanetSize.PADDING:
                    if position[1] < 0 or position[1] > PlanetSize.HEIGHT-PlanetSize.PADDING:
                        posFound = False
                for i in self.minerals:
                    if position[0] > i.position[0] and position[0] < i.position[0]+PlanetSize.PADDING:
                        if position[1] > i.position[1] and position[1] < i.position[1]+PlanetSize.PADDING:
                            posFound = False
                for i in self.gaz:
                    if position[0] > i.position[0] and position[0] < i.position[0]+PlanetSize.PADDING:
                        if position[1] > i.position[1] and position[1] < i.position[1]+PlanetSize.PADDING:
                            posFound = False
            self.gaz.append(GazStack(nGaz, position))
        for i in self.minerals:
            self.mineralQte += i.nbMinerals
        for i in self.gaz:
            self.gazQte += i.nbGaz

class MineralStack(Target):
    def __init__(self, nbMinerals, position):
        Target.__init__(self, position)
        self.nbMinerals = nbMinerals
        
class GazStack(Target):
    def __init__(self, nbGaz, position):
        Target.__init__(self, position)
        self.nbGaz= nbGaz
