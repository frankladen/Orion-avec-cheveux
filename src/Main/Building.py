# -*- coding: UTF-8 -*-
import Target as t
import World as w
import Player as p
from Flag import *
from Helper import *
from Unit import  *

class Building(t.PlayerObject):
    WAYPOINT=0
    UTILITY=1
    BARRACK=2
    FARM=3
    TURRET=4
    MOTHERSHIP=5
    LANDING_ZONE=6
    LAB=7
    NAME = ("Point ralliement", "Utilités", "Barraque", "Ferme", "Tourette", "Vaisseau mere", "Zone d'aterrissage","Laboratoire de recherche")
    SIZE =((30,30),(75,70),(75,80),(75,59),(32,32),(125,125),(32,32),(94,94))
    INSPACE = (True,True,True,False,True,True,False,False)
    COST = ((50,50),(250,250),(300,300),(75,75),(250,200),(2000,2000),(0,0),(300,300))
    TIME = (125,250,250,125,125,1250,0,250)
    MAX_HP = (150,250,250,200,200,1500,100,200)
    VIEW_RANGE=(200, 200, 200, 100, 250, 400, 200,100)
    SCORE_VALUE=(15,10,10,10,20,50,15,30)
    MAX_SHIELD=0
    REGEN_WAIT_TIME = 30
    REGEN_WAIT_TIME_AFTER_ATTACK = 60
    
    def __init__(self,type, position, owner):
        t.PlayerObject.__init__(self, type, position, owner)
        self.buildingTimer = 0   
        self.viewRange = self.VIEW_RANGE[type]
        self.hitpoints = 0
        self.maxHP=self.MAX_HP[type]
        self.buildTime = self.TIME[type]
        self.buildCost = self.COST[type]
        self.name = self.NAME[type]    
        self.finished = False
        self.shield = 0
        self.shieldRegenCount = self.REGEN_WAIT_TIME
        self.shieldRegenAfterAttack = 0

    def action(self, parent):
        if self.finished:
            self.regenShield()

    def regenShield(self):
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

    def applyBonuses(self, bonuses):
        if self.finished:
            self.shield = bonuses[p.Player.BUILDING_SHIELD_BONUS]
            self.MAX_SHIELD = bonuses[p.Player.BUILDING_SHIELD_BONUS]

class SpaceBuilding(Building):
    def __init__(self, type, position, owner):
        Building.__init__(self, type, position, owner)

class Waypoint(SpaceBuilding):
    def __init__(self, type, position, owner):
        SpaceBuilding.__init__(self, type, position, owner)
        
class Turret(SpaceBuilding):
    ATTACK_SPEED = 12
    ATTACK_DAMAGE = 6
    ATTACK_RANGE = 175
    
    def __init__(self, type, position, owner):
        SpaceBuilding.__init__(self, type, position, owner)
        self.range=self.ATTACK_RANGE
        self.AttackSpeed=self.ATTACK_SPEED
        self.AttackDamage=self.ATTACK_DAMAGE
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

    def getKilledCount(self):
        return self.killCount

    #Change le flag pour une nouvelle destination et un nouvel etat
    def changeFlag(self, finalTarget, state):
        #On doit vérifier si l'unité est encore vivante
        if self.isAlive:
            self.flag.initialTarget = t.Target([self.position[0],self.position[1],0])
            self.flag.finalTarget = finalTarget
            self.flag.flagState = state

    def applyBonuses(self, bonuses):
        if self.finished:
            self.AttackSpeed = self.ATTACK_SPEED+bonuses[p.Player.ATTACK_SPEED_BONUS]
            self.AttackDamage = self.ATTACK_DAMAGE+bonuses[p.Player.ATTACK_DAMAGE_BUILDING_BONUS]
            self.range = self.ATTACK_RANGE+bonuses[p.Player.ATTACK_RANGE_BONUS]
            Building.applyBonuses(self, bonuses)

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

