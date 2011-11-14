import Target as t

#Les differents etats qu'un flag peut prendre
class FlagState():
    STANDBY=1
    MOVE=2
    PATROL=4
    ATTACK=8
    GATHER=16
    BUILD=32
    LAND=64
    RESEARCH=128
    DESTROY=256
    CREATE = 512
    CHANGE_RALLY_POINT = 1024
    CANCEL_UNIT = 2048
    BUILD_UNIT = 4096
    FINISH_BUILD = 8192

#Represente un flag
class Flag():
    def __init__(self, initialTarget = None, finalTarget = None, flagState = FlagState.STANDBY):
        self.initialTarget = initialTarget
        self.finalTarget = finalTarget
        self.flagState = flagState
            
    def toString(self):
        return self.initialTarget.toString()
