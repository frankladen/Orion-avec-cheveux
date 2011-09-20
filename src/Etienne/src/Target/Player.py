class Player():
    def __init__(self, name, civilization=None, selectedObjects=None, currentView=None):
        self.name = name
        self.civilization = civilization
        self.selectedObjects = selectedObjects
        self.currentView = currentView