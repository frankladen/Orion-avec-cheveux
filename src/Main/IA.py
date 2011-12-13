# -*- coding: UTF-8 -*-
from Unit import *
from Flag import *
from Client import *
from Player import *
import random
import socket
import time

class IA(Player):
    def __init__(self, name, game, id , colorId):
        Player.__init__(self, name, game, id , colorId)       
        self.frameAction = 60
        self.frameActuel = 0        
        
    def requeteModele(self): #methode que controleur va appeler
        if self.frameActuel == self.frameAction:
            self.choixAction()
            self.frameActuel = 0
        else:
             self.frameActuel = self.frameActuel+1
        
    def action(self):
        Player.action(self)
        # si on est rendu pour faire une nouvelle action
        if self.frameActuel == self.frameAction:
            self.choixAction()
            self.frameActuel = 0
        else:
             self.frameActuel = self.frameActuel+1
             
    def trouverRessource(self):
        for i in self.game.galaxy.solarSystemList:
            for j in i.nebulas:
                if(self.game.players[self.id].inViewRange(j.position)):
                    return j
            for j in i.asteroids:
                if(self.game.players[self.id].inViewRange(j.position)):
                    return j
        return None
                    
    def envoyerCargo(self,ressource):
        for i in self.units:
            if i.type == Unit.CARGO:
                if i.flag.flagState == FlagState.STANDBY:
                    i.changeFlag(ressource,FlagState.GATHER)
                    
    def explore(self):
        for i in self.units:
            if i.type == Unit.SCOUT:
                x = random.randint(1,800) - 400
                y = random.randint(1,800) - 400
                while (i.position[0]+x < (self.game.galaxy.width/2)*-1 or i.position[0]+x > self.game.galaxy.width/2):
                    x = random.randint(1,800) - 400
                while (i.position[1]+y < (self.game.galaxy.height/2)*-1 or i.position[1]+y > self.game.galaxy.height/2):
                    y = random.randint(1,800) - 400
                i.changeFlag(Target([i.position[0]+x,i.position[1]+y,0]), FlagState.MOVE)
                 
    def choixAction(self):
        r = random.randint(1,2)
    
        if r == 1:
            self.explore()
        elif r == 2:
            ressource = self.trouverRessource()
            if ressource != None:
               self.envoyerCargo(ressource)
        elif r == 3:
            print("buildddd")
        else:
            print("attaqueeeee")
            

# Joueur IA 1 (stupid)       
class IA1(IA): # hérite de la classe IA
    def __init__(self):
        IA.__init__(self, name, game, id , colorId)
 
 # Joueur IA 2 (smart) 
class IA1(IA): # hérite de la classe IA
    def __init__(self):
        IA.__init__(self, name, game, id , colorId)       
            