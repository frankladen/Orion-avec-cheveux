# -*- coding: UTF-8 -*-
from Target import *
from Flag import *
import World as w
import Player as p
import Building as b
from Helper import *
import math

class Unit(PlayerObject):
    DEFAULT = 0
    SCOUT = 1
    ATTACK_SHIP = 2
    TRANSPORT = 3
    CARGO = 4
    GROUND_UNIT = 5
    GROUND_GATHER = 6
    SPECIAL_GATHER = 7
    GROUND_ATTACK = 8
    GROUND_BUILDER_UNIT = 9
    HEALING_UNIT = 10
    SPACE_BUILDING_ATTACK = 11
    NYAN_CAT = 12
    NAME = ('Unité','Scout', "Vaisseau d'attaque", "Vaisseau de Transport", "Cargo", 'Unité terrestre', 'Unité de collecte', 'Unité spéciale', 'Unité d\'attaque', 'Unité de construction', 'Drone de Réparation', "Unité d'attaque lourde", "Nyan cat")
    MINERAL=0
    GAS=1
    FOOD=2
    SIZE=((0,0),  (18,15), (28,32), (32,29), (20,30), (24,24), (20,38), (32,32), (36,33), (23,37), (30,37), (60,33), (35,25))
    MAX_HP = (50, 50, 100,125, 75, 100, 100, 100, 100,100, 100, 100, 175)
    MOVE_SPEED=(1.0,  4.0, 2.0, 3.0, 3.0, 5.0, 5.0, 3.0, 3.5, 4.0, 3.0, 1.5, 7.0)
    ATTACK_SPEED=(0,0,10,0,0,0,0,0,15,0,0, 125, 6)
    ATTACK_DAMAGE=(0,0,5,0,0,0,0,0,12,0,0, 15, 50)
    ATTACK_RANGE=(0,0,150,0,0,0,0,0,150,0,0, 300, 450)
    BUILD_TIME=(300,  200, 400, 300, 250, 200, 200, 200, 200, 200,200, 500, 0)
    BUILD_COST=((50,50,1),  (100,50,1), (300,300,1), (500,500,1), (75,0,1), (150,100,1),(50,75,1), (75,125,1), (100,80,1), (65,90,1),(75,50,1),(400,400,1), (0,0,0))
    VIEW_RANGE=(150,  250, 200, 175, 175,200, 200, 200, 200, 200, 200, 300, 450)
    SCORE_VALUE=(10,10,20,30,15,10,15,25,20,15,20,25,50)
    
    def __init__(self, type, position, owner):
        PlayerObject.__init__(self, type, position, owner)
        self.viewRange = self.VIEW_RANGE[type]
        self.hitpoints = self.MAX_HP[type]
        self.maxHP=self.hitpoints
        self.buildTime = self.BUILD_TIME[type]
        self.buildCost = self.BUILD_COST[type]
        self.name = self.NAME[type]
        self.moveSpeed = self.MOVE_SPEED[type]

    def action(self, parent):
        if self.flag.flagState == FlagState.MOVE or self.flag.flagState == FlagState.GROUND_MOVE:
            self.move()
        elif self.flag.flagState == FlagState.ATTACK:
            if isinstance(self.flag.finalTarget, TransportShip):
                if self.flag.finalTarget.landed == True:
                    self.flag = Flag(self, self, FlagState.STANDBY)
            if self.flag.flagState == FlagState.ATTACK:
                killedIndex = self.attack(parent.game.players)
                if killedIndex[0] > -1:
                    parent.killUnit(killedIndex)
        elif self.flag.flagState == FlagState.PATROL:
            self.patrol()
        elif self.flag.flagState == FlagState.BUILD:
            self.build(self.flag.finalTarget, parent)
    
    #La deplace d'un pas vers son flag et si elle est rendu, elle change arrete de bouger    
    def move(self):
        if Helper.calcDistance(self.position[0], self.position[1], self.flag.finalTarget.position[0], self.flag.finalTarget.position[1]) <= self.moveSpeed:
            endPos = [self.flag.finalTarget.position[0],self.flag.finalTarget.position[1]]
            self.position = endPos
            if self.flag.flagState == FlagState.MOVE or self.flag.flagState == FlagState.GROUND_MOVE:
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

    def select(self, position):
        if self.isAlive:
            if self.position[0] >= position[0] - self.SIZE[self.type][0]/2 and self.position[0] <= position[0] + self.SIZE[self.type][0]/2:
                if self.position[1] >= position[1] - self.SIZE[self.type][1]/2 and self.position[1] <= position[1] + self.SIZE[self.type][1]/2:
                    return self
        return None

    def boxSelect(self, startPos, endPos):
        if self.isAlive:
            if self.position[0] > startPos[0] - self.SIZE[self.type][0]/2 and self.position[0] < endPos[0] + self.SIZE[self.type][0]/2:
                if self.position[1] > startPos[1] - self.SIZE[self.type][1]/2 and  self.position[1] < endPos[1] + self.SIZE[self.type][1]/2:
                    return self
        return None

    def build(self, building, player):
        if Helper.calcDistance(self.position[0], self.position[1], self.flag.finalTarget.position[0], self.flag.finalTarget.position[1]) >= self.moveSpeed:
            self.move()
        else:
            endPos = [self.flag.finalTarget.position[0],self.flag.finalTarget.position[1]]
            self.position = endPos
            
            if building.buildingTimer < building.buildTime:
                building.buildingTimer += 1
                building.hitpoints += (1/building.buildTime)*building.MAX_HP[building.type]
            else:
                building.finished = True
                if building.hitpoints >= building.MAX_HP[building.type]-1:
                    building.hitpoints = building.MAX_HP[building.type]
                self.flag.flagState = FlagState.STANDBY
                if isinstance(building, b.Mothership):
                    building.armor = building.MAX_ARMOR
                building.applyBonuses(player.BONUS)
            
    #Efface la unit
    def eraseUnit(self):
        self.flag.flagState = 0
        self.position = [-1500,-1500,0]

    #Applique les bonus du Unit selon les upgrades
    def applyBonuses(self, bonuses):
        self.moveSpeed = self.MOVE_SPEED[self.type]+bonuses[p.Player.MOVE_SPEED_BONUS]
        self.viewRange = self.VIEW_RANGE[self.type]+bonuses[p.Player.VIEW_RANGE_BONUS]
        
    #Retourne le flag de la unit    
    def getFlag(self):
        return self.flag

    def getKilledCount(self):
        return 0
              
