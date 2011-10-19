from Flag import *

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
    
    def getFlag(self):
        return self.flag
    
    def kill(self):
        self.isAlive = False        