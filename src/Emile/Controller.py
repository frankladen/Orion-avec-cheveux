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
        for i in self.player.units:
            i.changeFlag(t.Target([rX,rY,0]),2)

    def mouvement(self):
        for i in self.player.units:
            if i.flag.flagState == 2:
                i.move()
        self.view.drawWorld()
        self.view.root.after(50, self.mouvement)
            
c = Controller()