# -*- coding: UTF-8 -*-
import random
from Target import *
import Unit as u
import math

#Classe qui represente la galaxie en entier.
class Galaxy():
    SIZE_MULTIPLIER=1000
    MIN_SPAWN_POINT_SPACING = 800
    BORDER_SPACING=25
    SUN_BORDER_SPACING=BORDER_SPACING + 175
    MAX_SOLARSYSTEM = 9
    def __init__(self,nbPlayer, seed):
        if nbPlayer>2:
            temp = int(math.pow(2, math.sqrt(nbPlayer)) * 1500)
            if temp%2 >0:
                temp +=1
            self.width = temp
            self.height = temp
            self.depth = temp
##            self.width=(nbPlayer-2)*self.SIZE_MULTIPLIER
##            self.height=(nbPlayer-2)*self.SIZE_MULTIPLIER
##            self.depth=(nbPlayer-2)*self.SIZE_MULTIPLIER
        else:
            self.width=3000
            self.height=3000
            self.depth=3000
        self.seed  = random.seed(seed)
        self.spawnPoints = []
        self.solarSystemList = []
        for i in range(1,nbPlayer*self.MAX_SOLARSYSTEM):
            tempX=""
            tempY=""
            placeFound = False
            while placeFound == False:
                tempX=random.randrange(self.width/2 * -1, self.width/2)#(random.random()*self.width/2)-(random.random()*self.width/2)
                tempY=random.randrange(self.height/2 * -1, self.height/2)#(random.random()*self.height/2)-(random.random()*self.width/2)
                placeFound = True
                #Conditions de placement des soleils
                if tempX < -1*(self.width/2)+self.SUN_BORDER_SPACING or tempX > self.width/2-self.SUN_BORDER_SPACING:
                    placeFound = False
                if tempY < -1*(self.height/2)+self.SUN_BORDER_SPACING or tempY > self.height/2-self.SUN_BORDER_SPACING: 
                    placeFound = False
                for j in self.solarSystemList:
                    if tempX > j.sunPosition[0]-j.WIDTH/2 and tempX < j.sunPosition[0]+j.WIDTH/2:
                        if tempY > j.sunPosition[1]-j.HEIGHT/2 and tempY < j.sunPosition[1]+j.HEIGHT/2:
                            placeFound = False
                            break
            self.solarSystemList.append(SolarSystem([tempX,tempY,0],i-1))

    def getSpawnPoint(self):
        find = False
        while(find == False):
            x =(random.random()*self.width)-self.width/2
            y = (random.random()*self.height)-self.height/2
            find = True
            if x < (self.width/2*-1)+u.Unit.SIZE[u.Unit.MOTHERSHIP][0] or x > self.width/2-u.Unit.SIZE[u.Unit.MOTHERSHIP][0]:
                find = False
            if y < (self.height/2*-1)+u.Unit.SIZE[u.Unit.MOTHERSHIP][1] or y > self.height/2-u.Unit.SIZE[u.Unit.MOTHERSHIP][1]:
                find = False
            if find == True:
                for i in self.solarSystemList:
                    if((x > i.sunPosition[0] - i.WIDTH/2 and x < i.sunPosition[0] + i.WIDTH/2)
                        and (y > i.sunPosition[1] - i.HEIGHT/2) and y < i.sunPosition[1]+i.HEIGHT/2):
                        find = False
                        break
            if find == True:
                for i in self.spawnPoints:
                    if((x > i[0] - Galaxy.MIN_SPAWN_POINT_SPACING and x < i[0] + Galaxy.MIN_SPAWN_POINT_SPACING)
                        and (y > i[1] - Galaxy.MIN_SPAWN_POINT_SPACING) and (y < i[1] + Galaxy.MIN_SPAWN_POINT_SPACING)):
                        find = False
                        break
        self.spawnPoints.append((x,y,0))
        return [x,y,0]


