import View as v
import World as w
import Player as p
import Target as t
class Controller():
    def __init__(self):
        self.players = [] #La liste des joueurs
        self.playerId = 0 #Le id du joueur courant
        self.galaxy=w.Galaxy(2)
        self.players.append(p.Player('Emile'))
        self.players[self.playerId].startGame([0,0],self.galaxy)
        self.view = v.View(self, 'Orion')
        self.multiSelect = False
        self.action()
        self.view.root.mainloop()
        
    def setMovingFlag(self,x,y):
        pos = self.players[self.playerId].camera.calcPointInWorld(x,y)
        for i in self.players[self.playerId].selectedObjects:
            if i.__module__ == 'Unit':
                i.changeFlag(t.Target(pos),2)
            
    def select(self, x, y, canva):
        posSelected = self.players[self.playerId].camera.calcPointInWorld(x,y)
        for i in self.galaxy.solarSystemList:
            for j in i.planets:
                if j.position[0] >= posSelected[0]-10 and j.position[0] <= posSelected[0]+10:
                    if j.position[1] >= posSelected[1]-10 and j.position[1] <= posSelected[1]+10:
                        if j not in self.players[self.playerId].selectedObjects:
                            self.players[self.playerId].selectedObjects = []
                            self.players[self.playerId].selectedObjects.append(j)
                            
        for j in self.players[self.playerId].units:
            if j.position[0] >= posSelected[0]-8 and j.position[0] <= posSelected[0]+8:
                if j.position[1] >= posSelected[1]-8 and j.position[1] <= posSelected[1]+8: 
                    if self.multiSelect == False:
                        self.players[self.playerId].selectedObjects = []
                    if j not in self.players[self.playerId].selectedObjects:
                        self.players[self.playerId].selectedObjects.append(j)
        print('selected:',self.players[self.playerId].selectedObjects)
    
    def quickMove(self, x,y, canva):
        posSelected = self.players[self.playerId].camera.calcPointOnMap(x,y)
        self.players[self.playerId].camera.position = posSelected
        print("deplacement rapide de la camera")
    
    def action(self):
        self.multiSelect = False
        for i in self.players[self.playerId].units:
            if i.flag.flagState == 2:
                i.move()
        self.view.drawWorld()
        self.view.root.after(50, self.action)        
c = Controller()