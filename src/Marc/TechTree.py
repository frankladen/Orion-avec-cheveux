# -*- coding: UTF-8 -*-
from xml.etree.ElementTree import *

class TechTree():
    UNITS=0
    BUILDINGS=1
    MOTHERSHIP=2
    
    def __init__(self):
        self.unitTechs = []
        self.buildingTechs = []
        self.mothershipTechs = []
        tree = ElementTree(file="TechTree.xml")
        units = tree.find("Units")
        for u in units.findall("Tech"):
            self.unitTechs.append(Tech(self, u))
        buildings = tree.find("Buildings")
        for b in buildings.findall("Tech"):
            self.buildingTechs.append(Tech(self, b))
        motherships = tree.find("Mothership")
        for m in motherships.findall("Tech"):
            self.mothershipTechs.append(Tech(self, m))

    def buyUpgrade(self, effect, branch, tech=None):
        if tech == None:
            for i in self.getBranch(branch):
                if i.effect == effect:
                    tech = i
                    break
        if not tech.isAvailable:
            if tech.child:
                self.buyUpgrade(effect, branch, tech.child)
        else:
            tech.isAvailable = False
            if tech.child != None:
                tech.child.isAvailable = True

    def showUpgrade(self, effect, branch, tech=None):
        if tech == None:
            for i in self.getBranch(branch):
                if i.effect == effect:
                    tech = i
                    break
        if not tech.isAvailable:
            if tech.child != None:
                self.showUpgrade(effect, branch, tech.child)
        else:
            print(tech.name)
            #return tech.name

    def getBranch(self, branch):
        if branch == self.UNITS:
            return self.unitTechs
        elif branch == self.BUILDINGS:
            return self.buildingTechs
        elif branch == self.MOTHERSHIP:
            return self.mothershipTechs
                
class Tech(TechTree):
    def __init__(self, parent, element):
        self.parent = parent
        self.name = element.find("Name").text
        self.effect = element.find("Effect").text
        self.add = int(element.find("Add").text)
        self.costMine = int(element.find("CostMine").text)
        self.costGaz = int(element.find("CostGaz").text)
        self.isAvailable = True
        if element.find("Upgrade") != None:
            self.child = TechUpgrade(self,element.find("Upgrade"))
        else:
            self.child = None

class TechUpgrade(Tech):
    def __init__(self, parent, element):
        Tech.__init__(self, parent, element)
        self.parent = parent
        self.isAvailable = False

tr = TechTree()
print('Affichage upgrades')
tr.showUpgrade('S', tr.UNITS)

print('J\'achète un upgrade de vitesse première échelon')
tr.buyUpgrade('S', tr.UNITS)

print('Affichage après achat')
tr.showUpgrade('S', tr.UNITS)

print('Achat Upgrade')
tr.buyUpgrade('S', tr.UNITS)

print('Affichage après deuxième achat')
tr.showUpgrade('S', tr.UNITS)


