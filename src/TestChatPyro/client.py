# -*- coding: iso-8859-1 -*-
import Pyro4
import socket
import player

n=input("Adresse du serveur >> ").rstrip('\r')
myServer=Pyro4.core.Proxy("PYRO:controleurServeur@"+n+":54440")
try:
    player1=player.Player()
    numSocket=myServer.getNumSocket(player1)
    print(numSocket)
    print(myServer.getNewMessage(numSocket))
    while 1:
        n=input("Msg >> ")
        if n.lower().rfind("q",0,1) != -1:
            break
        myServer.addMessage(n, numSocket)
        print(myServer.getNewMessage(numSocket))
except:
    print('Le serveur n\'existe pas.  Fermeture du programme')


print('thanks babe d\'avoir essayer')