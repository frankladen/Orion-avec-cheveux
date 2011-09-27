# -*- coding: UTF-8 -*-
import Pyro4
import socket
import player

class ControleurServeur(object):
    def __init__(self):
        self.sockets=[]
        self.numClient=0
    
    def addMessage(self, text, num):
        self.sockets[num].setText(text)
        
    def addChange(self, info, num):
        self.sockets[num].addPlayerChange(info)
    
    
    # Méthode qui envoie les changements aux joueurs, et décide qui dois en recevoir ou non, selon le retard que peuvent avoir pris certain player.
    def getChange(self, num):
        frameList = []
        for player in self.sockets :
            frameList.append(player.getCurrentframe)
        
        #Je détermine le frame maximum et le frame minimum de tout les clients
        frameMax = max(frameList)
        frameMin = min(frameList)
        
        #Détermine si l'écart entre les joueurs est trop grand (15 étant une valeur arbitraire, destinée à être modifié)
        if frameMax - frameMin > 15:
            playerMax = []
            playerMin = []
            
            #Je recherche et j'isole toute les occurences des joueurs ayant les frames les plus élevés
            if frameList.count(frameMax > 1):
                for i in frameList:
                    if i == frameMax:
                        playerMax.append(self.sockets[i])
        
        return #liste de changement auquel un un "flag" à été rajouté indiquant aux joueurs 
                #concernées de ralentir le rythme ainsi qu'un indication sur le nombre de frame qu'ils ont à "attendre" (frameMax-FrameMin)
                #La structure de ce flag devra être discuté avec monsieur Hinse mardi !
                
        
        
    
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
            if self.sockets[i].getIP() == player.getIP():
                print('a trouver le meme socket que le precedent')
                self.sockets[i]=player
                return i
            n=n+1
        print('ajoute le socket a la fin')
        self.sockets.append(player)
        return n
    
    def testConnect(self):
        #dummy afin de v�rifier si le serveur existe
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