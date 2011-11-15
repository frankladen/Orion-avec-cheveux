# -*- coding: UTF-8 -*-
from Target import *
from Flag import *
import World as w
from Helper import *
import math

class Unit(PlayerObject):
    DEFAULT = 0
    MOTHERSHIP = 1
    SCOUT = 2
    ATTACK_SHIP = 3
    TRANSPORT = 4
    CARGO = 5
    GROUND_UNIT = 6
    FRENCHNAME = ('Unité', 'Vaisseau mère','Scout', "Vaisseau d'attaque", "Vaisseau de Transport", "Cargo", 'Unité terrestre')
    MINERAL=0
    GAS=1
    FOOD=2
    SIZE=((0,0), (125,125), (18,15), (28,32), (32,29), (20,30),(24,24))
    MAX_HP = (50,500,50,100,125,75,100)
    MOVE_SPEED=(1.0, 0.0, 4.0, 2.0, 3.0, 3.0, 5.0)
    BUILD_TIME=(300, 0, 200, 400, 300, 250, 200)
    BUILD_COST=((50,50,1), (0,0,0), (50,0,1), (150,100,1), (75,20,1), (50,10,1), (50,10,1))
    VIEW_RANGE=(150, 400, 200, 150, 175, 175,200)
    
    def __init__(self, name, type, position, owner):
        PlayerObject.__init__(self, name, type, position, owner)
        if type <= self.GROUND_UNIT:
            self.moveSpeed=self.MOVE_SPEED[type]
        else:
            self.moveSpeed=self.MOVE_SPEED[self.DEFAULT]

    def action(self, parent):
        if self.flag.flagState == FlagState.MOVE or self.flag.flagState == FlagState.GROUND_MOVE:
            self.move()
        elif self.flag.flagState == FlagState.ATTACK:
            if isinstance(self.flag.finalTarget, TransportShip):
                if self.flag.finalTarget.landed:
                    parent.game.setAStandByFlag(self)
            killedIndex = self.attack(parent.game.players)
            if killedIndex[0] > -1:
                parent.killUnit(killedIndex)
        elif self.flag.flagState == FlagState.PATROL:
            unit = self.patrol()
            if unit != None:
                parent.setAnAttackFlag(unit, self)
        elif self.flag.flagState == FlagState.BUILD:
            self.build(self.flag.finalTarget)
        elif self.flag.flagState == FlagState.LAND:
            self.land(parent.game)
        elif self.flag.flagState == FlagState.GATHER:
            self.gather(parent, parent.game)
        elif isinstance(self, SpaceAttackUnit):
            parent.game.checkIfEnemyInRange(self)
    
    #La deplace d'un pas vers son flag et si elle est rendu, elle change arrete de bouger    
    def move(self):
        if Helper.calcDistance(self.position[0], self.position[1], self.flag.finalTarget.position[0], self.flag.finalTarget.position[1]) <= self.moveSpeed:
            endPos = [self.flag.finalTarget.position[0],self.flag.finalTarget.position[1]]
            self.position = endPos
            if self.flag.flagState == FlagState.MOVE:
                self.flag.flagState = FlagState.STANDBY
            elif self.flag.flagState == FlagState.MOVE+FlagState.ATTACK:
                self.flag.flagState = FlagState.ATTACK
        else:
            angle = Helper.calcAngle(self.position[0], self.position[1], self.flag.finalTarget.position[0], self.flag.finalTarget.position[1])
            temp = Helper.getAngledPoint(angle, self.moveSpeed, self.position[0], self.position[1])
            self.position[0] = temp[0]
            self.position[1] = temp[1]

    def patrol(self):
        arrived = True
        if self.position[0] < self.flag.finalTarget.position[0] or self.position[0] > self.flag.finalTarget.position[0]:
                if self.position[1] < self.flag.finalTarget.position[1] or self.position[1] > self.flag.finalTarget.position[1]:
                    self.move()
                    arrived = False
        if arrived == True:
            self.before = self.flag.initialTarget
            self.flag.initialTarget = self.flag.finalTarget
            self.flag.finalTarget = self.before
            self.move()
        return None

    def build(self, building):
        if Helper.calcDistance(self.position[0], self.position[1], self.flag.finalTarget.position[0], self.flag.finalTarget.position[1]) >= self.moveSpeed:
            self.move()
        else:
            endPos = [self.flag.finalTarget.position[0],self.flag.finalTarget.position[1]]
            self.position = endPos
            
            if building.buildingTimer < building.TIME[building.type]:
                building.buildingTimer += 1
            else:
                building.finished = True
                self.flag.flagState = FlagState.STANDBY
            
    #Efface la unit
    def eraseUnit(self):
        self.flag.flagState = 0
        self.position = [-1500,-1500,0]
        
    #Change le flag pour une nouvelle destination et un nouvel etat
    def changeFlag(self, finalTarget, state):
        #On doit vérifier si l'unité est encore vivante
        if self.isAlive:
            self.flag.initialTarget = t.Target([self.position[0],self.position[1],0])
            self.flag.finalTarget = finalTarget
            self.flag.flagState = state
            
    #Retourne le flag de la unit    
    def getFlag(self):
        return self.flag
              
