import FlagState
class Flag():
    def __init__(self, initialTarget = None, finalTarget = None, flagState = FlagState.FlagState.STANDBY):
        self.initialTarget = initialTarget
        self.finalTarget = finalTarget
        self.flagState = flagState
        if isinstance(flag.finalTarget, t.PlayerObject):
            self.targetIsPlayerObject = True
        else:
            self.targetIsPlayerObject = False