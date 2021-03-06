# -*- coding: UTF-8 -*-
import random
from Target import *
import Unit as u
import Building as b
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
        else:
            self.width=3000
            self.height=3000
            self.depth=3000
        self.seed  = random.seed(seed)
        self.spawnPoints = []
        self.solarSystemList = []
        self.wormholes = []
        for i in range(1,nbPlayer*self.MAX_SOLARSYSTEM):
            tempX=""
            tempY=""
            placeFound = False
            while placeFound == False:
                tempX=random.randrange(self.width/2 * -1, self.width/2)
                tempY=random.randrange(self.height/2 * -1, self.height/2)
                placeFound = True
                #Conditions de placement des soleils
                if tempX < -1*(self.width/2)+self.SUN_BORDER_SPACING or tempX > self.width/2-self.SUN_BORDER_SPACING:
                    placeFound = False
                if tempY < -1*(self.height/2)+self.SUN_BORDER_SPACING or tempY > self.height/2-self.SUN_BORDER_SPACING: 
                    placeFound = False
                for j in self.solarSystemList:
                    if tempX > j.sunPosition[0]-j.WIDTH and tempX < j.sunPosition[0]+j.WIDTH:
                        if tempY > j.sunPosition[1]-j.HEIGHT and tempY < j.sunPosition[1]+j.HEIGHT:
                            placeFound = False
                            break
            self.solarSystemList.append(SolarSystem([tempX,tempY,0],i-1))

    def getSpawnPoint(self):
        find = False
        while(find == False):
            x =(random.random()*self.width)-self.width/2
            y = (random.random()*self.height)-self.height/2
            find = True
            if x < (self.width/2*-1)+b.Building.SIZE[b.Building.MOTHERSHIP][0] or x > self.width/2-b.Building.SIZE[b.Building.MOTHERSHIP][0]:
                find = False
            if y < (self.height/2*-1)+b.Building.SIZE[b.Building.MOTHERSHIP][1] or y > self.height/2-b.Building.SIZE[b.Building.MOTHERSHIP][1]:
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
    
    def select(self, position, wantWormhole=True):
        clickedObj = None
        if wantWormhole:
            for i in self.wormholes:
                if i.duration > 0:
                    wormhole = i.select(position)
                    if wormhole != None and clickedObj == None:
                        clickedObj = wormhole
        if clickedObj == None:
            for i in self.solarSystemList:
                spaceObj = i.select(position)
                if spaceObj != None and clickedObj == None:
                    clickedObj = spaceObj
        return clickedObj

#Classe qui represente 1 seul systeme solaire
class SolarSystem():
    HEIGHT=400
    WIDTH=400
    SUN_WIDTH=64
    SUN_HEIGHT=64
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
                tempX = random.randrange(self.WIDTH/2*-1, self.WIDTH/2)
                tempY = random.randrange(self.HEIGHT/2*-1, self.HEIGHT/2)
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
            self.planets.append(Planet([self.sunPosition[0]+tempX,self.sunPosition[1]+tempY],int(random.random()*3),int(random.random()*3),i, self))
        for i in range(0,nNebu):
            tempX=""
            tempY=""
            placeFound = False
            while placeFound == False:
                placeFound = True
                tempX = random.randrange(self.WIDTH/2*-1, self.WIDTH/2)
                tempY = random.randrange(self.HEIGHT/2*-1, self.HEIGHT/2)
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
            self.nebulas.append(AstronomicalObject(SolarSystem.NEBULA, (self.sunPosition[0]+tempX,self.sunPosition[1]+tempY),i,self))
        for i in range(0,nAstero):
            tempX=""
            tempY=""
            placeFound = False
            while placeFound == False:
                placeFound = True
                tempX = random.randrange(self.WIDTH/2*-1, self.WIDTH/2)
                tempY = random.randrange(self.HEIGHT/2*-1, self.HEIGHT/2)
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
            self.asteroids.append(AstronomicalObject(SolarSystem.ASTEROID, (self.sunPosition[0]+tempX,self.sunPosition[1]+tempY),i,self))

    def over(self, positionStart, positionEnd):
        if positionEnd[0] > self.sunPosition[0] - self.SUN_WIDTH/2 and positionStart[0] < self.sunPosition[0] + self.SUN_WIDTH/2:
            if positionEnd[1] > self.sunPosition[1] - self.SUN_HEIGHT/2 and positionStart[1] < self.sunPosition[1] + self.SUN_HEIGHT/2:
                return True
        for i in self.planets:
            if i.over(positionStart, positionEnd):
                return True
        for i in self.nebulas:
            if i.overNebula(positionStart, positionEnd):
                return True
        for i in self.asteroids:
            if i.overAsteroid(positionStart, positionEnd):
                return True
        return False
            
    
    def select(self, position):
        clickedObj = None
        for i in self.planets:
            planet = i.select(position)
            if planet != None and clickedObj == None:
                clickedObj = planet
        for i in self.nebulas:
            nebula = i.selectNebula(position)
            if nebula != None and clickedObj == None:
                clickedObj = nebula
        for i in self.asteroids:
            asteroid = i.selectAsteroid(position)
            if asteroid != None and clickedObj == None:
                clickedObj = asteroid
        return clickedObj

