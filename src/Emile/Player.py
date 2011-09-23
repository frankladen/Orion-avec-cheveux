import Unit as u

class Player():
    def __init__(self, name, galaxy, civilization=None, selectedObjects=None):
        self.name = name
        self.civilization = civilization
        self.selectedObjects = selectedObjects
        self.camera = Camera([400,400], galaxy)
        self.units = []
        self.units.append(u.Unit('Scout001',[400,400,0]))
        
class Camera():
    def __init__(self, defaultPos, galaxy):
        self.position = defaultPos
        self.screenCenter = (400,400)
        self.screenWidth = 800
        self.screenHeight = 800
        self.galaxy = galaxy
    
    def calcDistance(self, position):
        distX = position[0] - self.position[0]
        distY = position[1] - self.position[1]
        return [distX+self.screenCenter[0], distY+self.screenCenter[1]]
    
    
    def isInFOV(self, position):
        if position[0] > self.position[0]-self.screenWidth/2-20 and position[0] < self.position[0]+self.screenWidth/2+20:
            if position[1] > self.position[1]-self.screenHeight/2-20 and position[1] < self.position[1]+self.screenHeight/2+20:
                return True
        return False
    
    def move(self, direction):
        if direction == 'LEFT':
            if self.position[0] > (self.galaxy.width*-1)/2:
                self.position[0]-=5
        elif direction == 'RIGHT':
            if self.position[0] < self.galaxy.width/2:
                self.position[0]+=5
        elif direction == 'UP':
            if self.position[1] > (self.galaxy.height*-1)/2:
                self.position[1]-=5
        elif direction == 'DOWN':
            if self.position[1] < self.galaxy.height/2:
                self.position[1]+=5
        print('cameraPosition:',self.position)


