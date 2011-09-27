# -*- coding: UTF-8 -*-
import Pyro4
import socket
from time import time

class ControleurServeur(object):
    def __init__(self):
        self.sockets=[]
        self.numClient=0
        self.seed = int(time())
    
    def getSeed(self):
        return self.seed;
    
    def addMessage(self, text, num):
        self.sockets[num].setText(text)
        
    def addChange(self, info, num):
        self.sockets[num].addPlayerChange(info)
    

    def frameDifference(self):
        frameList = []
        for player in self.sockets :
            frameList.append(player.getCurrentframe)
        
        #Je détermine le frame maximum et le frame minimum de tout les clients
        frameMax = max(frameList)
        frameMin = min(frameList)
        
        return (frameMax-frameMin)
    
    
    # Méthode qui détermine et isole les joueurs dont le frame courant est trop élevé par apport aux autres
    def playersTooDamnHigh(self):
        frameList = []
        for player in self.sockets :
            frameList.append(player.getCurrentframe)
        
        #Je détermine le frame maximum et le frame minimum de tout les clients
        frameMax = max(frameList)
        frameMin = min(frameList)
        
        #Détermine si l'écart entre les joueurs est trop grand (15 étant une valeur arbitraire, destinée à être modifié)
        if frameMax - frameMin > 15:
            playerMax = []
            
            #Je recherche et j'isole toute les occurences des joueurs ayant les frames les plus élevés
            if frameList.count(frameMax > 1):
                for i in frameList:
                    if i == frameMax:
                        playerMax.append(i)
         
            return playerMax
        
        return 0
                
    def getNumberOfPlayers(self):
        return len(self.sockets)
    
      
    def getChange(self,num): 
        #Je construit une chaîne de caractère contenant la liste de tout les changements de tout les joueurs
        change = ""
        for i in self.sockets:
            for a in i.getChangeList():
                change = change,a
            #Je remet la liste à zéro
            a.changeListRestore()
                
                
        #Si ce joueur fais partie de la liste des joueurs trop rapide, je rajoute le flag à la fin de la chaîne
        if self.playersTooDamnHigh().count(num) > 0 :
            change = change,"/",self.frameDifference()

        return change
    def getNewMessage(self, num):
        messages=[]
        for i in range(0,len(self.sockets)):
            if i != num:
                if self.sockets[i].getLastMess() != self.sockets[i].getText():
                    messages.append(self.sockets[i])
                    self.sockets[i].setLastMess(self.sockets[i].getText())
        return messages
    
       
    def getNumSocket(self, player):
        n=0
        for i in range(0,len(self.sockets)):
            if self.sockets[i].getIp() == player.getIp():
                print('a trouver le meme socket que le precedent')
                self.sockets[i]=player
                return i
            n=n+1
        print('ajoute le socket a la fin')
        self.sockets.append(player)
        return n
    
    def testConnect(self):
        #dummy afin de vérifier si le serveur existe
        i=1   

# le processus qui ecoute les messages des clients
adresse=socket.gethostbyname(socket.getfqdn())
daemon = Pyro4.core.Daemon(host=adresse,port=54440) 
# un objet ControleurServeur() dont les methodes peuvent etre invoquees, 
# connu sous le nom de controleurServeur
daemon.register(ControleurServeur(), "controleurServeur")  
 
 # juste pour voir quelque chose sur la console du serveur
print("Serveur Pyro actif sous le nom \'controleurServeur\' avec l'adresse "+adresse)

#on demarre l'ecoute des requetes
daemon.requestLoop()