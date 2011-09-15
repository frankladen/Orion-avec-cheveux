from Constants import Civilizations 

class Civilization():
    def __init__(self, type):
        if type == Civilizations.HUMAN:
            self.name = "Humans"
            self.Units = [0,1,2]
        elif type == Civilizations.CYBORG:
            self.name = "Cyborgs"
            self.Units = [3,4,5]
            
civ = Civilization(Civilizations.CYBORG)
print (civ.name)