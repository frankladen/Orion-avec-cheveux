import View as v
import World as w

class Controller():
    def __init__(self):
        self.galaxy=w.Galaxy(2)
        self.cam = w.Camera([400,400])
        self.view = v.View(self, 'Orion')
        
c = Controller()