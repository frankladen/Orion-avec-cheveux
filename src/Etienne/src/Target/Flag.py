from Utilities.FlagState import FlagState
class Flag():
    def __init__(self, initialTarget = None, finalTarget = None, flagState = FlagState.STANDBY):
        self.initialTarget = initialTarget
        self.finalTarget = finalTarget
        self.flagState = flagState