class SpaceUnit(Unit):
    def __init__(self, name, type, position, owner):
        Unit.__init__(self, name, type, position, owner)

class GroundUnit(Unit):
    def __init__(self, name, type, position, owner, planetId, sunId):
        Unit.__init__(self, name, type, position, owner)
        self.sunId = sunId
        self.planetId = planetId
    
class GroundAttackUnit(GroundUnit):
    def __init__(self,attackspeed,attackdamage):
        super(GroundAttackUnit,self).__init__()
        self.AttackSpeed=attackspeed
        self.AttackDamage=attackdamage
    
class GroundBuildUnit(GroundUnit):
    def __init__(self):
        super(GroundBuildUnit,self).__init__()
    
    def build(self,building):
        print("build")

class Mothership(Unit):
    def __init__(self, name, type, position, owner):
        Unit.__init__(self, name, type, position, owner)
        self.flag.finalTarget = t.Target(position)
        self.unitBeingConstruct = []
        self.rallyPoint = [position[0],position[1]+(self.SIZE[type][1]/2)+5,0]
        self.owner = owner
        self.range=250.0
        self.AttackSpeed=10.0
        self.AttackDamage=3.0
        self.attackcount=self.AttackSpeed
        self.killCount = 0

    def action(self, parent):
        if self.isAlive:
            p = [self.position[0], self.position[1], 0]

            if (self.flag.flagState == FlagState.CREATE):
                print("Flag est sur CREATE, C'EST PAS SUPPOSÉ")

            elif self.flag.flagState == FlagState.BUILD_UNIT:
                self.progressUnitsConstruction()

            elif self.flag.flagState == FlagState.CANCEL_UNIT:
                self.unitBeingConstruct.pop(self.flag.finalTarget)
                self.flag.flagState = FlagState.BUILD_UNIT

            elif self.flag.flagState == FlagState.CHANGE_RALLY_POINT:
                target = self.flag.finalTarget
                target = target.strip("[")
                target = target.strip("]")
                target = target.split(",")
                for i in range(0, len(target)):
                    target[i]=math.trunc(float(target[i])) 
                self.rallyPoint = target
                self.flag.flagState = FlagState.BUILD_UNIT

            parent.game.checkIfEnemyInRange(self)

            if len(self.unitBeingConstruct) > 0:
                    if(self.isUnitFinished()):
                        parent.buildUnit()
            else:
                if self.flag.flagState != FlagState.ATTACK:
                    self.flag.flagState = FlagState.STANDBY
        else:
            self.unitBeingConstruct = []
            self.isAlive = False

    def progressUnitsConstruction(self):
        if len(self.unitBeingConstruct) > 0:
            self.flag.flagState = FlagState.BUILD_UNIT
            self.unitBeingConstruct[0].constructionProgress = self.unitBeingConstruct[0].constructionProgress + 1
        else:
            self.flag.flagState = FlagState.STANDBY

    def addUnitToQueue(self, unitType):
        p = [self.position[0], self.position[1], 0]
        if unitType == self.SCOUT:
            self.unitBeingConstruct.append(Unit('Scout', self.SCOUT, p, self.owner))
        elif unitType == self.ATTACK_SHIP:
            self.unitBeingConstruct.append(SpaceAttackUnit('Attack ship', self.ATTACK_SHIP, p, self.owner))
        elif unitType == self.CARGO:
            self.unitBeingConstruct.append(GatherShip('Cargo', self.CARGO, p, self.owner))
        elif unitType == self.TRANSPORT:
            self.unitBeingConstruct.append(TransportShip('Transport', self.TRANSPORT, p, self.owner))
    
    def isUnitFinished(self):
        if len(self.unitBeingConstruct) > 0:
            return self.unitBeingConstruct[0].constructionProgress >= self.unitBeingConstruct[0].buildTime

    def attack(self, players, unitToAttack=None):
        if unitToAttack == None:
            unitToAttack = self.flag.finalTarget
        index = -1
        killedOwner = -1
        distance = Helper.calcDistance(self.position[0], self.position[1], unitToAttack.position[0], unitToAttack.position[1])
        try:
            if distance > self.range :
                self.attackcount=self.AttackSpeed
            else:
                self.attackcount = self.attackcount - 1
                if self.attackcount == 0:
                    unitToAttack.hitpoints-=self.AttackDamage
                    if unitToAttack.hitpoints <= 0:
                        index = players[unitToAttack.owner].units.index(unitToAttack)
                        killedOwner = unitToAttack.owner
                        for i in players[self.owner].units:
                            if i.isAlive:
                                if i.flag.finalTarget == unitToAttack:
                                    i.flag = Flag(t.Target(i.position), t.Target(i.position), FlagState.BUILD_UNIT)
                                    i.attackcount=i.AttackSpeed
                        self.killCount +=1
                    self.attackcount=self.AttackSpeed
            return (index, killedOwner)
        except ValueError:
            self.flag = Flag(t.Target(self.position), t.Target(self.position), FlagState.BUILD_UNIT)
            return (-1, -1)

    def getUnitBeingConstructAt(self, index):
        return self.unitBeingConstruct[index]
        
