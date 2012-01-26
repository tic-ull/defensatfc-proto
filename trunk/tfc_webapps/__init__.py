from os.path import dirname, join, abspath
from sys import path

#path.append(dirname(__file__))
path.append(join(dirname(abspath(__file__)), "packages"))
path.append(join(dirname(abspath(__file__)), "packages/suds-timestamp"))
path.append(join(dirname(abspath(__file__)), "packages/py-wkhtmltox"))
