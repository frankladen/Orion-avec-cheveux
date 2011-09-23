class Target():
    def __init__(self, position=[0,0,0]):
        self.position = position

class PlayerObject(Target):
    def __init__(self, name, flag, position):
        super(PlayerObject, self).__init__(position)
        self.name = name
        self.flag = flag
        