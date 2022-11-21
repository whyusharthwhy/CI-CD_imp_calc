from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt 
from flask_login import LoginManager
from flask_migrate import Migrate

import os
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from datetime import timedelta

app = Flask(__name__)
app.debug = True

# Setting up my database

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY']= '0b843376d6f247b8a5e38df2'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes = 5)

#creating a sqlalchemy instance
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

login_manager.login_view = "login"
login_manager.login_message_category="info"

# mail = Mail(app)

s=URLSafeTimedSerializer(app.config['SECRET_KEY'])

from imp_calc import routes, models, errors