#Represente un objet spacial (Planete, Meteorite, Nebuleuse)
#Le type represente quel objet parmi les 3
class AstronomicalObject(Target):
    NEBULA_WIDTH=40
    NEBULA_HEIGHT=41
    MAX_GAS=1000
    ASTEROID_WIDTH=30
    ASTEROID_HEIGHT=31
    MAX_MINERALS=1000
    NEBULA = 0
    ASTEROID = 1
    
    def __init__(self, type, position, id,solarSystem):
        Target.__init__(self, position)
        self.solarSystem = solarSystem
        self.id = id
        self.type = type
        self.discovered = False
        if type == AstronomicalObject.NEBULA:
            self.gazQte = random.randrange(self.MAX_GAS/2, self.MAX_GAS)
            self.mineralQte = 0
        elif type == AstronomicalObject.ASTEROID:
            self.mineralQte = random.randrange(self.MAX_MINERALS/2, self.MAX_MINERALS)
            self.gazQte = 0 

    def overNebula(self, positionStart, positionEnd):
        if self.gazQte > 0:
            if positionEnd[0] > self.position[0] - self.NEBULA_WIDTH/2 and positionStart[0] < self.position[0] + self.NEBULA_WIDTH/2:
                if positionEnd[1] > self.position[1] - self.NEBULA_HEIGHT/2 and positionStart[1] < self.position[1] + self.NEBULA_HEIGHT/2:
                    return True

    def overAsteroid(self, positionStart, positionEnd):
        if self.mineralQte > 0:
            if positionEnd[0] > self.position[0] - self.ASTEROID_WIDTH/2 and positionStart[0] < self.position[0] + self.ASTEROID_WIDTH/2:
                if positionEnd[1] > self.position[1] - self.ASTEROID_HEIGHT/2 and positionStart[1] < self.position[1] + self.ASTEROID_HEIGHT/2:
                    return True
            
    def selectNebula(self, position):
        if position[0] >= self.position[0]-self.NEBULA_WIDTH/2 and position[0] <= self.position[0]+self.NEBULA_WIDTH/2:
            if position[1] >= self.position[1]-self.NEBULA_HEIGHT/2 and position[1] <= self.position[1]+self.NEBULA_HEIGHT/2:
                return self
        return None
    
    def selectAsteroid(self, position):
        if position[0] >= self.position[0]-self.ASTEROID_WIDTH/2 and position[0] <= self.position[0]+self.ASTEROID_WIDTH/2:
            if position[1] >= self.position[1]-self.ASTEROID_HEIGHT/2 and position[1] <= self.position[1]+self.ASTEROID_HEIGHT/2:
                return self
        return None