class SpaceUnit(Unit):
    def __init__(self,  type, position, owner):
        Unit.__init__(self, type, position, owner)

class GroundUnit(Unit):
    def __init__(self, type, position, owner, planetId, sunId, isLanded = False):
        Unit.__init__(self, type, position, owner)
        self.sunId = sunId
        self.planetId = planetId
        self.planet = None
        self.isLanded = isLanded

    def isInRange(self, position, range, onPlanet = False, planetId = -1, solarSystemId = -1):
        if self.isLanded and onPlanet:
            if self.sunId == solarSystemId and self.planetId == planetId:
                if self.position[0] > position[0]-range and self.position[0] < position[0]+range:
                    if self.position[1] > position[1]-range and self.position[1] < position[1]+range:
                        return self
        return None

    def land(self, planet, position):
        self.isLanded = True
        self.position = position
        self.planet = planet
        self.planetId = planet.id
        self.sunId = planet.solarSystem.sunId
        planet.units.append(self)

    def takeOff(self):
        self.isLanded = False
        self.planetId = -1
        self.sunId = -1
        self.planet = None

    def action(self, parent):
        if self.flag.flagState == FlagState.LOAD:
            self.load(parent.game)
        else:
            Unit.action(self, parent)

    def load(self, game):
        landingZone = self.flag.finalTarget
        planet = game.galaxy.solarSystemList[landingZone.sunId].planets[landingZone.planetId]
        arrived = True
        if self.position[0] < landingZone.position[0] or self.position[0] > landingZone.position[0]:
            if self.position[1] < landingZone.position[1] or self.position[1] > landingZone.position[1]:
                arrived = False
                self.move()
        if arrived and landingZone.LandedShip != None:
            if len(landingZone.LandedShip.units) <= landingZone.LandedShip.capacity:
                self.planet = None
                self.position = [-100000, -100000]
                self.planetId = -1
                self.sunId = -1
                planet.units.pop(planet.units.index(self))
                landingZone.LandedShip.units.append(self)
                if self in game.players[self.owner].selectedObjects:
                    game.players[self.owner].selectedObjects.pop(game.players[self.owner].selectedObjects.index(self))
                self.flag.flagState = FlagState.STANDBY
            else:
                self.flag.flagState = FlagState.STANDBY

