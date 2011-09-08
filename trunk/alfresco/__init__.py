from os.path import dirname, join, abspath
from sys import path

#path.append(dirname(__file__))
path.insert(0, join(dirname(abspath(__file__)), "packages"))
print path