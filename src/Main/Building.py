# -*- coding: UTF-8 -*-
import Target as t
import World as w
import Player as p
from Flag import *
from Helper import *
from Unit import  *

class Building(t.PlayerObject):
    WAYPOINT=0
    REFINERY=1
    BARRACK=2
    FARM=3
    TURRET=4
    MOTHERSHIP=5
    LANDING_ZONE=6
    NAME = ("Point ralliement", "Raffinerie", "Barraque", "Ferme", "Tourette", "Vaisseau mere", "Zone d'aterrissage")
    SIZE =((30,30),(0,0),(0,0),(75,59),(32,32),(125,125),(32,32))
    INSPACE = (True,False,False,False,True,True,False)
    COST = ((50,50),(0,0),(0,0),(50,50),(50,50),(0,0),(0,0))
    TIME = (60,0,0,75,75,0,0)
    MAX_HP = (150,0,0,200,200,1500,100)
    VIEW_RANGE=(200, 0, 0, 100, 250, 400, 200)
    MAX_SHIELD=0
    REGEN_WAIT_TIME = 30
    REGEN_WAIT_TIME_AFTER_ATTACK = 60
    
    def __init__(self,type, position, owner):
        t.PlayerObject.__init__(self, type, position, owner)
        self.buildingTimer = 0   
        self.viewRange = self.VIEW_RANGE[type]
        self.hitpoints = self.MAX_HP[type]
        self.maxHP=self.hitpoints
        self.buildTime = self.TIME[type]
        self.buildCost = self.COST[type]
        self.name = self.NAME[type]    
        self.finished = False
        self.shield = self.MAX_SHIELD
        self.shieldRegenCount = self.REGEN_WAIT_TIME
        self.shieldRegenAfterAttack = 0

    def action(self, parent):
        if self.finished:
            self.regenShield()

    def regenShield(self):
        if self.shield >= 0:
            if self.shieldRegenAfterAttack > 0:
                self.shieldRegenAfterAttack -= 1
            elif self.shieldRegenCount > 0:
                self.shieldRegenCount -= 1
            else:
                if self.shield > self.MAX_SHIELD-5:
                    self.shield = self.MAX_SHIELD
                else:
                    self.shield += 5
                    self.shieldRegenCount = self.REGEN_WAIT_TIME
                    
    def takeDammage(self, amount, players):
        self.shieldRegenCount = self.REGEN_WAIT_TIME
        self.shieldRegenAfterAttack = self.REGEN_WAIT_TIME_AFTER_ATTACK
        if self.shield > 0:
            if self.shield < amount:
                self.shield = 0
            else:
                self.shield -= amount
        else:
            if self.hitpoints <= amount:
                self.hitpoints = 0
                return True
            else:
                self.hitpoints -= amount
        return False

    def select(self, position):
        if self.isAlive:
            if self.position[0] >= position[0] - self.SIZE[self.type][0]/2 and self.position[0] <= position[0] + self.SIZE[self.type][0]/2:
                if self.position[1] >= position[1] - self.SIZE[self.type][1]/2 and self.position[1] <= position[1] + self.SIZE[self.type][1]/2:
                    return self
        return None

    def selectIcon(self, startPos, endPos):
        if self.isAlive:
            if self.position[0] > startPos[0] - self.SIZE[self.type][0]/2 and self.position[0] < endPos[0] + self.SIZE[self.type][0]/2:
                if self.position[1] > startPos[1] - self.SIZE[self.type][1]/2 and  self.position[1] < endPos[1] + self.SIZE[self.type][1]/2:
                    return self
        return None

class SpaceBuilding(Building):
    def __init__(self, type, position, owner):
        Building.__init__(self, type, position, owner)

class Waypoint(Building):
    def __init__(self, type, position, owner):
        SpaceBuilding.__init__(self, type, position, owner)
        
