# -*- coding: UTF-8 -*-
import Unit as u
from Flag import *
from Helper import *
from TechTree import *
import math
import socket

#Represente un joueur
class Player():
    MINERAL = 0
    GAS = 1
    FOOD = 2
    #[AttaqueDamage,AttaqueSpeed,MoveSpeed,AttackRange]
    ATTACK_DAMAGE_BONUS = 0
    ATTACK_SPEED_BONUS = 1
    MOVE_SPEED_BONUS = 2
    ATTACK_RANGE_BONUS = 3
    VIEW_RANGE_BONUS = 4
    BONUS = [0,0,0,0,0]
    
    def __init__(self, name, game, id , colorId):
        self.name = name
        self.game = game
        self.colorId = colorId
        self.techTree = TechTree()
        self.selectedObjects = [] #Liste des unites selectionnes
        self.units = [] #Liste de toute les unites
        self.buildings = [] #Liste de tous les buildings
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
    def selectUnitsByType(self, unitType):
        units = []
        for i in self.selectedObjects:
            if i.type == unitType:
                units.append(i)
        self.selectedObjects = units
            
    def addBaseUnits(self, startPos):
        self.units.append(u.Mothership('Mothership', u.Unit.MOTHERSHIP,startPos, self.id))
        self.motherShip = self.units[0]
        self.units.append(u.Unit('Scout', u.Unit.SCOUT,[startPos[0] + 20, startPos[1] + 20 ,0], self.id))
        self.units.append(u.GatherShip('Gather ship', u.Unit.CARGO,[startPos[0] + 40, startPos[1]+40], self.id))
        
    #Ajoute une camera au joueur seulement quand la partie commence    
    def addCamera(self, galaxy, taille):
        pos = [0,0,0]
        for i in self.units:
            if i.type == i.MOTHERSHIP:
                pos = i.position
        default = [pos[0],pos[1]]
        self.camera = Camera(default, galaxy, self, taille)

    def moveCamera(self):
        self.camera.move()

    def changeDiplomacy(self, playerToChange, newStatus):
        self.diplomacies[playerToChange] = newStatus

    def selectUnit(self, position):
        for i in self.units:
            unit = i.select(position)
            if unit != None:
                self.selectedObjects = [unit]
        for i in self.buildings:
            building = i.select(position)
            if building != None:
                self.selectedObjects = [building]

    def multiSelectUnit(self, position):
        for i in self.units:
            unit = i.select(position)
            if unit != None and unit not in self.selectedObjects:
                self.selectedObjects.append(unit)

    def selectObject(self, playerObj, multi):
        if playerObj != None and playerObj not in self.selectedObjects:
            if not multi:
                self.selectedObjects = [playerObj]
            else:
                self.selectedObjects.append(playerObj)

    def boxSelect(self, selectStart, selectEnd):
        first = True
        if self.currentPlanet == None:
            for i in self.units:
                unit = i.boxSelect(selectStart, selectEnd)
                if first:
                    self.selectedObjects = []
                    first = False
                self.selectObject(unit, True)
        else:
            for i in self.currentPlanet.units:
                unit = i.boxSelect(selectStart, selectEnd)
                if first:
                    self.selectedObjects = []
                    first = False
                self.selectObject(unit, True)
    
    def selectAll(self, position):
        if self.currentPlanet == None:
            self.selectUnit(position)
            firstUnit = self.selectedObjects[0]
            if len(self.selectedObjects) > 0:
                for i in self.units:
                    if self.camera.inGameArea(i.position):
                        unit = i.select(position)
                        if unit.type == firstUnit.type:
                            self.selectObject(unit, True)
                            
    def getFirstUnit(self):
        if len(self.selectedObjects) > 0:
            if isinstance(self.selectedObjects[0], u.Unit):
                return self.selectedObjects[0]
        return None
    
    def rightClic(self, pos, playerId):
        if self.isAlive:
            if self.isAlly(playerId) == False or playerId == self.id:
                for i in self.units:
                    unit = i.select(pos)
                    if unit != None:
                        return unit
                unit = self.motherShip.select(pos)
                if unit != None:
                    return unit
                for b in self.buildings:
                    building = b.select(pos)
                    if building != None:
                        return building                
        return None

    def selectPlanet(self, planet):
        if len(self.selectedObjects) > 0:
            if self.selectedObjects[0] == planet:
                self.lookPlanet(planet)
            else:
                self.selectedObjects = [planet]
        else:
            self.selectedObjects = [planet]
            
    def lookPlanet(self, planet):
        if planet.alreadyLanded(self.id):
            self.currentPlanet = planet
            self.camera.placeOnLanding(planet.getLandingSpot(self.id))
        
    def inViewRange(self, position):
        x = position[0]
        y = position[1]
        for i in self.units:
            if i.isAlive and not isinstance(i, u.GroundUnit):
                if x > i.position[0]-i.viewRange and x < i.position[0]+i.viewRange:
                    if y > i.position[1]-i.viewRange and y < i.position[1]+i.viewRange:
                        if i.name == 'Transport':
                            if not i.landed:
                                return True
                        else:
                            return True
        for i in self.buildings:
            if i.isAlive and i.finished:
                if x > i.position[0]-i.viewRange and x < i.position[0]+i.viewRange:
                    if y > i.position[1]-i.viewRange and y < i.position[1]+i.viewRange:
                        return True
                    
        for i in range(len(self.diplomacies)):
            if self.isAlly(i) and i != self.id:
                for i in self.game.players[i].units:
                    if i.isAlive and not isinstance(i, u.GroundUnit):
                        if x > i.position[0]-i.viewRange and x < i.position[0]+i.viewRange:
                            if y > i.position[1]-i.viewRange and y < i.position[1]+i.viewRange:
                                if i.name == 'Transport':
                                    if not i.landed:
                                        return True
                                else:
                                    return True
                for i in self.game.players[i].buildings:
                    if i.isAlive and i.finished:
                        if x > i.position[0]-i.viewRange and x < i.position[0]+i.viewRange:
                            if y > i.position[1]-i.viewRange and y < i.position[1]+i.viewRange:
                                return True
        return False
    
    def isAlly(self, playerId):
        if self.diplomacies[playerId] == "Ally":
            return self.game.isAllied(playerId, self.id)
        return False

    def getNearestReturnRessourceCenter(self, position):
        motherShipPosition = self.motherShip.position
        nearestDistance = Helper.calcDistance(position[0],position[1],motherShipPosition[0],motherShipPosition[1])
        nearestBuilding = self.motherShip
        for b in self.buildings:
            if b.type == b.WAYPOINT:
                if b.finished:
                    buildingPosition = b.position
                    distance = Helper.calcDistance(position[0],position[1],buildingPosition[0],buildingPosition[1])
                    if distance < nearestDistance:
                        nearestDistance = distance
                        nearestBuilding = b
        return nearestBuilding

    def killUnit(self, killedIndexes):
        if killedIndexes[1] == self.id:
            if killedIndexes[2] == False:
                if self.units[killedIndexes[0]] in self.selectedObjects:
                    self.selectedObjects.remove(self.units[killedIndexes[0]])
                self.units[killedIndexes[0]].kill()
            else:
                if self.buildings[killedIndexes[0]] in self.selectedObjects:
                    self.selectedObjects.remove(self.buildings[killedIndexes[0]])
                self.buildings[killedIndexes[0]].kill()
        else:
            self.game.killUnit(killedIndexes)

    def buildUnit(self):
        unit = self.motherShip.unitBeingConstruct.pop(0)
        unit.applyBonuses(self.BONUS)
        if unit.type == u.Unit.TRANSPORT:
            pilot = u.GroundGatherUnit('Collector', u.Unit.GROUND_GATHER, [-10000,-10000,-10000], self.id, -1, -1)
            unit.units.append(pilot)
            self.units.append(pilot)
        unit.changeFlag(t.Target(self.motherShip.rallyPoint), FlagState.MOVE)
        self.units.append(unit)

    def sendKill(self):
        self.parent.sendKillPlayer(self.id)

    def kill(self):
        self.isAlive = False
        for i in self.units:
            i.kill()

    def changeBonuses(self):
        for unit in self.units:
            unit.applyBonuses(self.BONUS)
            
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
        if self.ressources[self.MINERAL] >= u.Unit.BUILD_COST[unitType][u.Unit.MINERAL] and self.ressources[self.GAS] >= u.Unit.BUILD_COST[unitType][u.Unit.GAS]:
            self.motherShip.addUnitToQueue(unitType)
            self.ressources[self.MINERAL] -= u.Unit.BUILD_COST[unitType][u.Unit.MINERAL]
            self.ressources[self.GAS] -= u.Unit.BUILD_COST[unitType][u.Unit.GAS]
            self.motherShip.flag.flagState = FlagState.BUILD_UNIT

    def makeUnitsAttack(self, units, targetPlayer, targetUnit, type):
        for i in units:
            if i != '':
                if type == "u":
                    self.units[int(i)].changeFlag(targetPlayer.units[targetUnit], FlagState.ATTACK)
                else:
                    self.units[int(i)].changeFlag(targetPlayer.buildings[targetUnit], FlagState.ATTACK)

    def makeUnitLand(self, unitId, planet):
        self.units[unitId].changeFlag(planet, FlagState.LAND)

    def makeUnitsGather(self, units, astroObject):
        for i in units:
            if i != '':
                self.units[int(i)].changeFlag(astroObject, FlagState.GATHER)
                
    def makeGroundUnitsGather(self, units, ressource):
        for i in units:
            if i != '':
                self.units[int(i)].changeFlag(ressource, FlagState.GROUND_GATHER)
        
    def makeFormation(self, units, galaxy, target = None, action = FlagState.MOVE):
        if len(units) > 1:
            #S'il n'y a pas de target de spécifiée comme lors du changement de formation
            if target == None:
                target = self.units[int(units[0])].flag.finalTarget.position
            #tuple qui contient les lignes qui peut contenir par ligne
            lineTaken=[]
            line=0
            #Coordonnées avant modification
            targetorig=[0,0]
            targetorig[0]=target[0]
            targetorig[1]=target[1]
            #Permet de savoir combien en x et en y je dois les séparer selon la grosseur
            #du plus gros unit dans les selectedObjects
            unit =  self.units[int(units[0])]
            widths = [unit.SIZE[unit.type][0]]
            heights = [unit.SIZE[unit.type][1]]
            for i in range(0,len(units)-2):
                unit = self.units[int(units[i])]
                widths.append(unit.SIZE[unit.type][0])
                heights.append(unit.SIZE[unit.type][1])
            width = max(widths)
            height = max(heights)
            #Formation en carré selon le nombre de unit qui se déplace, OH YEAH
            if self.formation == "carre":
                #tuple qui contient les units qui peut contenir par ligne
                thatLine = []
                lineTaken = []
                #Nombre de ligne nécessaires pour faire la formation carré
                numberOfLines = math.sqrt(len(units)-1)
                if str(numberOfLines).split('.')[1] != '0':
                    numberOfLines+=1
                math.trunc(float(numberOfLines))
                numberOfLines = int(numberOfLines)
                #Remplissage du tuple de chaque ligne pour créer la formation par des False
                for l in range(0,numberOfLines):
                    thatLine = []
                    for k in range(0,numberOfLines):
                        thatLine.append(False)
                    lineTaken.append(thatLine)
                #Maintenant on fait la vérification de chaque Unit pour les placer dans le carré
                for i in range(0,len(units)-1):
                    goodPlace=False
                    line=0
                    while goodPlace==False:
                        for p in range(0,len(lineTaken[line])):
                            #Si la place n'est pas prise
                            if lineTaken[line][p]==False:
                                lineTaken[line][p]=True
                                target[0]=targetorig[0]+(p*width*1.2)
                                if target[0] < -1*(galaxy.width/2)+(width):
                                    target[0] = -1*(galaxy.width/2)+width
                                elif target[0] > (galaxy.width/2)-(width):
                                    target[0] = (galaxy.width/2)-width
                                target[1]=targetorig[1]-(line*height*1.2)
                                if target[1] < -1*(galaxy.height/2)+(height):
                                    target[1] = -1*(galaxy.height/2)+height
                                goodPlace=True
                                break
                        #Si le Unit n'a pas trouvé sa place, on avance d'une ligne
                        if goodPlace==False:
                            line+=1
                            if (len(lineTaken)-1)<line:
                                numberOfSpaces=1+line
                                thatLine=[]
                                for a in range(0,numberOfSpaces):
                                    thatLine.append(False)
                                lineTaken.append(thatLine)
                    #Lorsqu'il a trouvé sa place, on le fait bouger vers sa nouvelle target
                    self.units[int(units[i])].changeFlag(t.Target([target[0],target[1],0]),int(action))
            #Formation en triangle, FUCK YEAH
            elif self.formation == "triangle":
                #tuple qui contient le nombre de Unit par ligne
                thatLine=[]
                #tuple qui contient les X de la ligne précédente
                xLineBefore=[0,0,0,0,0,0,0,0,0,0,0,0]
                #On initialise directement la première ligne et on l'ajoute dans le tableau des lignes par
                #la suite
                thatLine.append([False])
                lineTaken.append(thatLine[False])
                xLineBefore[0] = target[0]
                #Après, on fait chercher un endroit dans la formation pour chaque Unit
                for i in range(0,len(units)-1):
                    goodPlace=False
                    line=0
                    while goodPlace==False:
                        for p in range(0,len(lineTaken[line])):
                            #S'il a trouvé une place vide
                            if lineTaken[line][p]==False:
                                lineTaken[line][p]=True
                                if line != 0:
                                    if p==len(lineTaken[line-1]):
                                        target[0]=targetorig[0]+(p*width)
                                        #jerome ajoute ca ici la largeur du vaisseau
                                        if target[0] > (galaxy.width/2)-width:
                                            target[0] = target[0]-(target[0]-(galaxy.width/2)+width)
                                        xLineBefore[p] = target[0]
                                    else:
                                        target[0]=xLineBefore[p]-width
                                        if target[0] < -1*(galaxy.width/2)+(width/2):
                                            target[0] = xLineBefore[p]
                                        elif target[0] > (galaxy.width/2)-(width/2):
                                            target[0] = target[0]-(target[0]-(galaxy.width/2)+width)
                                        xLineBefore[p] = target[0]
                                target[1]=targetorig[1]-(line*height)
                                if target[1] < -1*(galaxy.height/2)+(height/2):
                                    target[1] = targetorig[1]
                                goodPlace=True
                                break
                        #S'il n'a pas trouvé de place dans cette ligne
                        if goodPlace==False:
                            line+=1
                            #Si la prochaine ligne n'existe pas, on la crée
                            if (len(lineTaken)-1)<line:
                                numberOfSpaces=1+line
                                thatLine=[]
                                for a in range(0,numberOfSpaces):
                                    thatLine.append(False)
                                lineTaken.append(thatLine)
                    #Lorsqu'il a trouvé sa place, on le fait bouger à sa nouvelle Target  
                    self.units[int(units[i])].changeFlag(t.Target([target[0],target[1],0]),int(action))
        
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
        self.recalculateDefault()

    #Pour replacer la position du début sur le mothership
    def recalculateDefault(self):
        if self.defaultPos[0]-self.screenCenter[0] < (self.galaxy.width*-1)/2:
            self.position[0] = (self.galaxy.width*-1)/2+self.screenCenter[0]
        if self.defaultPos[0]+self.screenCenter[0] > self.galaxy.width/2:
            self.position[0] = (self.galaxy.width)/2-self.screenCenter[0]
        if self.defaultPos[1]-self.screenCenter[1] < (self.galaxy.height*-1)/2:
            self.position[1] = (self.galaxy.height*-1)/2+self.screenCenter[1]
        if self.defaultPos[1]+self.screenCenter[1] > self.galaxy.height/2:
            self.position[1] = (self.galaxy.height)/2-self.screenCenter[1]
        self.defaultPos = [self.position[0], self.position[1]]

    #Pour savoir si la position est dans le gameArea
    def inGameArea(self, position):
        if position[0] > self.position[0] - self.screenWidth/2 and position[0] < self.position + self.screenWidth/2:
            if position[1] > self.position[1] - self.screenHeight/2 and position[1] < self.position[1] + self.screenHeight/2:
                return True
        return False
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

    def placeOnLanding(self, landingZone):
        planet = self.player.currentPlanet
        self.position = [landingZone.position[0], landingZone.position[1]]
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


