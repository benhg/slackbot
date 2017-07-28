import sys
import os

#sys.path.insert(0, '/var/www/slackFlask')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

#from /var/www/slackFlask/slackFlask.py import app as application
from slackFlask import app as application
os.chmod('/var/www/slackFlask/slackFlask.pyc',0777)

