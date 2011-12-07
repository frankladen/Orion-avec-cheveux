import Pyro4
import time
import subprocess

server = Pyro4.Proxy("PYRONAME:ServeurOrion")
print(len(server.getSockets()))
