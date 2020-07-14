from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_crontab import Crontab


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
db = SQLAlchemy(app)
crontab = Crontab(app)

from web_checker import routes