class SpaceAttackUnit(SpaceUnit):
    def __init__(self, name, type, position, owner):
        SpaceUnit.__init__(self, name, type, position, owner)
        self.AttackSpeed=10.0
        self.AttackDamage=5.0
        self.range=150.0
        self.attackcount=self.AttackSpeed
        self.killCount = 0

    def changeFlag(self, finalTarget, state):
        self.attackcount=self.AttackSpeed
        Unit.changeFlag(self, finalTarget, state)
        
    def attack(self, players, unitToAttack=None):
        if unitToAttack == None:
            unitToAttack = self.flag.finalTarget
        index = -1
        killedOwner = -1
        distance = Helper.calcDistance(self.position[0], self.position[1], unitToAttack.position[0], unitToAttack.position[1])
        try:
            if distance > self.range :
                self.attackcount=self.AttackSpeed
                self.move()
            else:
                self.attackcount = self.attackcount - 1
                if self.attackcount == 0:
                    unitToAttack.hitpoints-=self.AttackDamage
                    if unitToAttack.hitpoints <= 0:
                        index = players[unitToAttack.owner].units.index(unitToAttack)
                        killedOwner = unitToAttack.owner
                        for i in players[self.owner].units:
                            if i.isAlive:
                                if i.flag.finalTarget == unitToAttack:
                                    i.flag = Flag(t.Target(i.position), t.Target(i.position), FlagState.STANDBY)
                                    i.attackcount=i.AttackSpeed
                        self.killCount +=1
                    self.attackcount=self.AttackSpeed
            return (index, killedOwner)
        except ValueError:
            self.flag = Flag(t.Target(self.position), t.Target(self.position), FlagState.STANDBY)
            return (-1, -1)

    def patrol(self, players):
        arrived = True
        if self.position[0] < self.flag.finalTarget.position[0] or self.position[0] > self.flag.finalTarget.position[0]:
                if self.position[1] < self.flag.finalTarget.position[1] or self.position[1] > self.flag.finalTarget.position[1]:
                    for p in players:
                        if players.index(p) != self.owner:
                            for uni in p.units:
                                if uni.position[0] > self.position[0]-self.range and uni.position[0] < self.position[0]+self.range:
                                    if uni.position[1] > self.position[1]-self.range and uni.position[1] < self.position[1]+self.range:
                                        return uni
                    self.move()
                    arrived = False
        if arrived == True:
            self.before = self.flag.initialTarget
            self.flag.initialTarget = self.flag.finalTarget
            self.flag.finalTarget = self.before

        return None