class GroundBuilderUnit(GroundUnit):
    def __init__(self,  type, position, owner, planetId, sunId, isLanded = False):
        GroundUnit.__init__(self,  type, position, owner, planetId, sunId, isLanded)

    def action(self, parent):
        if self.flag.flagState == FlagState.BUILD:
            self.build(self.flag.finalTarget, parent)
        else:
            GroundUnit.action(self, parent)

    def build(self, building, player):
        if Helper.calcDistance(self.position[0], self.position[1], self.flag.finalTarget.position[0], self.flag.finalTarget.position[1]) >= self.moveSpeed:
            self.move()
        else:
            endPos = [self.flag.finalTarget.position[0],self.flag.finalTarget.position[1]]
            self.position = endPos
            
            if building.buildingTimer < building.buildTime:
                building.buildingTimer += 1
                building.hitpoints += (1/building.buildTime)*building.MAX_HP[building.type]
            else:
                building.finished = True
                if building.hitpoints >= building.MAX_HP[building.type]-1:
                    building.hitpoints = building.MAX_HP[building.type]
                self.flag.flagState = FlagState.STANDBY
                if building.type == b.Building.FARM:
                    player.MAX_FOOD +=5

    def load(self, game):
        landingZone = self.flag.finalTarget
        planet = game.galaxy.solarSystemList[landingZone.sunId].planets[landingZone.planetId]
        arrived = True
        if self.position[0] < landingZone.position[0] or self.position[0] > landingZone.position[0]:
            if self.position[1] < landingZone.position[1] or self.position[1] > landingZone.position[1]:
                arrived = False
                self.move()
        if arrived and landingZone.LandedShip != None:
            if len(landingZone.LandedShip.units) <= landingZone.LandedShip.capacity:
                self.planet = None
                self.position = [-100000, -100000]
                self.planetId = -1
                self.sunId = -1
                planet.units.pop(planet.units.index(self))
                landingZone.LandedShip.units.append(self)
                if self in game.players[self.owner].selectedObjects:
                    game.players[self.owner].selectedObjects.pop(game.players[self.owner].selectedObjects.index(self))
                self.flag.flagState = FlagState.STANDBY
            else:
                self.flag.flagState = FlagState.STANDBY
               
            
class GroundGatherUnit(GroundUnit):
    GATHERTIME = 20
    def __init__(self,  type, position, owner, planetId, sunId, isLanded = False):
        GroundUnit.__init__(self, type, position, owner, planetId, sunId, isLanded)
        self.maxGather = 50
        self.gatherSpeed = self.GATHERTIME
        self.container = [0,0]
        self.returning = False

    def action(self, parent):
        if self.flag.flagState == FlagState.GROUND_GATHER:
            self.gather(parent, parent.game)
        elif self.flag.flagState == FlagState.LOAD:
            self.load(parent, parent.game)
        else:
            GroundUnit.action(self, parent)

    def gather(self, player, game):
        ressource = self.flag.finalTarget
        arrived = True
        if isinstance(ressource, w.MineralStack) or isinstance(ressource, w.GazStack):
            if self.position[0] < ressource.position[0] or self.position[0] > ressource.position[0]:
                if self.position[1] < ressource.position[1] or self.position[1] > ressource.position[1]:
                    arrived = False
                    self.move()
            if arrived:
                if self.gatherSpeed==0:
                    if isinstance(ressource, w.MineralStack):
                        if self.container[0] < self.maxGather:
                            if ressource.nbMinerals >= 5:
                                self.container[0]+=5
                                ressource.nbMinerals-=5
                            else:
                                self.container[0]+=ressource.nbMinerals
                                ressource.nbMinerals = 0
                                self.flag.initialTarget = self.flag.finalTarget
                                self.flag.finalTarget =player.getNearestReturnRessourceCenterOnSpace(self.position, self)
                                game.parent.redrawMinimap()
                            self.gatherSpeed = self.GATHERTIME
                        else:
                            self.flag.initialTarget = self.flag.finalTarget
                            self.flag.finalTarget = player.getNearestReturnRessourceCenterOnSpace(self.position, self)
                    else:
                        if self.container[1]<self.maxGather:
                            if ressource.nbGaz >= 5:
                                self.container[1]+=5
                                ressource.nbGaz-=5
                            else:
                                self.container[1]+=ressource.nbGaz
                                ressource.nbGaz = 0
                                self.flag.initialTarget = self.flag.finalTarget
                                self.flag.finalTarget = player.getNearestReturnRessourceCenterOnSpace(self.position, self)
                                game.parent.redrawMinimap()
                            self.gatherSpeed = self.GATHERTIME
                        else:
                            self.flag.initialTarget = self.flag.finalTarget
                            self.flag.finalTarget = player.getNearestReturnRessourceCenterOnSpace(self.position, self)
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
                if isinstance(self.flag.initialTarget, w.MineralStack) or isinstance(self.flag.initialTarget, w.GazStack):
                    self.flag.finalTarget = self.flag.initialTarget
                    if isinstance(self.flag.initialTarget, w.MineralStack):
                        if self.flag.finalTarget.nbMinerals == 0:
                            if game.getCurrentPlanet() == self.planet:
                                player.notifications.append(Notification(self.position, Notification.FINISH_GATHER))
                            else:
                                player.notifications.append(Notification(self.planet.position, Notification.FINISH_GATHER))
                            self.flag.flagState = FlagState.STANDBY
                    else:
                        if self.flag.finalTarget.nbGaz == 0:
                            if game.getCurrentPlanet() == self.planet:
                                player.notifications.append(Notification(self.position, Notification.FINISH_GATHER))
                            else:
                                player.notifications.append(Notification(self.planet.position, Notification.FINISH_GATHER))
                            self.flag.flagState = FlagState.STANDBY
                else:
                    self.flag.finalTarget = self.position
                    self.flag.flagState = FlagState.STANDBY
					
    def load(self, player, game):
        landingZone = self.flag.finalTarget
        planet = game.galaxy.solarSystemList[landingZone.sunId].planets[landingZone.planetId]
        arrived = True
        if self.position[0] < landingZone.position[0] or self.position[0] > landingZone.position[0]:
            if self.position[1] < landingZone.position[1] or self.position[1] > landingZone.position[1]:
                arrived = False
                self.move()
        if arrived and landingZone.LandedShip != None:
            if len(landingZone.LandedShip.units) <= landingZone.LandedShip.capacity:
                player.ressources[player.MINERAL] += self.container[player.MINERAL]
                player.ressources[player.GAS] += self.container[player.GAS]
                self.container[player.MINERAL] = 0
                self.container[player.GAS] = 0
                self.planet = None
                self.position = [-100000, -100000]
                self.planetId = -1
                self.sunId = -1
                planet.units.pop(planet.units.index(self))
                landingZone.LandedShip.units.append(self)
                if self in player.selectedObjects:
                    player.selectedObjects.pop(player.selectedObjects.index(self))
                self.flag.flagState = FlagState.STANDBY
            else:
                self.flag.flagState = FlagState.STANDBY

