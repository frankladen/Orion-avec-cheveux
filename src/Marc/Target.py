from Flag import *
from Constants import *

#Represente une position dans l'espace  
class Target():
    def __init__(self, position=[0,0,0]):
        self.position = position

#Represente un objet pouvant appartenir a un joueur
class PlayerObject(Target):
    def __init__(self, name, position, owner):
        super(PlayerObject, self).__init__(position)
        self.name = name
        self.flag = Flag(Target([0,0,0]), Target([0,0,0]), FlagState.STANDBY)
        self.owner = owner
        self.hitpoints = 50
        self.maxHP = 50
        self.isAlive = True
        self.constructionProgress = 0
        if name == UnitType.SCOUT:
            self.viewRange = ViewRange.SCOUT
            self.buildTime = BuildTime.SCOUT
        elif name == UnitType.MOTHERSHIP:
            self.viewRange = ViewRange.MOTHERSHIP
            self.hitpoints = 500
            self.maxHP=self.hitpoints
        elif name == UnitType.SPACE_ATTACK_UNIT:
            self.hitpoints = 100
            self.maxHP=self.hitpoints
            self.viewRange = ViewRange.SPACE_ATTACK_UNIT
            self.buildTime = BuildTime.SPACE_ATTACK_UNIT
        else:
            self.viewRange = 100
    
    def getFlag(self):
        return self.flag
    
    def kill(self):
        self.isAlive = False        
