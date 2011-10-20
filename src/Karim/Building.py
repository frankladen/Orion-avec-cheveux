# -*- coding: UTF-8 -*-
import Target as t
import World as w
import Player as p

class Building(t.PlayerObject):
    def __init__(self, name, position):
        t.PlayerObject.__init__(self, name, position)
        
class WayPoint(Building):
    def __init__(self, position):
        super(WayPoint, self).__init__()
        #Verifier plus tard si le nom du building entr� est "wayPoint"
        self.name = 'way point'
        
    def checkVacantSpace(self, galaxy, players):
        #Psition choisie = ou pas à la position du sun: direction x=0, direction y=1
        for i in galaxy.solarSystemList:
            if i.sunPosition[0] > self.position[0]-10 and i.sunPosition[0] < self.position[0]+10:
                if i.sunPosition[1] > self.position[1]-10 and i.sunPosition[1] < self.position[1]+10:
                    return False
            #Psition choisie = ou pas à la position du planet: direction x=0, direction y=1
            for j in i.planets:
                if j.position[0] > self.position[0]-10 and j.position[0] < self.position[0]-10:
                    if j.position[1] > self.position[1]-10 and j.position[0] < self.position[1]+10:
                        return False
        #Psition choisie = ou pas à la position du unit: direction x=0, direction y=1
        for k in players.units:
            if k.position[0] > self.position[0]-10 and k.position[1] < self.position[0]+10: 
                if k.position[1] > self.position[1]-10 and k.position[1] < self.position[1]+10:
                    return False 
        #Psition choisie = ou pas à la position du building: direction x=0, direction y=1
        for m in players.spaceBuildings:
            if m.position[0] > self.position[0]-10 and k.position[1] < self.position[0]+10: 
                if m.position[1] > self.position[1]-10 and k.position[1] < self.position[1]+10:
                    return False
    

    
        
        
        
        