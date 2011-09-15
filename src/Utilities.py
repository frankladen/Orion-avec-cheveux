from Constants import FlagState

class Flag():
    def __init__(self, flagState, initialPosition=None, finalPosition=None):
        self.flagState = flagState
        self.initialPosition = initialPosition
        self.finalPosition = finalPosition
        
class Point():
    def __init__(self, x=0, y=0, z=0):
        self.xPos = x
        self.yPos = y
        self.zPos = z
        
f = Flag(FlagState.MOVE)
print (f.flagState)
            
        
        