class SpecialGather(GroundGatherUnit) :
    GATHERTIME = 1200
    def __init__(self,  type, position, owner, planetId, sunId, isLanded = False):
        GroundGatherUnit.__init__(self, type, position, owner, planetId, sunId, isLanded)
        self.maxGather = 1
        self.gatherSpeed = self.GATHERTIME
        self.container = 0
        self.returning = False
        self.isGathering = False

    def action(self, parent):
        self.isGathering = False
        if self.flag.flagState == FlagState.GROUND_GATHER:
            self.gather(parent, parent.game)
        elif self.flag.flagState == FlagState.LOAD:
            self.load(parent, parent.game)
        else:
            GroundUnit.action(self, parent)
    def calcProgression(self):
        return self.gatherSpeed/30

    def getColorProgression(self):
        if self.gatherSpeed >= 800:
            return 'green'
        elif self.gatherSpeed >= 400:
            return 'yellow'
        else:
            return 'red'

    def gather(self, player, game):
        ressource = self.flag.finalTarget
        arrived = True
        if isinstance(ressource, w.NuclearSite):
            if self.position[0] < ressource.position[0] or self.position[0] > ressource.position[0]:
                if self.position[1] < ressource.position[1] or self.position[1] > ressource.position[1]:
                    arrived = False
                    self.move()
            if arrived:
                if self.gatherSpeed==0:
                    if self.container < self.maxGather:
                        if ressource.nbRessource > 0:
                            self.container+=1
                            ressource.nbRessource-=1
                        self.gatherSpeed = self.GATHERTIME
                        self.flag.initialTarget = self.flag.finalTarget
                        self.flag.finalTarget = self.planet.getLandingSpot(player.id)
                else:
                    self.isGathering = True
                    self.gatherSpeed-=1
        else:
            if self.position[0] < ressource.position[0] or self.position[0] > ressource.position[0]:
                if self.position[1] < ressource.position[1] or self.position[1] > ressource.position[1]:
                    arrived = False
                    self.move()
            if arrived:
                if ressource.LandedShip != None:
                    ressource.LandedShip.nuclear += self.container
                else:
                    ressource.nuclear += self.container
                self.container = 0
                self.flag.finalTarget = self.position
                player.notifications.append(Notification(self.position, Notification.FINISH_GATHER))
                self.flag.flagState = FlagState.STANDBY
				
    def load(self, player, game):
        landingZone = self.flag.finalTarget
        planet = game.galaxy.solarSystemList[landingZone.sunId].planets[landingZone.planetId]
        arrived = True
        if self.position[0] < landingZone.position[0] or self.position[0] > landingZone.position[0]:
            if self.position[1] < landingZone.position[1] or self.position[1] > landingZone.position[1]:
                arrived = False
                self.move()
        if arrived and landingZone.LandedShip != None:
            if len(landingZone.LandedShip.units) <= landingZone.LandedShip.capacity:
                landingZone.LandedShip.nuclear += self.container
                self.container = 0
                self.planet = None
                self.position = [-100000, -100000]
                self.planetId = -1
                self.sunId = -1
                planet.units.pop(planet.units.index(self))
                landingZone.LandedShip.units.append(self)
                if self in player.selectedObjects:
                    player.selectedObjects.pop(player.selectedObjects.index(self))
                self.flag.flagState = FlagState.STANDBY
            else:
                self.flag.flagState = FlagState.STANDBY

