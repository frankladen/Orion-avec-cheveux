import FlagState
import Target as t

class Flag():
    def __init__(self, initialTarget = None, finalTarget = None, flagState = FlagState.FlagState.STANDBY):
        self.initialTarget = initialTarget
        self.finalTarget = finalTarget
        self.flagState = flagState
            
            
    def toString(self):
        return self.initialTarget.toString()