class WormHole(Target):
    WIDTH = 125;
    HEIGHT = 125;
    NUKECOST = 2;
    DEFAULTDURATION = 600
    def __init__(self, position, destination, playerId):
        Target.__init__(self, position)
        self.duration = self.DEFAULTDURATION
        self.destination = destination
        self.playerId = playerId

    def action(self):
        self.duration -= 1

    def select(self, position):
        if position[0] > self.position[0]-self.WIDTH/2 and position[0] < self.position[0]+self.WIDTH/2:
            if position[1] > self.position[1]-self.HEIGHT/2 and position[1] < self.position[1]+self.HEIGHT/2:
                return self
        return None
    
    def over(self, positionStart, positionEnd):
        if positionEnd[0] > self.position[0] - self.WIDTH/2 and positionStart[0] < self.position[0] + self.WIDTH/2:
            if positionEnd[1] > self.position[1] - self.HEIGHT/2 and positionStart[1] < self.position[1] + self.HEIGHT/2:
                return True
        return False
    
class Planet(Target):
    IMAGE_WIDTH=38
    IMAGE_HEIGHT=37
    WIDTH=1600
    HEIGHT=1200
    PADDING=25
    MAX_DIST_FROM_SUN = SolarSystem.WIDTH/4
    MINERAL = 0
    GAZ = 1
    LANDINGZONE = 2
    NUCLEAR = 3
    def __init__(self, planetPosition, nMineralStack, nGazStack, id, solarSystem):
        Target.__init__(self, planetPosition)
        self.discovered = False
        self.minerals = []
        self.mineralQte = 0
        self.gazQte = 0
        self.gaz = []
        self.nuclearSite = None
        self.nMineralStack = nMineralStack + 1
        self.nGazStack = nGazStack + 1
        self.landingZones = []
        self.units = []
        self.buildings = []
        self.id = id
        self.solarSystem = solarSystem
        for i in range(0, self.nMineralStack):
            nMinerals = random.randrange(MineralStack.MAX_QTY/2, MineralStack.MAX_QTY)
            posFound = False
            while not posFound:
                posFound = True
                position = [random.random()*Planet.WIDTH, random.random()*Planet.HEIGHT]
                if position[0] < Planet.PADDING or position[0] > Planet.WIDTH-Planet.PADDING-MineralStack.WIDTH/2:
                    posFound = False
                if position[1] < Planet.PADDING or position[1] > Planet.HEIGHT-Planet.PADDING-MineralStack.HEIGHT/2:
                    posFound = False
                for j in self.minerals:
                    if position[0] > j.position[0]-j.WIDTH and position[0] < j.position[0]+j.WIDTH:
                        if position[1] > j.position[1]-j.HEIGHT and position[1] < j.position[1]+j.HEIGHT:
                            posFound = False
                            break
            self.minerals.append(MineralStack(nMinerals, position, i, id, solarSystem.sunId))
        for i in range(0, self.nGazStack):
            nGaz = int(random.randrange(GazStack.MAX_QTY/2, GazStack.MAX_QTY))
            posFound = False
            while not posFound:
                posFound = True
                position = [random.random()*Planet.WIDTH, random.random()*Planet.HEIGHT]
                if position[0] < Planet.PADDING or position[0] > Planet.WIDTH-Planet.PADDING-GazStack.WIDTH/2:
                    posFound = False
                if position[1] < Planet.PADDING or position[1] > Planet.HEIGHT-Planet.PADDING-GazStack.HEIGHT/2:
                    posFound = False
                for j in self.minerals:
                    if position[0] > j.position[0]-j.WIDTH and position[0] < j.position[0]+j.WIDTH:
                        if position[1] > j.position[1]-j.HEIGHT and position[1] < j.position[1]+j.HEIGHT:
                            posFound = False
                            break
                for j in self.gaz:
                    if position[0] > j.position[0]-j.WIDTH and position[0] < j.position[0]+j.WIDTH:
                        if position[1] > j.position[1]-j.HEIGHT and position[1] < j.position[1]+j.HEIGHT:
                            posFound = False
                            break
            self.gaz.append(GazStack(nGaz, position, i, id, solarSystem.sunId))
        nuclear = random.random()*6
        if nuclear > 4:
            posFound = False
            while not posFound:
                posFound = True
                position = [random.random()*Planet.WIDTH, random.random()*Planet.HEIGHT]
                if position[0] < Planet.PADDING or position[0] > Planet.WIDTH-Planet.PADDING-GazStack.WIDTH/2:
                    posFound = False
                if position[1] < Planet.PADDING or position[1] > Planet.HEIGHT-Planet.PADDING-GazStack.HEIGHT/2:
                    posFound = False
                for j in self.minerals:
                    if position[0] > j.position[0]-j.WIDTH and position[0] < j.position[0]+j.WIDTH:
                        if position[1] > j.position[1]-j.HEIGHT and position[1] < j.position[1]+j.HEIGHT:
                            posFound = False
                            break
                for j in self.gaz:
                    if position[0] > j.position[0]-j.WIDTH and position[0] < j.position[0]+j.WIDTH:
                        if position[1] > j.position[1]-j.HEIGHT and position[1] < j.position[1]+j.HEIGHT:
                            posFound = False
                            break
            self.nuclearSite = NuclearSite(position, self.id, self.solarSystem.sunId)

    def getNumMinerals(self):
        minerals = 0
        for i in self.minerals:
            minerals += i.nbMinerals
        return minerals

    def getNumGaz(self):
        gaz = 0
        for i in self.gaz:
            gaz += i.nbGaz
        return gaz

    def addLandingZone(self, playerid, landingShip, player):
        placeFound = False
        while not placeFound:
            placeFound = True
            position = [random.random()*Planet.WIDTH, random.random()*Planet.HEIGHT]
            if position[0] < b.LandingZone.WIDTH/2 or position[0] > self.WIDTH-b.LandingZone.WIDTH/2:
                placeFound = False
            if position[1] < b.LandingZone.HEIGHT/2 or position[1] > self.HEIGHT-b.LandingZone.HEIGHT/2:
                placeFound = False
            for i in self.landingZones:
                if position[0] > i.position[0]-i.WIDTH-100 and position[0] < i.position[0]+i.WIDTH+100:
                    if position[1] > i.position[1]-i.HEIGHT-100 and position[1] < i.position[1]+i.HEIGHT+100:
                        placeFound = False
                        break
            for i in self.minerals:
                if position[0] > i.position[0]-i.WIDTH-10 and position[0] < i.position[0]+i.WIDTH+10:
                    if position[1] > i.position[1]-i.HEIGHT-10 and position[1] < i.position[1]+i.HEIGHT+10:
                        placeFound = False
                        break
            for i in self.gaz:
                if position[0] > i.position[0]-i.WIDTH-10 and position[0] < i.position[0]+i.WIDTH+10:
                    if position[1] > i.position[1]-i.HEIGHT-10 and position[1] < i.position[1]+i.HEIGHT+10:
                        placeFound = False
                        break
        id = len(self.landingZones)
        newSpot = b.LandingZone(position, playerid, landingShip, id, self.id, self.solarSystem.sunId)
        newSpot.MAX_SHIELD = player.BONUS[player.BUILDING_SHIELD_BONUS]
        newSpot.shield = newSpot.MAX_SHIELD
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

    def select(self, position):
        if position[0] > self.position[0]-self.IMAGE_WIDTH/2 and position[0] < self.position[0]+self.IMAGE_WIDTH/2:
            if position[1] > self.position[1]-self.IMAGE_HEIGHT/2 and position[1] < self.position[1]+self.IMAGE_HEIGHT/2:
                return self
        return None
    
    def over(self, positionStart, positionEnd):
        if positionEnd[0] > self.position[0] - self.IMAGE_WIDTH/2 and positionStart[0] < self.position[0] + self.IMAGE_WIDTH/2:
            if positionEnd[1] > self.position[1] - self.IMAGE_HEIGHT/2 and positionStart[1] < self.position[1] + self.IMAGE_HEIGHT/2:
                return True
        return False

    def groundOver(self, positionStart, positionEnd):
        for i in self.minerals:
            if i.over(positionStart, positionEnd):
                return True
        for i in self.gaz:
            if i.over(positionStart, positionEnd):
                return True
        for i in self.landingZones:
            if i.over(positionStart, positionEnd):
                return True
        if self.nuclearSite != None:
            if self.nuclearSite.over(positionStart, positionEnd):
                return True
        return False

    def groundSelect(self, position):
        for i in self.landingZones:
            landing = i.select(position)
            if landing != None:
                return landing
        for i in self.minerals:
            mineral = i.select(position)
            if mineral != None:
                return mineral
        for i in self.gaz:
            gaz = i.select(position)
            if gaz != None:
                return gaz
        if self.nuclearSite != None:
            site = self.nuclearSite.select(position)
            if site != None:
                return site
        for i in self.units:
            unit = i.select(position)
            if unit != None:
                return unit
        for i in self.buildings:
            building = i.select(position)
            if building != None:
                return building
        return None

    def hasZoneInRange(self, position, range):
        for i in self.landingZones:
            zoneInRange = i.isInRange(position, range)
            if zoneInRange != None:
                return zoneInRange
        return None