class HealingUnit(SpaceUnit):

        def __init__(self, type, position, owner):
            SpaceUnit.__init__(self,  type, position, owner)
            self.unitsToHeal = []
            self.HEALING_RANGE = 50
            self.HEALING_SPEED = 40
            self.HEALING_POWER = 1
            self.ctr = 0

        
        
        def action(self,parent):
            if self.flag.flagState == FlagState.HEAL:
                target = self.flag.finalTarget
                if (Helper.calcDistance(self.position[0], self.position[1], target.position[0], target.position[1])) >= self.HEALING_RANGE:
                    self.move()
                else:
                    self.ctr+=1
                    if self.ctr == self.HEALING_SPEED and self.flag.finalTarget.hitpoints <self.flag.finalTarget.maxHP:
                        self.flag.finalTarget.hitpoints += self.HEALING_POWER
                        self.ctr = 0
                    elif self.flag.finalTarget.hitpoints >= self.flag.finalTarget.maxHP:
                        self.flag.finalTarget.hitpoints = self.flag.finalTarget.maxHP
                        self.flag.flagState = FlagState.STANDBY
                
            else:
                SpaceUnit.action(self, parent)

            

class GroundAttackUnit(GroundUnit):
    def __init__(self,  type, position, owner, planetId, sunId, isLanded = False):
        GroundUnit.__init__(self,  type, position, owner, planetId, sunId, isLanded)
        self.range=self.ATTACK_RANGE[type]
        self.AttackSpeed=self.ATTACK_SPEED[type]
        self.AttackDamage=self.ATTACK_DAMAGE[type]
        self.attackcount=self.AttackSpeed
        self.killCount = 0

    def action(self, parent):
        if self.isLanded:
            if self.flag.flagState == FlagState.ATTACK:
                killedIndex = self.attack(parent.game.players)
                if killedIndex[0] > -1:
                    parent.killUnit(killedIndex)
            elif self.flag.flagState == FlagState.PATROL:
                self.patrol()
                parent.game.checkIfEnemyInRange(self, True, self.planetId, self.sunId)
            elif self.flag.flagState == FlagState.STANDBY:
                parent.game.checkIfEnemyInRange(self, True, self.planetId, self.sunId)
            else:
                GroundUnit.action(self, parent)

    def attack(self, players, unitToAttack=None):
        if unitToAttack == None:
            unitToAttack = self.flag.finalTarget
        index = -1
        killedOwner = -1
        isBuilding = False
        distance = Helper.calcDistance(self.position[0], self.position[1], unitToAttack.position[0], unitToAttack.position[1])
        try:
            if distance > self.range :
                self.attackcount=self.AttackSpeed
                self.move()
            else:
                self.attackcount = self.attackcount - 1
                if self.attackcount == 0:
                    if unitToAttack.takeDammage(self.AttackDamage, players):
                        if isinstance(unitToAttack, b.Building) == False:
                            index = players[unitToAttack.owner].units.index(unitToAttack)
                        else:
                            index = players[unitToAttack.owner].buildings.index(unitToAttack)
                            isBuilding = True
                        killedOwner = unitToAttack.owner
                        self.killCount +=1
                        if self.killCount % 2 == 1:
                            self.AttackDamage += 1
                    self.attackcount=self.AttackSpeed
            return (index, killedOwner, isBuilding)
        except ValueError:
            self.flag = Flag(t.Target(self.position), t.Target(self.position), FlagState.STANDBY)
            return (-1, -1)

    def applyBonuses(self, bonuses):
        SpaceAttackUnit.applyBonuses(self, bonuses)

    def getKilledCount(self):
        return self.killCount
                    
