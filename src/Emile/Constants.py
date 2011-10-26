# -*- coding: UTF-8 -*-

class MenuType():
    MAIN=1
    WAITING_FOR_RALLY_POINT=2
    MOTHERSHIP_BUILD_MENU=4

#J'ai mis des String, car on aura besoin d'afficher ces valeurs dans le jeu
class UnitType():
    SCOUT='Scout'
    SPACE_ATTACK_UNIT="Attack"
    MOTHERSHIP = "MotherShip"
    

class FlagState():
    STANDBY=1
    MOVE=2
    PATROL=4
    ATTACK=8
    GATHER=16
    BUILD=32
    LAND=64
    RESEARCH=128
    DESTROY=256 

class MoveSpeed():
    SCOUT = 4.0
    SPACE_ATTACK_UNIT = 2.0
    MOTHERSHIP = 0.0

class BuildTime():
    SCOUT = 200
    SPACE_ATTACK_UNIT = 400
    
class ViewRange():
    SCOUT = 200
    SPACE_ATTACK_UNIT = 150
    MOTHERSHIP = 400
   
