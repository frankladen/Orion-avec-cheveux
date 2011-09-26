# -*- coding: UTF-8 -*-
import socket

class Player():
    def __init__(self, playerName):
        self.playerName = playerName
        self.ipPlayer = socket.gethostbyname(socket.getfqdn())
        self.text=""
        self.lastMess=""
        self.currentFrame = 0
        self.changeList = []
        
    def getText(self):
        return self.text
    
    def getIP(self):
        return self.ipPlayer
    
    def getPlayerName(self):
        return self.playerName
    
    def setText(self, text):
        self.text=text
    
    def getLastMess(self):
        return self.lastMess
    
    def setLastMess(self, text):
        self.lastMess=text
    
    def getCurrentFrame(self):
        return self.currentFrame
    
    #méthode qui rajoute le dernier changement à l'état du player dans la liste des update.
    def addPlayerChange(self,info):
        self.frameCourant = self.getFrameNum(info)
        self.changeList.append(info)
        
    #méthode à discuter, elle servira à trouver le numéro du frame du player dans la chaine de caractère des info.
    def getFrameNum(self, info):
        