class Turret(Building):
    def __init__(self, type, position, owner):
        SpaceBuilding.__init__(self, type, position, owner)
        self.range=200
        self.AttackSpeed=12
        self.AttackDamage=6
        self.attackcount=self.AttackSpeed
        self.killCount = 0

    def action(self, parent):
        if self.finished:
            if self.flag.flagState == FlagState.ATTACK:
                killedIndexes = self.attack(parent.game.players)
                if killedIndexes[0] > -1:
                    parent.killUnit(killedIndexes)
            else:
                parent.game.checkIfEnemyInRange(self)

    def attack(self, players, unitToAttack=None):
        if unitToAttack == None:
            unitToAttack = self.flag.finalTarget
        index = -1
        killedOwner = -1
        isBuilding = False
        distance = Helper.calcDistance(self.position[0], self.position[1], unitToAttack.position[0], unitToAttack.position[1])
        try:
            if distance <= self.range:
                self.attackcount = self.attackcount - 1
                if self.attackcount == 0:
                    if unitToAttack.takeDammage(self.AttackDamage, players):
                        if isinstance(unitToAttack, Building) == False:
                            index = players[unitToAttack.owner].units.index(unitToAttack)
                        else:
                            index = players[unitToAttack.owner].buildings.index(unitToAttack)
                            isBuilding = True
                        killedOwner = unitToAttack.owner
                        for i in players[self.owner].units:
                            if i.isAlive:
                                if i.flag.finalTarget == unitToAttack:
                                    i.flag = Flag(t.Target(i.position), t.Target(i.position), FlagState.STANDBY)
                                    i.attackcount=i.AttackSpeed
                        self.killCount +=1
                    self.attackcount=self.AttackSpeed
            else:
                self.flag = Flag(t.Target(self.position), t.Target(self.position), FlagState.STANDBY)
            return (index, killedOwner, isBuilding)
        except ValueError:
            self.flag = Flag(t.Target(self.position), t.Target(self.position), FlagState.STANDBY)
            return (-1, -1, isBuilding)

    #Change le flag pour une nouvelle destination et un nouvel etat
    def changeFlag(self, finalTarget, state):
        #On doit vérifier si l'unité est encore vivante
        if self.isAlive:
            self.flag.initialTarget = t.Target([self.position[0],self.position[1],0])
            self.flag.finalTarget = finalTarget
            self.flag.flagState = state

class GroundBuilding(Building):
    def __init__(self, type, position, owner, sunId, planetId):
        Building.__init__(self, type, position, owner)
        self.sunId = sunId
        self.planetId = planetId

    def isInRange(self, position, range, onPlanet = False, planetId = -1, sunId = -1):
        if onPlanet and self.finished:
            if self.sunId == sunId and self.planetId == planetId:
                if self.position[0] > position[0]-range and self.position[0] < position[0]+range:
                    if self.position[1] > position[1]-range and self.position[1] < position[1]+range:
                        return self
        return None

class Farm(Building):
    def __init__(self, type, position, owner, sunId, planetId):
        GroundBuilding.__init__(self, type, position, owner, sunId, planetId)