class MineralStack(Target):
    WIDTH = 48
    HEIGHT = 64
    MAX_QTY = 3000
    def __init__(self, nbMinerals, position, id, planetId, sunId):
        Target.__init__(self, position)
        self.nbMinerals = nbMinerals
        self.id = id
        self.planetId = planetId
        self.sunId = sunId

    def over(self, positionStart, positionEnd):
        if self.nbMinerals > 0:
            if positionEnd[0] > self.position[0] - self.WIDTH/2 and positionStart[0] < self.position[0] + self.WIDTH/2:
                if positionEnd[1] > self.position[1] - self.HEIGHT/2 and positionStart[1] < self.position[1] + self.HEIGHT/2:
                    return True
        return False
        
    def select(self, position):
        if position[0] > self.position[0] - self.WIDTH/2 and position[0] < self.position[0]+self.WIDTH/2:
            if position[1] > self.position[1] -self.HEIGHT/2 and position[1] < self.position[1]+self.HEIGHT/2:
                return self
        return None
    
class GazStack(Target):
    WIDTH = 40
    HEIGHT = 42
    MAX_QTY = 3000
    def __init__(self, nbGaz, position, id, planetId, sunId):
        Target.__init__(self, position)
        self.nbGaz= nbGaz
        self.id = id
        self.planetId = planetId
        self.sunId = sunId
        self.state = 0

    def over(self, positionStart, positionEnd):
        if self.nbGaz > 0:
            if positionEnd[0] > self.position[0] - self.WIDTH/2 and positionStart[0] < self.position[0] + self.WIDTH/2:
                if positionEnd[1] > self.position[1] - self.HEIGHT/2 and positionStart[1] < self.position[1] + self.HEIGHT/2:
                    return True
        return False

    def select(self, position):
        if position[0] > self.position[0]-self.WIDTH/2 and position[0] < self.position[0]+self.WIDTH/2:
            if position[1] > self.position[1]-self.HEIGHT/2 and position[1] < self.position[1]+self.HEIGHT/2:
                return self
        return None

class NuclearSite(Target):
    WIDTH = 35
    HEIGHT = 35
    def __init__(self, position, planetId, sunId):
        Target.__init__(self, position)
        self.nbRessource = 1
        self.planetId = planetId
        self.sunId = sunId

    def over(self, positionStart, positionEnd):
        if self.nbRessource > 0:
            if positionEnd[0] > self.position[0] - self.WIDTH/2 and positionStart[0] < self.position[0] + self.WIDTH/2:
                if positionEnd[1] > self.position[1] - self.HEIGHT/2 and positionStart[1] < self.position[1] + self.HEIGHT/2:
                    return True
        return False

    def select(self, position):
        if self.position[0] > position[0] - self.WIDTH/2 and self.position[0] < position[0] + self.WIDTH/2:
            if self.position[1] > position[1] - self.HEIGHT/2 and self.position[1] < self.position[1] + self.HEIGHT/2:
                return self
        return None