class TransportShip(SpaceUnit):
    def __init__(self, name, type, position, owner):
        SpaceUnit.__init__(self, name, type, position, owner)
        self.landed = False
        self.capacity = 10
        self.units = []
        #self.units.append(GroundUnit('Builder', self.GROUND_UNIT, [0,0,0], self.owner,-1,-1))

    def land(self, game):
        playerId = game.playerId
        galaxy = game.galaxy
        planet = self.flag.finalTarget
        planetId = 0
        sunId = 0
        for i in galaxy.solarSystemList:
            for j in i.planets:
                if planet == j:
                    planetId = i.planets.index(j)
                    sunId = galaxy.solarSystemList.index(i)
        self.arrived = True
        if self.position[0] < planet.position[0] or self.position[0] > planet.position[0]:
            if self.position[1] < planet.position[1] or self.position[1] > planet.position[1]:
                self.arrived = False
                self.move()
        if self.arrived:
            player = game.players[playerId]
            player.currentPlanet = planet
            alreadyLanded = False
            for i in planet.landingZones:
                if i.ownerId == playerId:
                    alreadyLanded = True
            if not alreadyLanded:
                if len(planet.landingZones) < 4:
                    landingZone = planet.addLandingZone(playerId, self)
                    self.landed = True
                    if playerId == game.playerId:
                        cam = game.players[playerId].camera
                        cam.position = [landingZone.position[0], landingZone.position[1]]
                        cam.placeOnLanding()
                    for i in self.units:
                        i.position = [landingZone.position[0] + 40, landingZone.position[1]]
                        i.planetId = planetId
                        i.sunId = sunId
                        planet.units.append(i)
                        self.units.pop(self.units.index(i))
                    if self in game.players[game.playerId].selectedObjects:
                        game.players[game.playerId].selectedObjects.pop(game.players[game.playerId].selectedObjects.index(self))
            else:
                landingZone = None
                for i in planet.landingZones:
                    if i.ownerId == playerId:
                        landingZone = i
                if landingZone.LandedShip == None:
                    self.landed = True
                    if playerId == game.playerId:
                        cam = game.players[playerId].camera
                        cam.position = [landingZone.position[0], landingZone.position[1]]
                        cam.placeOnLanding()
                    for i in self.units:
                        i.position = [landingZone.position[0] + 40, landingZone.position[1]]
                        i.planetId = planetId
                        i.sunId = sunId
                        planet.units.append(i)
                        self.units.pop(self.units.index(i))
                    landingZone.LandedShip = self
            if playerId == game.playerId:
                game.parent.changeBackground('PLANET')
                game.parent.drawPlanetGround(planet)
            self.flag = Flag (self.position, self.position, FlagState.STANDBY)
        
    def takeOff(self, planet):
        self.landed = False
        for i in planet.landingZones:
            if i.ownerId == self.owner:
                i.LandedShip = None

class GatherShip(SpaceUnit):
    GATHERTIME=20
    def __init__(self, name, type, position, owner):
        SpaceUnit.__init__(self, name, type, position, owner)
        self.maxGather = 50
        self.gatherSpeed = 20
        self.container = [0,0]
        self.returning = False

    def gather(self, player, game):
        ressource = self.flag.finalTarget
        arrived = True
        if isinstance(self.flag.finalTarget, w.AstronomicalObject):
            if self.position[0] < ressource.position[0] or self.position[0] > ressource.position[0]:
                if self.position[1] < ressource.position[1] or self.position[1] > ressource.position[1]:
                    arrived = False
                    self.move()
            if arrived:
                if self.gatherSpeed==0:
                    if ressource.type=='asteroid':
                        if self.container[0] < self.maxGather:
                            if ressource.mineralQte >= 5:
                                self.container[0]+=5
                                ressource.mineralQte-=5
                            else:
                                self.container[0]+=ressource.mineralQte
                                ressource.mineralQte = 0
                                self.flag.initialTarget = self.flag.finalTarget
                                self.flag.finalTarget = player.motherShip
                                game.parent.redrawMinimap()
                            self.gatherSpeed = 20
                        else:
                            self.flag.initialTarget = self.flag.finalTarget
                            self.flag.finalTarget = player.motherShip
                    else:
                        if self.container[1]<self.maxGather:
                            if ressource.gazQte >= 5:
                                self.container[1]+=5
                                ressource.gazQte-=5
                            else:
                                self.container[1]+=ressource.gazQte
                                ressource.gazQte = 0
                                self.flag.initialTarget = self.flag.finalTarget
                                self.flag.finalTarget = player.motherShip
                                game.parent.redrawMinimap()
                            self.gatherSpeed = 20
                        else:
                            self.flag.initialTarget = self.flag.finalTarget
                            self.flag.finalTarget = player.getNearestReturnRessourceCenter(self.position)
                else:
                    self.gatherSpeed-=1
        else:
            if self.position[0] < ressource.position[0] or self.position[0] > ressource.position[0]:
                if self.position[1] < ressource.position[1] or self.position[1] > ressource.position[1]:
                    arrived = False
                    self.move()
            if arrived:
                player.ressources[player.MINERAL] += self.container[0]
                player.ressources[player.GAS] += self.container[1]
                self.container[0] = 0
                self.container[1] = 0
                if isinstance(self.flag.initialTarget, w.AstronomicalObject):
                    self.flag.finalTarget = self.flag.initialTarget
                    if self.flag.finalTarget.type == 'asteroid':
                        if self.flag.finalTarget.mineralQte == 0:
                            self.flag.flagState = FlagState.STANDBY
                    else:
                        if self.flag.finalTarget.gazQte == 0:
                            self.flag.flagState = FlagState.STANDBY
                else:
                    self.flag.finalTarget = self.position
                    self.flag.flagState = FlagState.STANDBY
 
