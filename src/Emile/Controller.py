import View as v
import World as w
import Player as p
import Target as t
class Controller():
    def __init__(self):
        self.galaxy=w.Galaxy(2)
        self.player = p.Player('Emile', self.galaxy)
        self.view = v.View(self, 'Orion')
        self.mouvement()
        self.view.root.mainloop()
        
    def setMovingFlag(self,x,y):
        dist = self.player.camera.calcDistance([x,y])
        rX = self.player.camera.position[0]-self.player.camera.screenCenter[0]+x
        rY = self.player.camera.position[1]-self.player.camera.screenCenter[1]+y
        self.player.units[0].changeFlag(t.Target([rX,rY,0]),2)
    
    def allo(self):
        print('allo')
    
    def mouvement(self):
        if self.player.units[0].flag.flagState == 2:
            self.player.units[0].move()
            self.view.drawWorld()
        self.view.root.after(50, self.mouvement)
            
c = Controller()