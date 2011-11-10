# -*- coding: UTF-8 -*-
import Pyro4
import socket
import sys
from time import time

class ControleurServeur(object):
    def __init__(self):
        self.sockets=[]
        self.refreshes=[]
        self.gameIsStarted = False
        self.isStopped = True
        self.seed = int(time())
        self.mess = [[-1, 'Choisissez la couleur de votre battalion',False],[-1, '________________________________________________________________',False],[-1, 'Le but est détruire le vaisseau mère des autres équipes',False],[-1, 'en bâtissant votre propre battalion et en dominant.',False],[-1, '________________________________________________________________',False]]
        self.changeList = []
        self.readyPlayers = []
        self.choiceColors = [["Orange", False], ["Rouge", False], ["Bleu", False], ["Vert", False], ["Jaune", False], ["Brun", False], ["Blanc", False], ["Rose", False]]
    
    def getSeed(self):
        return self.seed;
    
    def getSockets(self):
        return self.sockets

    def getColorChoices(self):
        return self.choiceColors

    def isGameStopped(self):
        return self.isStopped
    
    def isGameStarted(self):
        return self.gameIsStarted
    
    def startGame(self):
        self.seed = int(time())
        self.gameIsStarted = True
        self.isStopped = False
        #J'initie mon tableau de changements et de refreshes
        for i in range(0, self.getNumberOfPlayers()):
            self.changeList.append([])
            self.refreshes.append(0)
            self.readyPlayers.append(False)
    
    def removePlayer(self, ip, login, playerId):
        self.sockets[playerId][2] = True
        if playerId == 0:
            self.isStopped = True
            self.gameIsStarted = False
            self.refreshes = []
            self.changeList = []
            self.sockets = []
            self.readyPlayers = []
            self.choiceColors = [["Orange", False], ["Rouge", False], ["Bleu", False], ["Vert", False], ["Jaune", False], ["Brun", False], ["Blanc", False], ["Rose", False]]
            self.mess = ['Système de chat de Orion']
    
    def addMessage(self, text, name, idPlayer, allies):
        self.mess.append([idPlayer ,name+" : "+text,allies])
    
    def getMessage(self):
        return self.mess
        
    def addChange(self, change):
        #décider à quel frame effectuer l'action
        #playerId = int(change.split("/")[0])
        change = change+'/'+str(self.decideActionRefresh())
        for ch in self.changeList:
            ch.append(change)
  
    def isThisColorChosen(self, colorName, playerId):
        for i in range(0,len(self.choiceColors)):
            if colorName == self.choiceColors[i][0]:
                colorId = i
        if self.choiceColors[colorId][1]:
            return True
        else:
            if self.sockets[playerId][3] != -1:
                self.choiceColors[self.sockets[playerId][3]][1] = False
            self.sockets[playerId][3]=colorId
            self.choiceColors[colorId][1] = True
            return False

    def firstColorNotChosen(self, playerId):
        for i in self.choiceColors:
            if i[1] == False:
                i[1] = True
                self.sockets[playerId][3] = self.choiceColors.index(i)
                break
        
    def refreshPlayer(self, playerId, refresh):
        self.refreshes[playerId] = refresh
    
    def decideActionRefresh(self):
        #décide à quel refresh les clients doivent effectuer la prochaine action
        return (max(self.refreshes)+2)

    def frameDifference(self):
        frameList = []
        for player in self.sockets :
            frameList.append(player.getRefresh)
        #Je détermine le frame maximum et le frame minimum de tout les clients
        frameMax = max(frameList)
        frameMin = min(frameList)
        return (frameMax-frameMin)
    
    # Méthode qui détermine et isole les joueurs dont le frame courant est trop élevé par apport aux autres
    def amITooHigh(self, playerId):
        refresh = []
        #Je détermine le frame minimum de tout les clients
        for r in range(len(self.refreshes)):
            if self.sockets[r][2] != True:
                refresh.append(self.refreshes[r])
        frameMin = min(refresh)
        #Détermine si l'écart entre les joueurs est trop grand (15 étant une valeur arbitraire, destinée à être modifié)
        if self.refreshes[playerId] - frameMin > 5:
            return (self.refreshes[playerId] - frameMin)*50
        return 50

    def isEveryoneReady(self, playerId):
        self.readyPlayers[playerId]=True
        for i in self.readyPlayers:
            if i==False:
                return False
        return True
                
    def getNumberOfPlayers(self):
        return len(self.sockets)
      
    def getChange(self,num,refresh):
        self.refreshes[num] = refresh
        changes = self.changeList[num]
        self.changeList[num] = []
        #Si ce joueur fais partie de la liste des joueurs trop rapide, je rajoute le flag à la fin du tableau
        #if self.playersTooDamnHigh().count(num) > 0 :
        #    change.append("*",self.frameDifference())
        return changes
       
    def getNumSocket(self, login, ip):
        if len(self.sockets) < 8:
            self.sockets.append([ip,login,False, -1])
            return len(self.sockets)-1
          

if len(sys.argv) > 1:
    adresse = sys.argv[1]
else:
    adresse=socket.gethostbyname(socket.getfqdn())
try:
    daemon = Pyro4.core.Daemon(host=adresse,port=54400) 
    # un objet ControleurServeur() dont les methodes peuvent etre invoquees, 
    daemon.register(ControleurServeur(), "ServeurOrion")  
     
    # juste pour voir quelque chose sur la console du serveur
    print("Serveur Pyro actif sous le nom \'ServeurOrion\' avec l'adresse "+adresse)
    #on demarre l'ecoute des requetes
    daemon.requestLoop()
except socket.error:
    sys.exit(1)


        
