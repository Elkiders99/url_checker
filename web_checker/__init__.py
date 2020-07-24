from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_crontab import Crontab
import json
import os

os.chdir('/home/piojox/Server/web_checker')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
db = SQLAlchemy(app)
crontab = Crontab(app)
# Ojo con esto... ahora no podes mover NADA de lugar papa...
with open('web_checker/config.json') as f:
    config = json.loads(f.read())

from web_checker import routes

