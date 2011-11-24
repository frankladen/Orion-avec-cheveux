# -*- coding: UTF-8 -*-
from Unit import *
from Flag import *
from Client import *
from Player import *
from Game import *
from Building import *
import random
import socket
import time

class IA(Player):
    MAXUNIT =(0,0,3,10)
    def __init__(self, name, id , colorId, parent):
        Player.__init__(name, id , colorId, parent)
        self.frameAction = 10
        self.frameActuel = 0
        #self.units = [] #Liste de toute les unites
        #self.tempsCourant = time.
        # regarder le timer d'action du joueur dans Client
        
        
    #def requeteModele(self): #methode que controleur va appeler
        
    def action(self):
        
        for i in self.units:
            if i.isAlive:
                i.action(self) 
        #il le fait tout le temps pour faire une nouvelle action
        if self.frameActuel == self.frameAction:
            self.choixAction()
            self.frameActuel = 0
        else:
            self.frameActuel = self.frameActuel+1
                 
    def choixAction(self):
        r = random.randint(1,5)
        
        # choix d'actions
        if r == 1:
            print 'explorer'
        elif r == 2:
            print 'build'
        elif r == 3:
            print 'deplacer'
        else:
            print 'attaque'


# Joueur IA 1 (stupid)       
#class IA1(IA): # hérite de la classe IA
#   def __init__(self):
#       IA.__init__(self, name, id, colorId, parent)
 
# Joueur IA 2 (smart) 
#class IA1(IA): # hérite de la classe IA
#    def __init__(self):
#        IA.__init__(self, name, id, colorId, parent)       

#Méthode explorer()
    def explorer(self,x,y):
        Game.setMovingFlag(x, y)
        
#Méthode build()
    def buildUnit(self,unitType):
        #on va vérifier si il a un nombre suffaisant de units sinon il en construit
        #build unité
        if unitType == 0:
            for i in self.units:
                if self.units[i] == unitType:
                    if self.nbrUnit(self.units[i]) < IA.MAXUNIT[unitType]:
                        #Vérifier il possede les ressources necessaire
                        if self.ressources[0] > 25:
                            pass
                            #Appel la méthode qui build unit
        #build Scout
        elif unitType == 2: 
            for i in self.units:
                if self.units[i] == unitType:
                    if self.nbrUnit(self.units[i]) < 2:
                        #Vérifier il possede les ressources necessaire
                        if self.ressources[0] > 25:
                            #Appel la méthode qui build Scout
                            pass
        #build ATTACK_SHIP 
        elif unitType == 3 :
            for i in self.units:
                if self.units[i] == unitType:
                    if self.nbrUnit(self.units[i]) < 2:
                        #Vérifier il possede les ressources necessaire
                        if self.ressources[0] > 25:
                            #Appel la méthode qui build Scout
                            pass
        #build CARGO
        elif unitType == 5 :
            for i in self.units:
                if self.units[i] == unitType:
                    if self.nbrUnit(self.units[i]) < 2:
                        #Vérifier il possede les ressources necessaire
                        if self.ressources[0] > 25:
                            #Appel la méthode qui build ATTACK_SHIP 
                            pass
       
                    
    #Game.buildBuilding(playerId, target, flag, unitIndex)
#M�thode qui retourne le nbr totale d'un type d'unit� pr�sente ds la liste
    def nbrUnit(self,unitType):
        nbr = 0
        for i in self.units[i]:
            if self.units[i] == unitType:
                nbr++
        return nbr
                
        
        