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
    MOTHERSHIP = 5
    SIZE =((30,30),(0,0),(0,0),(75,59),(32,32),(125,125))
    INSPACE = (True,False,False,False,True,True)
    COST = ((50,50),(0,0),(0,0),(50,50),(50,50),(0,0))
    TIME = (60,0,0,75,75,0)
    MAX_HP = (150,0,0,200,200,1500)
    VIEW_RANGE=(200, 0, 0, 100, 250, 400)
    

    
    def __init__(self, name,type, position, owner):
        t.PlayerObject.__init__(self, type, position, owner)
        self.buildingTimer = 0   
        self.viewRange = self.VIEW_RANGE[type]
        self.hitpoints = self.MAX_HP[type]
        self.maxHP=self.hitpoints
        self.buildTime = self.TIME[type]
        self.buildCost = self.COST[type]
        self.name = u.Unit.NAME[type]
        
        self.finished = False
        self.name = name

    def select(self, position):
        if self.isAlive:
            if self.position[0] >= position[0] - self.SIZE[self.type][0]/2 and self.position[0] <= position[0] + self.SIZE[self.type][0]/2:
                if self.position[1] >= position[1] - self.SIZE[self.type][1]/2 and self.position[1] <= position[1] + self.SIZE[self.type][1]/2:
                    return self
        return None

class SpaceBuilding(Building):
    def __init__(self, name, type, position, owner):
        Building.__init__(self, name, type, position, owner)

class Waypoint(Building):
    def __init__(self, name,type, position, owner):
        SpaceBuilding.__init__(self,name,  type, position, owner)
        
class Turret(Building):
    def __init__(self, name, type, position, owner):
        SpaceBuilding.__init__(self, name, type, position, owner)
        self.range=200
        self.AttackSpeed=12
        self.AttackDamage=6
        self.attackcount=self.AttackSpeed
        self.killCount = 0

    def attack(self, players, unitToAttack):
        index = -1
        killedOwner = -1
        isBuilding = False
        distance = Helper.calcDistance(self.position[0], self.position[1], unitToAttack.position[0], unitToAttack.position[1])
        try:
            if distance <= self.range:
                self.attackcount = self.attackcount - 1
                if self.attackcount == 0:
                    unitToAttack.hitpoints-=self.AttackDamage
                    if unitToAttack.hitpoints <= 0:
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
            return (index, killedOwner, isBuilding)
        except ValueError:
            self.flag = Flag(t.Target(self.position), t.Target(self.position), FlagState.STANDBY)
            return (-1, -1, isBuilding)

class GroundBuilding(Building):
    def __init__(self, name, type, position, owner, sunId, planetId):
        Building.__init__(self, name, type, position, owner)
        self.sunId = sunId
        self.planetId = planetId

class Farm(Building):
    def __init__(self, name, type, position, owner, sunId, planetId):
        GroundBuilding.__init__(self, name, type, position, owner, sunId, planetId)


class ConstructionBuilding(Building):
    def __init__(self, type, position, owner):
        Building.__init__(self, 'Vaisseau mère', type, position, owner)
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
    
    
    def isUnitFinished(self):
        if len(self.unitBeingConstruct) > 0:
            return self.unitBeingConstruct[0].constructionProgress >= self.unitBeingConstruct[0].buildTime
        
    def action(self, parent):

        if self.isAlive:
            p = [self.position[0], self.position[1], 0]
            if self.flag.flagState == FlagState.BUILD_UNIT:
                self.progressUnitsConstruction()

            elif self.flag.flagState == FlagState.CANCEL_UNIT:
                self.unitBeingConstruct.pop(self.flag.finalTarget)
                self.flag.flagState = FlagState.BUILD_UNIT

            elif self.flag.flagState == FlagState.CHANGE_RALLY_POINT:
                target = self.flag.finalTarget
                self.rallyPoint = [target[0], target[1], 0]
                self.flag.flagState = FlagState.BUILD_UNIT


                    
            elif self.flag.flagState == FlagState.ATTACK:
                if isinstance(self.flag.finalTarget, TransportShip):
                    if self.flag.finalTarget.landed:
                        parent.game.setAStandByFlag(self)
                killedIndex = self.attack(parent.game.players)
                if killedIndex[0] > -1:
                    parent.killUnit(killedIndex)
                    
            if self.flag.flagState != FlagState.ATTACK and self.flag.flagState != FlagState.BUILD_UNIT:
                self.flag.flagState = FlagState.STANDBY
            
            if len(self.unitBeingConstruct) > 0:
                if(self.isUnitFinished()):
                    parent.buildUnit()
            
            if isinstance(self, Mothership):
                self.regenShield()
            
        else:
            self.unitBeingConstruct = []
            self.isAlive = False
        
        
        
class Mothership(ConstructionBuilding):
    REGEN_WAIT_TIME = 30
    REGEN_WAIT_TIME_AFTER_ATTACK = 60
    MAX_SHIELD = 1500
    MAX_ARMOR = 2000
    ATTACK_RANGE = 250
    ATTACK_SPEED = 8
    ATTACK_DAMAGE = 5
    
     
    
    def __init__(self,  type, position, owner):
        ConstructionBuilding.__init__(self, type, position, owner)
        self.flag.finalTarget = t.Target(position)        
        self.owner = owner
        self.range=self.ATTACK_RANGE
        self.AttackSpeed=self.ATTACK_SPEED
        self.AttackDamage=self.ATTACK_DAMAGE
        self.attackcount=self.AttackSpeed
        self.shield = self.MAX_SHIELD
        self.shieldRegenCount = self.REGEN_WAIT_TIME
        self.shieldRegenAfterAttack = 0
        self.armor = self.MAX_ARMOR
        self.killCount = 0

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

    #Applique les bonus du Unit selon les upgrades
    def applyBonuses(self, bonuses):
        self.viewRange = self.VIEW_RANGE[self.type]+bonuses[p.Player.VIEW_RANGE_BONUS]
        self.AttackSpeed = self.ATTACK_SPEED[self.type]+bonuses[p.Player.ATTACK_SPEED_BONUS]
        self.AttackDamage = self.ATTACK_DAMAGE[self.type]+bonuses[p.Player.ATTACK_DAMAGE_BONUS]
        self.range = self.ATTACK_RANGE[self.type]+bonuses[p.Player.ATTACK_RANGE_BONUS]

    def takeDammage(self, amount):
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
        if not isinstance(unitToAttack, GroundUnit):
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
                        if unitToAttack.takeDammage(self.AttackDamage):
                            if isinstance(unitToAttack, b.Building) == False:
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
            
            
class LandingZone(ConstructionBuilding):
    WIDTH = 75
    HEIGHT = 75
    def __init__(self, position, ownerId, landingShip, id, planetId, sunId):
        PlayerObject.__init__(self, 0, position, ownerId)
        self.ownerId = ownerId
        self.LandedShip = landingShip
        self.id = id
        self.planetId = planetId
        self.sunId = sunId
        

    def select(self, position):
        if position[0] > self.position[0]-self.WIDTH/2 and position[0] < self.position[0]+self.WIDTH/2:
            if position[1] > self.position[1]-self.HEIGHT/2 and position[1] < self.position[1]+self.HEIGHT/2:
                return self
        return None


       
        
