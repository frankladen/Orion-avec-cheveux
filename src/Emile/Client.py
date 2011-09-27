import View as v
import World as w
import Player as p
import Target as t
class Controller():
    def __init__(self):
        self.players = [] #La liste des joueurs
        self.playerId = 0 #Le id du joueur courant
        self.galaxy=w.Galaxy(4)
        self.players.append(p.Player('Emile'))
        self.players[self.playerId].startGame([0,0],self.galaxy)
        self.view = v.View(self, 'Orion')
        self.mouvement()
        self.view.root.mainloop()
        
    def setMovingFlag(self,x,y):
        pos = self.players[self.playerId].camera.calcPointInWorld(x,y)
        for i in self.players[self.playerId].units:
            i.changeFlag(t.Target(pos),2)

    def mouvement(self):
        for i in self.players[self.playerId].units:
            if i.flag.flagState == 2:
                i.move()
        self.view.drawWorld()
        self.view.root.after(50, self.mouvement)
            
c = Controller()