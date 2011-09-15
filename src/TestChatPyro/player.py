# -*- coding: iso-8859-1 -*-
import socket

class Player(object):
    def __init__(self):
        self.ipPlayer = socket.gethostbyname(socket.getfqdn())
        self.text="ass"
        
    def getText(self):
        return self.text
    
    def getIP(self):
        return self.ipPlayer
    
    def setText(self, text):
        self.text=text