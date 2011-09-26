# -*- coding: UTF-8 -*-
import Pyro4
import socket
import player

def printMessages():
    mess = myServer.getNewMessage(numSocket)
    for i in range(0,len(mess)):
        nom=mess[i].getPlayerName()
        text=mess[i].getText()
        print(nom,'-',text)

n=input("Adresse du serveur >> ").rstrip('\r')
myServer=Pyro4.core.Proxy("PYRO:controleurServeur@"+n+":54440")
try:
    myServer.testConnect()
    name = input('Quel est votre surnom >> ').rstrip('\r')
    player1=player.Player(name)
    numSocket=myServer.getNumSocket(player1)
    print('(Q)uitter')
    print('(R)efresh')
    print('Appuyez sur Enter pour envoyer')
    printMessages()
    while 1:
        n=input("Msg >> ")
        
        if n.lower().find('q',0,1) == 0 and len(n) == 2:
            break;
        elif n.lower().find('r',0,1) == 0 and len(n) == 2:
            printMessages()
        else:
            myServer.addMessage(n, numSocket)
            printMessages()
        
except:
    print('Le serveur n\'existe pas.')


print('Fermeture du programme.')