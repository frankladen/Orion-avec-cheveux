# -*- coding: UTF-8 -*-
import Unit

class Scout(Unit):
    def __init__(self, name, position):
        super(Scout, self).__init__()
        self.name = name
        self.position = position