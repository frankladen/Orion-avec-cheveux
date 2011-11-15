# -*- coding: UTF-8 -*-
from xml.etree.ElementTree import *

class TechTree():
    def __init__(self):
        unitTechs = []
        buildingTechs = []
        mothershipTechs = []
        tree = ElementTree(file="TechTree.xml")
        units = tree.find("Units")
        for u in units.findall("Tech"):
            unitTechs.append(Tech(u.find("Name").text, u.find("Effect").text, int(u.find("Add").text), int(u.find("CostMine").text), int(u.find("CostGaz").text)))
        buildings = tree.find("Buildings")
        for b in buildings.findall("Tech"):
            buildingTechs.append(Tech(b.find("Name").text, b.find("Effect").text, int(b.find("Add").text), int(b.find("CostMine").text), int(b.find("CostGaz").text)))
        motherships = tree.find("Mothership")
        for m in motherships.findall("Tech"):
            mothershipTechs.append(Tech(m.find("Name").text, m.find("Effect").text, int(m.find("Add").text), int(m.find("CostMine").text), int(m.find("CostGaz").text)))

class Tech(TechTree):
    def __init__(self, name, effect, add, costMine, costGaz):
        self.name = name
        self.effect = effect
        self.add = add
        self.costMine = costMine
        self.costGaz = costGaz

tr = TechTree()
