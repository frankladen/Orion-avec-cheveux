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
    print('(Q)uitter')
    print('(R)efresh')
    print('Appuyez sur Enter pour envoyer')
    print(myServer.getNewMessage(numSocket))
    while 1:
        n=input("Msg >> ")
        if n.lower().rfind("q",0,1) != -1 and len(n) == 2:
            break
        elif n.lower().rfind("r",0,1) != -1 and len(n) == 2:
            print(myServer.getNewMessage(numSocket))
        else:
            myServer.addMessage(n.rstrip('\r'), numSocket)
            print(myServer.getNewMessage(numSocket))
except:
    print('Le serveur n\'existe pas.  Fermeture du programme')


print('thanks babe d\'avoir essayer')