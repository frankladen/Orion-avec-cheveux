import Target as t
from Constants import *
#Les differents etats qu'un flag peut prendre


#Represente un flag
class Flag():
    def __init__(self, initialTarget = None, finalTarget = None, flagState = FlagState.STANDBY):
        self.initialTarget = initialTarget
        self.finalTarget = finalTarget
        self.flagState = flagState
            
    def toString(self):
        return self.initialTarget.toString()
