from Flag import *
from Constants import *
#Represente une position dans l'espace  
class Target():
    def __init__(self, position=[0,0,0]):
        self.position = position

#Represente un objet pouvant appartenir a un joueur
class PlayerObject(Target):
    def __init__(self, name, position, owner, hitpoints=50):
        super(PlayerObject, self).__init__(position)
        self.name = name
        self.flag = Flag(Target([0,0,0]), Target([0,0,0]), FlagState.STANDBY)
        self.owner = owner
        self.hitpoints=hitpoints
        self.isAlive = True;
        self.constructionProgress = 0
        if name == UnitType.SCOUT:
            self.viewRange = ViewRange.SCOUT
            self.buildTime = BuildTime.SCOUT
        elif name == UnitType.MOTHERSHIP:
            self.viewRange = ViewRange.MOTHERSHIP
        elif name == UnitType.SPACE_ATTACK_UNIT:
            self.viewRange = ViewRange.SPACE_ATTACK_UNIT
            self.buildTime = BuildTime.SPACE_ATTACK_UNIT
        else:
            self.viewRange = 100
    
    def getFlag(self):
        return self.flag
    
    def kill(self):
        self.isAlive = False        