class SpaceBuildingAttack(SpaceUnit):
    def __init__(self,  type, position, owner):
        SpaceUnit.__init__(self,  type, position, owner)
        self.range=self.ATTACK_RANGE[type]
        self.AttackSpeed=self.ATTACK_SPEED[type]
        self.AttackDamage=self.ATTACK_DAMAGE[type]
        self.attackcount=self.AttackSpeed
        self.killCount = 0

    def action(self, parent):
        if self.flag.flagState == FlagState.ATTACK_BUILDING:
            self.attack(parent.game.players)
        elif self.flag.flagState == FlagState.PATROL:
            self.patrol()
        else:
            Unit.action(self, parent)

    def changeFlag(self, finalTarget, state):
        self.attackcount=self.AttackSpeed
        Unit.changeFlag(self, finalTarget, state)
        
    def attack(self, players):
        pos = self.flag.finalTarget.position
        distance = Helper.calcDistance(self.position[0], self.position[1], pos[0], pos[1])
        if distance > self.range :
            self.attackcount=5
            self.move()
        else:
            self.attackcount -= 1
            if self.attackcount == 0:
                players[self.owner].bullets.append(Bullet([self.position[0], self.position[1], 0],self.owner,players[self.owner].units.index(self)))
                players[self.owner].bullets[len(players[self.owner].bullets)-1].changeFlag(t.Target([pos[0],pos[1],0]),FlagState.ATTACK)
                self.attackcount=self.AttackSpeed



    #Applique les bonus du Unit selon les upgrades
    def applyBonuses(self, bonuses):
        Unit.applyBonuses(self, bonuses)
        self.AttackSpeed=self.ATTACK_SPEED[self.type]+bonuses[p.Player.ATTACK_SPEED_BONUS]
        self.AttackDamage=self.ATTACK_DAMAGE[self.type]+bonuses[p.Player.ATTACK_DAMAGE_BONUS]
        self.range=self.ATTACK_RANGE[self.type]+bonuses[p.Player.ATTACK_RANGE_BONUS]

    def getKilledCount(self):
        return self.killCount
        
class SpaceAttackUnit(SpaceUnit):
    def __init__(self,  type, position, owner):
        SpaceUnit.__init__(self,  type, position, owner)
        self.range=self.ATTACK_RANGE[type]
        self.AttackSpeed=self.ATTACK_SPEED[type]
        self.AttackDamage=self.ATTACK_DAMAGE[type]
        self.attackcount=self.AttackSpeed
        self.killCount = 0

    def action(self, parent):
        if self.flag.flagState == FlagState.ATTACK:
            if isinstance(self.flag.finalTarget, TransportShip):
                if self.flag.finalTarget.landed == True:
                    self.flag = Flag(self,self,FlagState.STANDBY)
            if self.flag.flagState == FlagState.ATTACK:
                killedIndex = self.attack(parent.game.players)
                if killedIndex[0] > -1:
                    parent.killUnit(killedIndex)
        elif self.flag.flagState == FlagState.PATROL:
            self.patrol()
            parent.game.checkIfEnemyInRange(self)
        elif self.flag.flagState == FlagState.STANDBY:
            parent.game.checkIfEnemyInRange(self)
        else:
            Unit.action(self, parent)

    def changeFlag(self, finalTarget, state):
        self.attackcount=self.AttackSpeed
        Unit.changeFlag(self, finalTarget, state)
        
    def attack(self, players, unitToAttack=None):
        if unitToAttack == None:
            unitToAttack = self.flag.finalTarget
        index = -1
        killedOwner = -1
        isBuilding = False
        distance = Helper.calcDistance(self.position[0], self.position[1], unitToAttack.position[0], unitToAttack.position[1])
        try:
            if distance > self.range :
                self.attackcount=self.AttackSpeed
                self.move()
            else:
                self.attackcount = self.attackcount - 1
                if self.attackcount == 0:
                    if unitToAttack.takeDammage(self.AttackDamage, players):
                        if isinstance(unitToAttack, b.Building) == False:
                            index = players[unitToAttack.owner].units.index(unitToAttack)
                        else:
                            index = players[unitToAttack.owner].buildings.index(unitToAttack)
                            isBuilding = True
                        killedOwner = unitToAttack.owner
                        self.killCount +=1
                        if self.killCount % 2 == 1:
                            self.AttackDamage += 1
                    self.attackcount=self.AttackSpeed
            return (index, killedOwner, isBuilding)
        except ValueError:
            self.flag = Flag(t.Target(self.position), t.Target(self.position), FlagState.STANDBY)
            return (-1, -1)


    #Applique les bonus du Unit selon les upgrades
    def applyBonuses(self, bonuses):
        Unit.applyBonuses(self, bonuses)
        self.AttackSpeed=self.ATTACK_SPEED[self.type]+bonuses[p.Player.ATTACK_SPEED_BONUS]
        self.AttackDamage=self.ATTACK_DAMAGE[self.type]+bonuses[p.Player.ATTACK_DAMAGE_BONUS]
        self.range=self.ATTACK_RANGE[self.type]+bonuses[p.Player.ATTACK_RANGE_BONUS]

    def getKilledCount(self):
        return self.killCount

