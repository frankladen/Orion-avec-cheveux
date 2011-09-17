import random
#Echelle pour les objets de la galaxie:
#Grandeur: (1000x1000)xNbJoueur
#Un système solaire: 200x200
#Un soleil(étoile): 8x8
#une planète: 4x4
#Vaisseau mère: 3x3
#WayPoint: 2x2
#Autres vaisseau: 1x1
#Ceci n'est qu'une échelle donc n'importe quel grandeur dans la vue est bonne
#tant qu'on respecte cette échelle pour les grandeurs
class Galaxy():
    def __init__(self,nbPlayer):
    	self.width=(nbPlayer)*1000
    	self.height=(nbPlayer)*1000
    	self.depth=(nbPlayer)*1000
    	self.solarSystemList = []
    	for i in nbPlayer*6:
            placeFound = False
            while placeFound == False:
                x=random.random()
                y=random.random()
                placeFound = True
                for j in solarSystemList:
                    if x > j.sunPosition[0]-100 and x < j.sunPosition[0]+100:
                        if y > j.sunPosition[1]-100 and y > j.sunPosition[1]+100:
                            placeFound = False
            self.solarSystemList.append(SolarSystem(x,y,0))
                            
class SolarSystem():
    def __init__(self,sunX,sunY,sunZ):
        self.sunPosition = (sunX,sunY,sunZ)

galaxy=Galaxy(2)