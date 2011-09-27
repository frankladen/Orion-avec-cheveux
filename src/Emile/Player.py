import Unit as u

class Player():
    def __init__(self, name, civilization=None):
        self.name = name
        self.civilization = civilization
        self.selectedObjects = []
        self.units = []
        self.units.append(u.Unit('Scout001',[0,0,0], moveSpeed=5.0))
        self.units.append(u.Unit('Scout002',[100,200,0], moveSpeed=5.0))
        
    def startGame(self, position, galaxy):
        self.camera = Camera(position ,galaxy)
            
class Camera():
    def __init__(self, defaultPos, galaxy):
        self.position = defaultPos
        self.screenCenter = (400,300)
        self.screenWidth = 800
        self.screenHeight = 600
        self.galaxy = galaxy
    
    def calcDistance(self, position):
        distX = position[0] - self.position[0]
        distY = position[1] - self.position[1]
        return [distX+self.screenCenter[0], distY+self.screenCenter[1]]
    
    def calcPointInWorld(self, x,y):
        dist = self.calcDistance([x,y])
        rX = self.position[0]-self.screenCenter[0]+x
        rY = self.position[1]-self.screenCenter[1]+y
        return [rX,rY,0]
    
    def calcPointOnMap(self, x, y):
        rX = x/200 * self.galaxy.width - self.galaxy.width/2
        rY = y/200 * self.galaxy.height - self.galaxy.height/2
        if rX < 0-self.galaxy.width/2+self.screenWidth/2:
            rX = 0-self.galaxy.width/2+self.screenWidth/2
        elif rX > self.galaxy.width/2-self.screenWidth/2:
            rX = self.galaxy.width/2-self.screenWidth/2
        if rY < 0-self.galaxy.height/2+self.screenHeight/2:
            rY = 0-self.galaxy.height/2+self.screenHeight/2
        elif rY > self.galaxy.height/2-self.screenHeight/2:
            rY = self.galaxy.height/2-self.screenHeight/2
        return [rX, rY]
    
    def isInFOV(self, position):
        if position[0] > self.position[0]-self.screenWidth/2-20 and position[0] < self.position[0]+self.screenWidth/2+20:
            if position[1] > self.position[1]-self.screenHeight/2-20 and position[1] < self.position[1]+self.screenHeight/2+20:
                return True
        return False
    
    def move(self, direction):
        if direction == 'LEFT':
            if self.position[0] > (self.galaxy.width*-1)/2+self.screenCenter[0]:
                self.position[0]-=5
        elif direction == 'RIGHT':
            if self.position[0] < self.galaxy.width/2 - self.screenCenter[0]:
                self.position[0]+=5
        elif direction == 'UP':
            if self.position[1] > (self.galaxy.height*-1)/2 + self.screenCenter[1]:
                self.position[1]-=5
        elif direction == 'DOWN':
            if self.position[1] < self.galaxy.height/2 - self.screenCenter[1]:
                self.position[1]+=5


