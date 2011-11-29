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
        self.frameAction = 10
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
        
                 
    def choixAction(self):
        r = random.randint(1,5)
        
        # choix d'actions
        if r == 1:
            print("moveeee")
        elif r == 2:
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
            