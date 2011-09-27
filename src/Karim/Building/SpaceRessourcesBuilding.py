#-*- coding: UTF-8 -*-
class SpaceRessourceBuilding(SpaceBuilding):
    def __init__(self, collectRate):
        self.collectRate = collectRate
        super(SpaceRessourceBuilding, self).__init__()