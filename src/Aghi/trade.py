# -*- coding: ISO-8859-1 -*-
from tkinter import *

class Vue(object):
    def __init__(self,parent):
        self.root=Tk()
        self.parent=parent
        self.vueechange=VueEchange(self)
        self.menuBase()
        self.cadreActif=self.cadreMenu
        self.cadreMenu.pack()
        
    def menuBase(self):
        self.cadreMenu=Frame(self.root)
        bStartTrade = Button(self.cadreMenu,text="Start Trade",command=self.startTrade)
        bStartTrade.grid(column=1,row=2)
        
    def startTrade(self):
        if self.cadreActif:
            self.cadreActif.pack_forget()
        self.cadreActif=self.vueechange.cadreTrader
        self.cadreActif.pack()
        
        
    def tradeOuiNon(self,joueur):
        if self.cadreActif:
            self.cadreActif.pack_forget()
        self.vueechange.etiqOuiNon.config(text="Voulez-vous échanger avec "+joueur)
        self.cadreActif=self.vueechange.cadreOuiNon
        self.cadreActif.pack()
        
    def menuTrade(self):
        if self.cadreActif:
            self.cadreActif.pack_forget()
        self.cadreActif=self.vueechange.cadreMenuTrade
        self.cadreActif.pack()
        
    def confirmationDu2Joueur(self):
        if self.cadreActif:
            self.cadreActif.pack_forget()
        self.cadreActif = self.vueechange.cadreConfirmationDu2Joueur
        self.cadreActif.pack()
        
class VueEchange(object):
    def __init__(self,parent):
        #self.fen=Toplevel(self.parent.root)
        self.parent=parent
        self.tradePlayers() # fenetre 1
        self.tradeOuiNon() # fenetre 2
        self.menuTrade() # fenetre 3
        self.confirmationDu2Joueur() #fenetre 4
        
    def tradePlayers(self,listeJoueurs=['Couscous', 'Poutine', 'Burger', 'Shishtaouk']):
        self.cadreTrader=Frame(self.parent.root)
        question = Label(self.cadreTrader,text="Avec qui voulez-vous trader ?")
        question.grid(column=0,row=0)
        self.spinJoueurs = Spinbox(self.cadreTrader,values=listeJoueurs)
        self.spinJoueurs.grid(row=1,column=0)
        bOK = Button(self.cadreTrader,text="Annuler", command=self.tradeAnnuler)
        bOK.grid(column=0,row=2)
        bOK = Button(self.cadreTrader,text="Ok", command=self.requeteTrade)
        bOK.grid(column=1,row=2)
        print("fenetre 1")
        
    def requeteTrade(self):
        self.parent.parent.requeteTrade(self.spinJoueurs.get())
                
    def tradeAnnuler(self):
        print("ANNULER")
        
    def tradeOuiNon(self,nom="toto"):
        self.cadreOuiNon=Frame(self.parent.root)
        self.etiqOuiNon = Label(self.cadreOuiNon,text='Voulez-vous trader avec ' + nom +' ?')
        self.etiqOuiNon.grid(column=0,row=0)
        bOui = Button(self.cadreOuiNon,text="Oui",command=self.parent.menuTrade)
        bOui.grid(column=1,row=2)
        bNon = Button(self.cadreOuiNon,text="Non",command=self.tradeRefuser)
        bNon.grid(column=2,row=2)
        print("fenêtre 2")
 
    def tradeRefuser(self):
        print("ANNULER NEGRO")
        
    def tradeAccepter(self):
        print("ACCEPTER BITCH")
        
    def confirmationDu2Joueur(self):
        self.cadreConfirmationDu2Joueur=Frame(self.parent.root)
        self.etiqOuiNon = Label(self.cadreConfirmationDu2Joueur,text='Que voulez-vous ?')
        self.etiqOuiNon.grid(column=0,row=0)
        bAccepter = Button(self.cadreConfirmationDu2Joueur,text="Accepter",command=self.tradeAccepter)
        bAccepter.grid(column=1,row=2)
        bRefuse = Button(self.cadreConfirmationDu2Joueur,text="Refuse",command=self.tradeRefuser)
        bRefuse.grid(column=2,row=2)
        bModifer = Button(self.cadreConfirmationDu2Joueur,text="Modifier",command=self.parent.menuTrade)
        bModifer.grid(column=3,row=2)
        print("fenêtre 4")
      
    def menuTrade(self):
        self.cadreMenuTrade = Frame(self.parent.root)
        # minerals Joueurs 1
        self.nomJoueur1 = Label(self.cadreMenuTrade, text='Joueur 1')
        self.nomJoueur1.grid(row=1,column=1)
        self.etiqMenieral1 = Label(self.cadreMenuTrade,text='Minerals ')
        self.etiqMenieral1.grid(row=2,column=0)
        self.spinMinerals1 = Spinbox(self.cadreMenuTrade, from_=0, to=100)
        self.spinMinerals1.grid(row=2,column=1)
        # gaz Joueurs 1
        self.etiqGaz1 = Label(self.cadreMenuTrade,text='Gaz ')
        self.etiqGaz1.grid(row=4,column=0)
        self.spinGaz1 = Spinbox(self.cadreMenuTrade, from_=0, to=100)
        self.spinGaz1.grid(row=4,column=1)
        # Bouton ECHANGE
        bEchange = Button(self.cadreMenuTrade,text="Échange",command=self.parent.confirmationDu2Joueur)
        bEchange.grid(column=2,row=2)
        # minerals Joueurs 2
        self.nomJoueur2 = Label(self.cadreMenuTrade, text='Joueur 2')
        self.nomJoueur2.grid(row=1,column=4)
        self.etiqMenieral2 = Label(self.cadreMenuTrade,text='Minerals ')
        self.etiqMenieral2.grid(row=2,column=4)
        self.spinMinerals2 = Spinbox(self.cadreMenuTrade, from_=0, to=100)
        self.spinMinerals2.grid(row=2,column=4)
        # gaz Joueurs 2
        self.etiqGaz2 = Label(self.cadreMenuTrade,text='Gaz ')
        self.etiqGaz2.grid(row=4,column=4)
        self.spinGaz2 = Spinbox(self.cadreMenuTrade, from_=0, to=100)
        self.spinGaz2.grid(row=4,column=4)
        print("fenêtre 3")
           
class Controleur(object):
    def __init__(self):
        self.vue=Vue(self)
        
    def requeteTrade(self,joueur):
        if 1:
            # test en boucle locale
            self.vue.tradeOuiNon(joueur) 
    
if __name__ == '__main__':
    con=Controleur()
    con.vue.root.mainloop()