class TransportShip(SpaceUnit):
    def __init__(self, type, position, owner):
        SpaceUnit.__init__(self,  type, position, owner)
        self.landed = False
        self.capacity = 10
        self.units = []
        self.planetId = -1
        self.sunId = -1
        self.planet = None
        self.nuclear = 0

    def action(self, parent):
        if self.flag.flagState == FlagState.LAND:
            self.land(parent.game)
        elif self.flag.flagState == FlagState.GATHER:
            self.returnToMothership(parent)
        else:
            Unit.action(self, parent)


    def isInRange(self, position, range, onPlanet = False, planetId = -1, solarSystemId = -1):
        if self.landed == onPlanet and onPlanet == False:
            return Unit.isInRange(self, position, range)
        return None

    def select(self, position):
        if self.isAlive and not self.landed:
            if self.position[0] >= position[0] - self.SIZE[self.type][0]/2 and self.position[0] <= position[0] + self.SIZE[self.type][0]/2:
                if self.position[1] >= position[1] - self.SIZE[self.type][1]/2 and self.position[1] <= position[1] + self.SIZE[self.type][1]/2:
                    return self
        return None

    def boxSelect(self, startPos, endPos):
        if self.isAlive and not self.landed:
            if self.position[0] >= startPos[0] - self.SIZE[self.type][0]/2 and self.position[0] <= endPos[0] + self.SIZE[self.type][0]/2:
                if self.position[1] >= startPos[1] - self.SIZE[self.type][1]/2 and self.position[1] <= endPos[1] + self.SIZE[self.type][1]/2:
                    return self
        return None
    
    def returnToMothership(self, player):
        mothership = self.flag.finalTarget
        arrived = True
        if self.position[0] < mothership.position[0] or self.position[0] > mothership.position[0]:
            if self.position[1] < mothership.position[1] or self.position[1] > mothership.position[1]:
                arrived = False
                self.move()
        if arrived:
            player.ressources[player.NUCLEAR] += self.nuclear
            self.nuclear = 0

    def land(self, game):
        playerId = self.owner
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
            alreadyLanded = False
            game.parent.view.isSettingOff()
            for i in planet.landingZones:
                if i.ownerId == playerId:
                    alreadyLanded = True
            if not alreadyLanded:
                if len(planet.landingZones) < 4:
                    for i in planet.landingZones:
                        game.players[i.ownerId].notifications.append(Notification(planet.position, Notification.LAND_PLANET, game.players[game.playerId].name))
                    player.currentPlanet = planet
                    self.planet = planet
                    landingZone = planet.addLandingZone(playerId, self, game.players[playerId])
                    self.nuclear += landingZone.nuclear
                    landingZone.nuclear = 0
                    landingZone.hitpoints = 100
                    player.buildings.append(landingZone)
                    player.selectedObjects = []
                    self.landed = True
                    self.planetId = planetId
                    self.sunId = sunId
                    self.planet = planet
                    player.planets.append(planet)
                    player.planetCurrent = player.planets.index(planet)
                    if playerId == game.playerId:
                        cam = game.players[playerId].camera
                        cam.placeOnLanding(landingZone)
                    x=40
                    for i in self.units:
                        position = [landingZone.position[0] + x, landingZone.position[1] + 5 * self.units.index(i)]
                        i.land(planet, position)
                        x+=25
                    del self.units[:]
                    if self in game.players[game.playerId].selectedObjects:
                        game.players[game.playerId].selectedObjects.pop(game.players[game.playerId].selectedObjects.index(self))
                    if playerId == game.playerId:
                        game.parent.changeBackground('PLANET')
                        game.parent.drawPlanetGround(planet)
            else:
                landingZone = None
                for i in planet.landingZones:
                    if i.ownerId == playerId:
                        landingZone = i
                if landingZone.LandedShip == None:
                    player.currentPlanet = planet
                    self.planet = planet
                    self.nuclear += landingZone.nuclear
                    landingZone.nuclear = 0
                    landingZone.hitpoints = 100
                    self.landed = True
                    self.planetId = planetId
                    self.sunId = sunId
                    self.planet = planet
                    if playerId == game.playerId:
                        cam = game.players[playerId].camera
                        cam.placeOnLanding(landingZone)
                    x=40
                    for i in self.units:
                        position = [landingZone.position[0] + x, landingZone.position[1] + 5 * self.units.index(i)]
                        i.land(planet, position)
                        x+=25
                    del self.units[:]
                    if self in game.players[game.playerId].selectedObjects:
                        game.players[game.playerId].selectedObjects.pop(game.players[game.playerId].selectedObjects.index(self))
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

    def kill(self):
        self.isAlive = False

    def load(self, unit):
        unit.flag = Flag(unit.position, unit.landingZone, FlagState.LOAD)