class ConstructionBuilding(Building):
    def __init__(self, type, position, owner):
        Building.__init__(self, type, position, owner)
        self.unitBeingConstruct = []
        self.rallyPoint = [position[0],position[1]+(self.SIZE[type][1]/2)+5,0]
  
    def progressUnitsConstruction(self):
        if len(self.unitBeingConstruct) > 0:
            self.flag.flagState = FlagState.BUILD_UNIT
            self.unitBeingConstruct[0].constructionProgress = self.unitBeingConstruct[0].constructionProgress + 1
        else:
            self.flag.flagState = FlagState.STANDBY
               
    def addUnitToQueue(self, unitType):
        p = [self.position[0], self.position[1], 0]
        if unitType == u.Unit.SCOUT:
            self.unitBeingConstruct.append(u.Unit( u.Unit.SCOUT, p, self.owner))
        elif unitType == u.Unit.ATTACK_SHIP:
            self.unitBeingConstruct.append(u.SpaceAttackUnit( u.Unit.ATTACK_SHIP, p, self.owner))
        elif unitType == u.Unit.CARGO:
            self.unitBeingConstruct.append(u.GatherShip( u.Unit.CARGO, p, self.owner))
        elif unitType == u.Unit.TRANSPORT:
            self.unitBeingConstruct.append(u.TransportShip( u.Unit.TRANSPORT, p, self.owner))
        elif unitType == u.Unit.GROUND_GATHER:
            self.unitBeingConstruct.append(u.GroundGatherUnit( u.Unit.GROUND_GATHER, p, self.owner, self.planetId, self.sunId,True))
        elif unitType == u.Unit.GROUND_ATTACK:
            self.unitBeingConstruct.append(u.GroundAttackUnit( u.Unit.GROUND_ATTACK, p, self.owner, self.planetId, self.sunId,True))
        elif unitType == u.Unit.GROUND_BUILDER_UNIT:
            self.unitBeingConstruct.append(u.GroundBuilderUnit( u.Unit.GROUND_BUILDER_UNIT, p, self.owner, self.planetId, self.sunId,True))

    def getUnitBeingConstructAt(self, unitId):
        return self.unitBeingConstruct[unitId]
    
    def isUnitFinished(self):
        if len(self.unitBeingConstruct) > 0:
            return self.unitBeingConstruct[0].constructionProgress >= self.unitBeingConstruct[0].buildTime
        
    def action(self, parent):
        if self.finished:
            p = [self.position[0], self.position[1], 0]
            
            if self.flag.flagState == FlagState.CHANGE_RALLY_POINT:
                target = self.flag.finalTarget
                self.rallyPoint = [target[0], target[1], 0]
                self.flag.flagState = FlagState.BUILD_UNIT
                
            if self.flag.flagState != FlagState.ATTACK and self.flag.flagState != FlagState.BUILD_UNIT:
                self.flag.flagState = FlagState.STANDBY

            self.progressUnitsConstruction()
            
            if len(self.unitBeingConstruct) > 0:
                if(self.isUnitFinished()):
                    parent.buildUnit(self)
        
