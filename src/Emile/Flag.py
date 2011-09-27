import FlagState
class Flag():
    def __init__(self, initialTarget = None, finalTarget = None, flagState = FlagState.FlagState.STANDBY):
        self.initialTarget = initialTarget
        self.finalTarget = finalTarget
        self.flagState = flagState