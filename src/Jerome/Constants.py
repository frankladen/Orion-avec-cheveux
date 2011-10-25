class Constants():
    WIDTH=0
    HEIGHT=1
        
class Game():
    MAX_NUMBER_OF_PLAYERS = 8

class MenuType():
    MAIN=1
    WAITING_FOR_RALLY_POINT=2
    MOTHERSHIP_BUILD_MENU=3
    
class MenuIcons():
    WIDTH=37
    HEIGHT=34

class UnitType():
    DEFAULT = 0
    MOTHERSHIP = 1
    SCOUT = 2
    ATTACK_SHIP = 3
    TRANSPORT = 4
    CARGO = 5
        
class UnitSize():
    MOTHERSHIP = [125,125]
    SCOUT = [18,15]
    ATTACK_SHIP = [28,32]
    TRANSPORT = [32,29]
    CARGO = [20,30]
    
class MoveSpeed():
    MOTHERSHIP = 0.0
    SCOUT = 4.0
    ATTACK_SHIP = 2.0
    TRANSPORT = 3.0 
    CARGO = 2.5
    DEFAULT = 1.0

class BuildTime():
    MOTHERSHIP = 0
    SCOUT = 200
    ATTACK_SHIP = 400
    TRANSPORT = 300
    CARGO = 250
    DEFAULT = 300
    
class BuildCost():
    MINERAL = 0
    GAS = 1
    MOTHERSHIP = [0,0]
    SCOUT = [50,0]
    ATTACK_SHIP = [150,100]
    TRANSPORT = [75,20]
    CARGO = [50,10]
    DEFAULT = [50,50]
    
class ViewRange():
    MOTHERSHIP = 400
    SCOUT = 200
    ATTACK_SHIP = 150
    TRANSPORT = 175
    CARGO = 175
    DEFAULT = 150
    
class RessourcesQuantity():
    MAX_ASTEROID_MINERALS = 300
    MAX_NEBULA_GAS = 300
    MAX_MINERAL_STACK = 3000
    MAX_GAS_STACK = 3000
    
class GalaxySize():
    WORLD_SIZE_MULTIPLIER = 1000
    SOLAR_SYSTEM = [500,500]
    PLANET = [15,15]
    SUN = [20,20]
    NEBULA = [15,15]
    ASTEROID = [16,16]
    MAX_PLANETS_PER_SOLAR_SYSTEM = 6
    MAX_ATRONOMICAL_OBJECTS_PER_SOLAR_SYSTEM = 4
    MIN_OBJECT_SPACING_FROM_BORDER = 25
    PLANET_MAX_SPACING_FROM_SUN = 125
    SUN_MIN_SPACING_FROM_BORDER = PLANET_MAX_SPACING_FROM_SUN + MIN_OBJECT_SPACING_FROM_BORDER
    SPAWN_POINT_MIN_SPACING = 20
    
class PlanetSize():
    WIDTH = 800
    HEIGHT = 600
    PADDING = 25
    MINERAL_SIZE = [48,64]
    GAS_SIZE = [24,24]
    
    