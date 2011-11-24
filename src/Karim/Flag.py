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
    CHANGE_FORMATION = 8192
    TRADE = 16384
    DESTROY_ALL = 32768
    DEMAND_ALLIANCE = 65536
    GROUND_MOVE = 131072
    GROUND_GATHER = 262144
    FINISH_BUILD = 524288
    BUY_TECH = 1048576
    GROUND_ATTACK = 2097152
    LOAD = 4194304
    UNLOAD = 11

#Represente un flag
class Flag():
    def __init__(self, initialTarget = None, finalTarget = None, flagState = FlagState.STANDBY):
        self.initialTarget = initialTarget
        self.finalTarget = finalTarget
        self.flagState = flagState
            
    def toString(self):
        return self.initialTarget.toString()
