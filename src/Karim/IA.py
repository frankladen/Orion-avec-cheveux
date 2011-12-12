# -*- coding: UTF-8 -*-
from Unit import *
from Flag import *
from Client import *
from Player import *
import random
import socket
import time
from Building import *

class IA(Player):
    MAXUNIT =(0,3,4,3,0,0,0,0,0,0)
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
        
                 
#    def choixAction(self):
#        r = random.randint(1,5)
#        
#        # choix d'actions
#        if r == 1:
#            print("moveeee")
#        elif r == 2:
#            print("build")
#            self.buildUnit(2)
#        else:
#            print("attaqueeeee")     
#     
    def choixAction(self):
        self.decisionExplor()
        #Si l'action explorer est terminée on passe à l'action buildUnit
        self.decisionBuildUnit()
        #Si l'action build est terminée on passe à l'action attaquer
        self.decisionAttack()
        
    def decisionExplor(self):
        pass
    
    def decisionBuildUnit(self):
        constructionUnit = self.buildings.index(self.motherships[0])
        for i in self.units:
            if i.type == 4: #unité  Cargo 
                self.buildUnitIA(i.type, constructionUnit)
                #if self.buildUnitIA(i.type, constructionUnit):
                print("créer cargo")
            elif i.type == 1: #unité  Scout
                if self.nbrUnit(2) == self.MAXUNIT[2] and self.nbrUnit(4) == self.MAXUNIT[4]:
                    self.buildUnitIA(i.type, constructionUnit)
                    print("créer scout")
#            elif i.type == 4: #unité  Transport
#                if self.nbrUnit(3) == self.MAXUNIT[3] and self.nbrUnit(8) == self.MAXUNIT[8] and self.nbrUnit(2) == self.MAXUNIT[2]:
#                    self.buildUnitIA(i.type, constructionUnit)
            elif i.type == 3 :
                if self.nbrUnit(3) ==self.MAXUNIT[3]and self.nbrUnit(2) == self.MAXUNIT[2] and self.nbrUnit(4) == self.MAXUNIT[4]:
                    self.buildUnitIA(i.type, constructionUnit)
                    print("créer tansport")
#            elif i.type == 7: #unité  Transport
#                if self.nbrUnit(3) == self.MAXUNIT[3] and self.nbrUnit(8) ==self.MAXUNIT[8] and self.nbrUnit(2) == self.MAXUNIT[4] and self.nbrUnit(4) == self.MAXUNIT[4] and self.nbrUnit(5) == self.MAXUNIT[5]:
#                    self.buildUnitIA(i.type, constructionUnit)
    #Méthode build()
    def buildUnitIA(self,unitType, constructionUnit):
        n=0
        for i in self.units:
            if i.type == unitType:
                if self.nbrUnit(unitType) < self.MAXUNIT[n]:
                    #Vérifier s'il possede les ressources necessaire

                    #Appel la méthode qui build unit
                    self.game.addUnit(unitType, constructionUnit) #voir la nouvelle version de game
                    print("ok-build")
                #else:
            n=n+1   #return True
                
    #def checkRessourcesBuildCost(self):  
      #  self.
#        buildCost = []
#        k=0
#        callBuild=True
#        for i in Unit.BUILD_COST:
#            for j in i:
#                buildCost.append(j) 
#        while(callBuild):
#            if self.ressources[k]>buildCost[k]:
#                callBuild=True
#            else:
#                callBuild=False
#        k=k+1
#        return callBuild
    
    def nbrUnit(self,unitType):
        nbr = 0
        for i in self.units:
            if i.type == unitType:
                nbr = nbr+1  
        return nbr
    
    def decisionAttack(self):
        pass


# Joueur IA 1 (stupid)       
#class IA1(IA): # hérite de la classe IA
#    def __init__(self):
#        IA.__init__(self, name, game, id , colorId)
# 
# # Joueur IA 2 (smart) 
#class IA1(IA): # hérite de la classe IA
#    def __init__(self):
#        IA.__init__(self, name, game, id , colorId)       