#Classe qui represente 1 seul systeme solaire
class SolarSystem():
    HEIGHT=400
    WIDTH=400
    SUN_WIDTH=20
    SUN_HEIGHT=20
    MAX_PLANETS=6
    MAX_ATRO_OBJS=8
    NEBULA = 0
    ASTEROID = 1
    
    def __init__(self,position,sunId):
        self.sunId = sunId
        self.sunPosition = position
        self.planets = []
        self.nebulas = []
        self.asteroids = []
        self.discovered = False
        nPlanet = int(random.random()*self.MAX_PLANETS)+1
        nRes = int(random.random()*self.MAX_ATRO_OBJS)+1
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
                tempX = random.randrange(self.WIDTH/2*-1, self.WIDTH/2) #(random.random()*SolarSystem.WIDTH/2)-(random.random()*SolarSystem.WIDTH/2)
                tempY = random.randrange(self.HEIGHT/2*-1, self.HEIGHT/2)#(random.random()*SolarSystem.HEIGHT/2)-(random.random()*SolarSystem.HEIGHT/2)
                #Condition de placement des planetes
                if tempX > -40 and tempX < 40:
                    placeFound = False
                if tempY > -40 and tempY < 40:
                    placeFound = False
                for j in self.planets:
                    if self.sunPosition[0]+tempX > j.position[0]-j.IMAGE_WIDTH and self.sunPosition[0]+tempX < j.position[0]+j.IMAGE_WIDTH:
                        if self.sunPosition[1]+tempY > j.position[1]-j.IMAGE_HEIGHT and self.sunPosition[1]+tempY < j.position[1]+j.IMAGE_HEIGHT:
                            placeFound = False
                            break
            self.planets.append(Planet([self.sunPosition[0]+tempX,self.sunPosition[1]+tempY],int(random.random()*3),int(random.random()*3)))
        for i in range(0,nNebu):
            tempX=""
            tempY=""
            placeFound = False
            while placeFound == False:
                placeFound = True
                tempX = random.randrange(self.WIDTH/2*-1, self.WIDTH/2) #(random.random()*SolarSystem.WIDTH/2)-(random.random()*SolarSystem.WIDTH/2)
                tempY = random.randrange(self.HEIGHT/2*-1, self.HEIGHT/2)#(random.random()*SolarSystem.HEIGHT/2)-(random.random()*SolarSystem.HEIGHT/2)
                #Condition de placement des nebuleuses
                if tempX > -40 and tempX < 40:
                    placeFound = False
                if tempY > -40 and tempY < 40:
                    placeFound = False
                for j in self.planets:
                    if self.sunPosition[0]+tempX > j.position[0]-j.IMAGE_WIDTH and self.sunPosition[0]+tempX < j.position[0]+j.IMAGE_WIDTH:
                        if self.sunPosition[1]+tempY > j.position[1]-j.IMAGE_HEIGHT and self.sunPosition[1]+tempY < j.position[1]+j.IMAGE_HEIGHT:
                            placeFound = False
                            break
                for k in self.nebulas:
                    if self.sunPosition[0]+tempX > k.position[0]-k.NEBULA_WIDTH and self.sunPosition[0]+tempX < k.position[0]+k.NEBULA_WIDTH:
                        if self.sunPosition[1]+tempY > k.position[1]-k.NEBULA_HEIGHT and self.sunPosition[1]+tempY < k.position[1]+k.NEBULA_HEIGHT:
                            placeFound = False
                            break
            self.nebulas.append(AstronomicalObject('nebula', (self.sunPosition[0]+tempX,self.sunPosition[1]+tempY),i,self))
        for i in range(0,nAstero):
            tempX=""
            tempY=""
            placeFound = False
            while placeFound == False:
                placeFound = True
                tempX = random.randrange(self.WIDTH/2*-1, self.WIDTH/2) #(random.random()*SolarSystem.WIDTH/2)-(random.random()*SolarSystem.WIDTH/2)
                tempY = random.randrange(self.HEIGHT/2*-1, self.HEIGHT/2)#(random.random()*SolarSystem.HEIGHT/2)-(random.random()*SolarSystem.HEIGHT/2)
                #Condition de placement des asteroïdes
                if tempX > -40 and tempX < 40:
                    placeFound = False
                if tempY > -40 and tempY < 40:
                    placeFound = False
                for j in self.planets:
                    if self.sunPosition[0]+tempX > j.position[0]-j.IMAGE_WIDTH and self.sunPosition[0]+tempX < j.position[0]+j.IMAGE_WIDTH:
                        if self.sunPosition[1]+tempY > j.position[1]-j.IMAGE_HEIGHT and self.sunPosition[1]+tempY < j.position[1]+j.IMAGE_HEIGHT:
                            placeFound = False
                            break
                for k in self.nebulas:
                    if self.sunPosition[0]+tempX > k.position[0]-k.NEBULA_WIDTH and self.sunPosition[0]+tempX < k.position[0]+k.NEBULA_WIDTH:
                        if self.sunPosition[1]+tempY > k.position[1]-k.NEBULA_HEIGHT and self.sunPosition[1]+tempY < k.position[1]+k.NEBULA_HEIGHT:
                            placeFound = False
                            break
                for q in self.asteroids:
                    if self.sunPosition[0]+tempX > q.position[0]-q.ASTEROID_WIDTH and self.sunPosition[0]+tempX < q.position[0]+q.ASTEROID_WIDTH:
                        if self.sunPosition[1]+tempY > q.position[1]-q.ASTEROID_HEIGHT and self.sunPosition[1]+tempY < q.position[1]+q.ASTEROID_HEIGHT:
                            placeFound = False
                            break
            self.asteroids.append(AstronomicalObject('asteroid', (self.sunPosition[0]+tempX,self.sunPosition[1]+tempY),i,self))
        
