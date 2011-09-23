from Flag import *
import FlagState as fs
class Target():
    def __init__(self, position=[0,0,0]):
        self.position = position

class PlayerObject(Target):
    def __init__(self, name, position):
        super(PlayerObject, self).__init__(position)
        self.name = name
        self.flag = Flag(Target([0,0,0]),Target([0,0,0]),fs.FlagState.STANDBY)
        