class Mothership(ConstructionBuilding):
    MAX_ARMOR = 2000
    MAX_SHIELD = 0
    ATTACK_RANGE = 250
    ATTACK_SPEED = 25
    ATTACK_DAMAGE = 15     
    
    def __init__(self,  type, position, owner):
        ConstructionBuilding.__init__(self, type, position, owner)
        self.flag.finalTarget = t.Target(position)        
        self.owner = owner
        self.range=self.ATTACK_RANGE
        self.AttackSpeed=self.ATTACK_SPEED
        self.AttackDamage=self.ATTACK_DAMAGE
        self.attackcount=self.AttackSpeed
        self.armor = self.MAX_ARMOR
        self.killCount = 0
        self.finished = True

    def action(self, parent):
        parent.game.checkIfEnemyInRange(self)
        if self.flag.flagState == FlagState.ATTACK:
            if isinstance(self.flag.finalTarget, u.TransportShip):
                if self.flag.finalTarget.landed:
                    parent.game.setAStandByFlag(self)
            killedIndex = self.attack(parent.game.players)
            if killedIndex[0] > -1:
                parent.killUnit(killedIndex)
        ConstructionBuilding.action(self, parent)

    #Applique les bonus du Unit selon les upgrades
    def applyBonuses(self, bonuses):
        self.viewRange = self.VIEW_RANGE[self.type]+bonuses[p.Player.VIEW_RANGE_BONUS]
        self.AttackSpeed = self.ATTACK_SPEED[self.type]+bonuses[p.Player.ATTACK_SPEED_BONUS]
        self.AttackDamage = self.ATTACK_DAMAGE[self.type]+bonuses[p.Player.ATTACK_DAMAGE_BONUS]
        self.range = self.ATTACK_RANGE[self.type]+bonuses[p.Player.ATTACK_RANGE_BONUS]

    def regenShield(self):
        if self.shield >= 0:
            if self.shieldRegenAfterAttack > 0:
                self.shieldRegenAfterAttack -= 1
            elif self.shieldRegenCount > 0:
                self.shieldRegenCount -= 1
            else:
                if self.shield > self.MAX_SHIELD-5:
                    self.shield = self.MAX_SHIELD
                else:
                    self.shield += 5
                    self.shieldRegenCount = self.REGEN_WAIT_TIME

    def takeDammage(self, amount, players):
        self.shieldRegenCount = self.REGEN_WAIT_TIME
        self.shieldRegenAfterAttack = self.REGEN_WAIT_TIME_AFTER_ATTACK
        if self.shield > 0:
            if self.shield < amount:
                self.shield = 0
            else:
                self.shield -= amount
        elif self.armor > 0:
            if self.armor < amount:
                self.armor = 0
            else:
                self.armor -= amount
        else:
            if self.hitpoints <= amount:
                self.hitpoints = 0
                return True
            else:
                self.hitpoints -= amount
        return False

    def attack(self, players, unitToAttack=None):
        if unitToAttack == None:
            unitToAttack = self.flag.finalTarget
        if not isinstance(unitToAttack, u.GroundUnit):
            index = -1
            killedOwner = -1
            isBuilding = False
            distance = Helper.calcDistance(self.position[0], self.position[1], unitToAttack.position[0], unitToAttack.position[1])
            try:
                if distance > self.range :
                    self.attackcount=self.AttackSpeed
                else:
                    self.attackcount = self.attackcount - 1
                    if self.attackcount == 0:
                        if unitToAttack.takeDammage(self.AttackDamage, players):
                            if isinstance(unitToAttack, Building) == False:
                                index = players[unitToAttack.owner].units.index(unitToAttack)
                            else:
                                index = players[unitToAttack.owner].buildings.index(unitToAttack)
                                isBuilding = True
                            killedOwner = unitToAttack.owner
                            self.killCount +=1
                        self.attackcount=self.AttackSpeed
                return (index, killedOwner, isBuilding)
            except ValueError:
                self.flag = Flag(t.Target(self.position), t.Target(self.position), FlagState.BUILD_UNIT)
                return (-1, -1)
            
            
class LandingZone(ConstructionBuilding,GroundBuilding):
    WIDTH = 75
    HEIGHT = 75
    def __init__(self, position, ownerId, landingShip, id, planetId, sunId):
        ConstructionBuilding.__init__(self, self.LANDING_ZONE, position, ownerId)
        self.ownerId = ownerId
        self.LandedShip = landingShip
        self.id = id
        self.planetId = planetId
        self.sunId = sunId
        self.finished = True
        self.planet = None

    def over(self, positionStart, positionEnd):
        if positionEnd[0] > self.position[0] - self.WIDTH/2 and positionStart[0] < self.position[0] + self.WIDTH/2:
            if positionEnd[1] > self.position[1] - self.HEIGHT/2 and positionStart[1] < self.position[1] + self.HEIGHT/2:
                return True
        return False

    def select(self, position):
        if position[0] > self.position[0]-self.WIDTH/2 and position[0] < self.position[0]+self.WIDTH/2:
            if position[1] > self.position[1]-self.HEIGHT/2 and position[1] < self.position[1]+self.HEIGHT/2:
                return self
        return None

    def isInRange(self, position, range, onPlanet = False, planetId = -1, sunId = -1):
        if onPlanet:
            if self.sunId == sunId and self.planetId == planetId:
                if self.position[0] > position[0]-range and self.position[0] < position[0]+range:
                    if self.position[1] > position[1]-range and self.position[1] < position[1]+range:
                        return self
        return None

    def takeDammage(self, amount, players):
        if self.LandedShip != None:
            if self.LandedShip.takeDammage(amount, players):
               killedOwner = self.ownerId
               index = players[self.ownerId].units.index(self.LandedShip)
               self.LandedShip = None
               players[self.ownerId].killUnit((index, killedOwner, False))
        else:
            self.hitpoints -= amount
            if self.hitpoints <= 0:
                return True
        return False       
                                                                                                                                            
