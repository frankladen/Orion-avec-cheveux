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

    def buyUpgrade(self, name, branch, tech=None):
        if tech == None:
            for i in self.getBranch(branch):
                if self.getNames(branch)[self.getBranch(branch).index(i)] == name:
                    tech = i
                    break
        if not tech.isAvailable:
            if tech.child:
                return self.buyUpgrade(tech.name, branch, tech.child)
            else:
                return None
        else:
            tech.isAvailable = False
            if tech.child != None:
                tech.child.isAvailable = True
            return tech

    def getUpgrade(self, name, branch, tech=None):
        if tech == None:
            for i in self.getBranch(branch):
                if self.getNames(branch)[self.getBranch(branch).index(i)] == name:
                    tech = i
                    break
        if not tech.isAvailable:
            if tech.child != None:
                return self.getUpgrade(name, branch, tech.child)
            else:
                return None
        else:
            return tech

    def getNames(self, branch):
        names = []
        for i in self.getBranch(branch):
            tech = self.getUpgrade(i.name, branch, i)
            if tech != None:
                names.append(tech.name)
        return names

    def getTechs(self, branch):
        techs = []
        for i in self.getBranch(branch):
            tech = self.getUpgrade(i.name, branch, i)
            if tech != None:
                techs.append(tech)
        return techs

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
        if element.find("CostNuclear") != None:
            self.costNuclear = int(element.find("CostNuclear").text)
        else:
            self.costNuclear = 0
        if element.find("Upgrade") != None:
            self.child = TechUpgrade(self,element.find("Upgrade"))
        else:
            self.child = None

class TechUpgrade(Tech):
    def __init__(self, parent, element):
        Tech.__init__(self, parent, element)
        self.parent = parent
        self.isAvailable = False