class Lab(GroundBuilding):
    def __init__(self, type, position, owner, sunId, planetId):
        GroundBuilding.__init__(self, type, position, owner, sunId, planetId)
        self.techsToResearch = []

    def action(self, parent):
        if self.finished:
            if len(self.techsToResearch) > 0:
                self.progressTechs(parent)

    def progressTechs(self, player):
        self.techsToResearch[0][0].researchTime += 1
        if self.techsToResearch[0][0].researchTime >= self.techsToResearch[0][0].timeNeeded:
            player.BONUS[self.techsToResearch[0][1]] = self.techsToResearch[0][0].add
            self.techsToResearch[0][0].isAvailable = False
            if self.techsToResearch[0][0].child != None:
                self.techsToResearch[0][0].child.isAvailable = True
            player.notifications.append(t.Notification([-10000,-10000,-10000],t.Notification.FINISH_TECH,self.techsToResearch[0][0].name))
            self.techsToResearch.pop(0)
            player.changeBonuses()
        
class Farm(GroundBuilding):
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
               
    def addUnitToQueue(self, unitType, galaxy=None, forcebuild=False):
        p = [self.position[0], self.position[1], 0]
        if unitType == u.Unit.SCOUT:
            un = u.Unit( u.Unit.SCOUT, p, self.owner)
        elif unitType == u.Unit.ATTACK_SHIP:
            un = u.SpaceAttackUnit( u.Unit.ATTACK_SHIP, p, self.owner)
        elif unitType == u.Unit.CARGO:
            un = u.GatherShip( u.Unit.CARGO, p, self.owner)
        elif unitType == u.Unit.TRANSPORT:
            un = u.TransportShip( u.Unit.TRANSPORT, p, self.owner)
        elif unitType == u.Unit.HEALING_UNIT:
            un = u.HealingUnit(u.Unit.HEALING_UNIT, p, self.owner)
        elif unitType == u.Unit.GROUND_GATHER:
            un = u.GroundGatherUnit( u.Unit.GROUND_GATHER, p, self.owner, self.planetId, self.sunId,True)
            un.planet = galaxy.solarSystemList[self.sunId].planets[self.planetId]
        elif unitType == u.Unit.GROUND_ATTACK:
            un = u.GroundAttackUnit( u.Unit.GROUND_ATTACK, p, self.owner, self.planetId, self.sunId,True)
            un.planet = galaxy.solarSystemList[self.sunId].planets[self.planetId]
        elif unitType == u.Unit.GROUND_BUILDER_UNIT:
            un = u.GroundBuilderUnit( u.Unit.GROUND_BUILDER_UNIT, p, self.owner, self.planetId, self.sunId,True)
            un.planet = galaxy.solarSystemList[self.sunId].planets[self.planetId]
        elif unitType == u.Unit.SPECIAL_GATHER:
            un = u.SpecialGather( u.Unit.SPECIAL_GATHER, p, self.owner, self.planetId, self.sunId,True)
            un.planet = galaxy.solarSystemList[self.sunId].planets[self.planetId]
        elif unitType == u.Unit.SPACE_BUILDING_ATTACK:
            un = u.SpaceBuildingAttack( u.Unit.SPACE_BUILDING_ATTACK, p, self.owner)
        if forcebuild:
            un.buildTime = 1
            if unitType in (u.Unit.SPECIAL_GATHER, u.Unit.GROUND_GATHER, u.Unit.CARGO):
                un.GATHERTIME = 0
        self.unitBeingConstruct.append(un)
        
                                           
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
    ATTACK_RANGE = 185
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
        self.armor = 0
        self.killCount = 0

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
        if self.finished:
            self.AttackDamage = self.ATTACK_DAMAGE+bonuses[p.Player.ATTACK_DAMAGE_MOTHERSHIP]
            self.shield = bonuses[p.Player.BUILDING_MOTHERSHIELD_BONUS]
            self.MAX_SHIELD = bonuses[p.Player.BUILDING_MOTHERSHIELD_BONUS]

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

class Barrack(ConstructionBuilding):
    def __init__(self,  type, position, owner):
        ConstructionBuilding.__init__(self, type, position, owner)
        self.flag.finalTarget = t.Target(position)        
        self.owner = owner

class Utility(ConstructionBuilding):
    def __init__(self,  type, position, owner):
        ConstructionBuilding.__init__(self, type, position, owner)
        self.flag.finalTarget = t.Target(position)        
        self.owner = owner
   
class LandingZone(ConstructionBuilding):
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
        self.planet = landingShip.planet
        self.nuclear = 0

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
                                                                                                                                            
