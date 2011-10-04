# -*- coding: UTF-8 -*-
import math

class Helper(object):
    """ cette classe est utilise de facon statique sans creer d'objet"""
    def getAngledPoint(angle,longueur,cx,cy):
        """ angle est en radians"""
        x = (math.cos(angle)*longueur)+cx
        y = (math.sin(angle)*longueur)+cy
        return (x,y)
    getAngledPoint = staticmethod(getAngledPoint)

    def calcAngle(x1,y1,x2,y2):
        dx = x2-x1
        dy = y2-y1
        angle = (math.atan2(dy,dx) )
        return angle
    calcAngle = staticmethod(calcAngle)

    def calcDistance(x1,y1,x2,y2):
        dx = abs(x2-x1)**2
        dy = abs(y2-y1)**2
        distance=math.sqrt(dx+dy)
        return distance
    calcDistance = staticmethod(calcDistance)
        