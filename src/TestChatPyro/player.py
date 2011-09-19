# -*- coding: iso-8859-1 -*-
import socket

class Player():
    def __init__(self, playerName):
        self.playerName = playerName
        self.ipPlayer = socket.gethostbyname(socket.getfqdn())
        self.text="Aucun"
        
    def getText(self):
        return self.text
    
    def getIP(self):
        return self.ipPlayer
    
    def getPlayerName(self):
        return self.playerName
    
    def setText(self, text):
        self.text=text