class GatherShip(SpaceUnit):
    GATHERTIME=20
    def __init__(self,  type, position, owner):
        SpaceUnit.__init__(self, type, position, owner)
        self.maxGather = 50
        self.gatherSpeed = 20
        self.container = [0,0]
        self.returning = False

    def action(self, parent):
        if self.flag.flagState == FlagState.GATHER:
            self.gather(parent, parent.game)
        else:
            Unit.action(self, parent)

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
                                self.flag.finalTarget = player.getNearestReturnRessourceCenter(self.position)
                                game.parent.redrawMinimap()
                            self.gatherSpeed = self.GATHERTIME
                        else:
                            self.flag.initialTarget = self.flag.finalTarget
                            self.flag.finalTarget = player.getNearestReturnRessourceCenter(self.position)
                    else:
                        if self.container[1]<self.maxGather:
                            if ressource.gazQte >= 5:
                                self.container[1]+=5
                                ressource.gazQte-=5
                            else:
                                self.container[1]+=ressource.gazQte
                                ressource.gazQte = 0
                                self.flag.initialTarget = self.flag.finalTarget
                                self.flag.finalTarget = player.getNearestReturnRessourceCenter(self.position)
                                game.parent.redrawMinimap()
                            self.gatherSpeed = self.GATHERTIME
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
                            player.notifications.append(Notification(self.position, Notification.FINISH_GATHER))
                            self.flag.flagState = FlagState.STANDBY
                    else:
                        if self.flag.finalTarget.gazQte == 0:
                            player.notifications.append(Notification(self.position, Notification.FINISH_GATHER))
                            self.flag.flagState = FlagState.STANDBY
                else:
                    self.flag.finalTarget = self.position
                    self.flag.flagState = FlagState.STANDBY

class NyanCat(SpaceUnit):
    def __init__(self,  type, position, owner):
        SpaceUnit.__init__(self,  type, position, owner)
        self.range=self.ATTACK_RANGE[type]
        self.AttackSpeed=self.ATTACK_SPEED[type]
        self.AttackDamage=self.ATTACK_DAMAGE[type]
        self.attackcount=self.AttackSpeed
        self.killCount = 0

    def action(self, parent):
        if self.flag.flagState == FlagState.ATTACK:
            if isinstance(self.flag.finalTarget, TransportShip):
                if self.flag.finalTarget.landed == True:
                    self.flag = Flag(self,self,FlagState.STANDBY)
            if self.flag.flagState == FlagState.ATTACK:
                killedIndex = self.attack(parent.game.players)
                if killedIndex[0] > -1:
                    parent.killUnit(killedIndex)
        elif self.flag.flagState == FlagState.PATROL:
            self.patrol()
        else:
            Unit.action(self, parent)

    def changeFlag(self, finalTarget, state):
        self.attackcount=self.AttackSpeed
        Unit.changeFlag(self, finalTarget, state)
        
    def attack(self, players, unitToAttack=None):
        if unitToAttack == None:
            unitToAttack = self.flag.finalTarget
        index = -1
        killedOwner = -1
        isBuilding = False
        distance = Helper.calcDistance(self.position[0], self.position[1], unitToAttack.position[0], unitToAttack.position[1])
        try:
            if distance > self.range :
                self.attackcount=self.AttackSpeed
                self.move()
            else:
                self.attackcount = self.attackcount - 1
                if self.attackcount == 0:
                    if unitToAttack.takeDammage(self.AttackDamage, players):
                        if isinstance(unitToAttack, b.Building) == False:
                            index = players[unitToAttack.owner].units.index(unitToAttack)
                        else:
                            index = players[unitToAttack.owner].buildings.index(unitToAttack)
                            isBuilding = True
                        killedOwner = unitToAttack.owner
                        self.killCount +=1
                        if self.killCount % 2 == 1:
                            self.AttackDamage += 1
                    self.attackcount=self.AttackSpeed
            return (index, killedOwner, isBuilding)
        except ValueError:
            self.flag = Flag(t.Target(self.position), t.Target(self.position), FlagState.STANDBY)
            return (-1, -1)

    def getKilledCount(self):
        return self.killCount
 