#Represente un objet spacial (Planete, Meteorite, Nebuleuse)
#Le type represente quel objet parmi les 3
class AstronomicalObject(Target):
    NEBULA_WIDTH=15
    NEBULA_HEIGHT=15
    MAX_GAS=300
    ASTEROID_WIDTH=16
    ASTEROID_HEIGHT=16
    MAX_MINERALS=300
    NEBULA = 90
    ASTEROID = 91
    
    def __init__(self, type, position, id,solarSystem):
        Target.__init__(self, position)
        self.solarSystem = solarSystem
        self.id = id
        self.type = type
        self.discovered = False
        if type == 'nebula':
            self.gazQte = random.randrange(self.MAX_GAS/2, self.MAX_GAS)#((random.random()*self.MAX_GAS/2)+self.MAX_GAS/2)
            self.mineralQte = 0
        elif type == 'asteroid':
            self.mineralQte = random.randrange(self.MAX_MINERALS/2, self.MAX_MINERALS)#((random.random()*self.MAX_MINERALS/2)+self.MAX_MINERALS/2)
            self.gazQte = 0 
            
class Planet(Target):
    IMAGE_WIDTH=15
    IMAGE_HEIGHT=15
    WIDTH=1600
    HEIGHT=1200
    PADDING=25
    MAX_DIST_FROM_SUN = SolarSystem.WIDTH/4
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
        self.units = []
        for i in range(0, self.nMineralStack):
            nMinerals = random.randrange(MineralStack.MAX_QTY/2, MineralStack.MAX_QTY)#random.random()*MineralStack.MAX_QTY/2+MineralStack.MAX_QTY/2)
            posFound = False
            while not posFound:
                posFound = True
                position = [random.random()*Planet.WIDTH, random.random()*Planet.HEIGHT]
                if position[0] < Planet.PADDING or position[0] > Planet.WIDTH-Planet.PADDING-MineralStack.WIDTH/2:
                    posFound = False
                if position[1] < Planet.PADDING or position[1] > Planet.HEIGHT-Planet.PADDING-MineralStack.HEIGHT/2:
                    posFound = False
                for i in self.minerals:
                    if position[0] > i.position[0]-i.WIDTH and position[0] < i.position[0]+i.WIDTH:
                        if position[1] > i.position[1]-i.HEIGHT and position[1] < i.position[1]+i.HEIGHT:
                            posFound = False
                            break
            self.minerals.append(MineralStack(nMinerals,position))
        for i in range(0, self.nGazStack):
            nGaz = int(random.randrange(GazStack.MAX_QTY/2, GazStack.MAX_QTY))#random.random()*GazStack.MAX_QTY/2+GazStack.MAX_QTY/2)
            posFound = False
            while not posFound:
                posFound = True
                position = [random.random()*Planet.WIDTH, random.random()*Planet.HEIGHT]
                if position[0] < Planet.PADDING or position[0] > Planet.WIDTH-Planet.PADDING-GazStack.WIDTH/2:
                    posFound = False
                if position[1] < Planet.PADDING or position[1] > Planet.HEIGHT-Planet.PADDING-GazStack.HEIGHT/2:
                    posFound = False
                for i in self.minerals:
                    if position[0] > i.position[0]-i.WIDTH and position[0] < i.position[0]+i.WIDTH:
                        if position[1] > i.position[1]-i.HEIGHT and position[1] < i.position[1]+i.HEIGHT:
                            posFound = False
                            break
                for i in self.gaz:
                    if position[0] > i.position[0]-i.WIDTH and position[0] < i.position[0]+i.WIDTH:
                        if position[1] > i.position[1]-i.HEIGHT and position[1] < i.position[1]+i.HEIGHT:
                            posFound = False
                            break
            self.gaz.append(GazStack(nGaz, position))
        for i in self.minerals:
            self.mineralQte += i.nbMinerals
        for i in self.gaz:
            self.gazQte += i.nbGaz

    def addLandingZone(self, playerid, landingShip):
        placeFound = False
        while not placeFound:
            placeFound = True
            position = [random.random()*Planet.WIDTH, random.random()*Planet.HEIGHT]
            if position[0] < LandingZone.WIDTH/2 or position[0] > self.WIDTH-LandingZone.WIDTH/2:
                placeFound = False
            if position[1] < LandingZone.HEIGHT/2 or position[1] > self.HEIGHT-LandingZone.HEIGHT/2:
                placeFound = False
            for i in self.minerals:
                if position[0] > i.position[0]-i.WIDTH and position[0] < i.position[0]+i.WIDTH:
                    if position[1] > i.position[1]-i.HEIGHT and position[1] < i.position[1]+i.HEIGHT:
                        posFound = False
                        break
            for i in self.gaz:
                if position[0] > i.position[0]-i.WIDTH and position[0] < i.position[0]+i.WIDTH:
                    if position[1] > i.position[1]-i.HEIGHT and position[1] < i.position[1]+i.HEIGHT:
                        posFound = False
                        break
        newSpot = LandingZone(position, playerid, landingShip)
        self.landingZones.append(newSpot)
        return newSpot

    def alreadyLanded(self, playerId):
        alreadyLanded = False
        for i in self.landingZones:
            if i.ownerId == playerId:
                alreadyLanded = True
        return alreadyLanded
    def getLandingSpot(self, playerId):
        for i in self.landingZones:
            if i.ownerId == playerId:
                return i
        return None
class MineralStack(Target):
    WIDTH = 48
    HEIGHT = 64
    MAX_QTY = 3000
    def __init__(self, nbMinerals, position):
        Target.__init__(self, position)
        self.nbMinerals = nbMinerals
        
class GazStack(Target):
    WIDTH = 24
    HEIGHT = 24
    MAX_QTY = 3000
    def __init__(self, nbGaz, position):
        Target.__init__(self, position)
        self.nbGaz= nbGaz
        
class LandingZone(PlayerObject):
    WIDTH = 75
    HEIGHT = 75
    def __init__(self, position, ownerId, landingShip):
        PlayerObject.__init__(self, 'Zone d\'atterissage', 0, position, ownerId)
        self.ownerId = ownerId
        self.LandedShip = landingShip
