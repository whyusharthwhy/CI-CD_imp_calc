from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt 
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate

import os
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from logging import FileHandler, INFO
import logging
from datetime import timedelta



logging.basicConfig(filename='record.log', level=logging.DEBUG, 
	format= '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
      datefmt='%H:%M:%S')
logger = logging.getLogger('imp_calc')
logger.setLevel(logging.INFO)

app = Flask(__name__)
app.debug = True

#app.config['SECRET_KEY'] = 'AntheaPharma*01'
###########DATABASE SETUP###############################
# Setting up my database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY']= '0b843376d6f247b8a5e38df2'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes = 30)
#creating a sqlalchemy instance
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

login_manager.login_view = "login"
login_manager.login_message_category="info"

#Same configuration has been done in Config file
# app.config['MAIL_SERVER']='smtp.googlemail.com'
# app.config['MAIL_USERNAME']=os.environ.get('MAIL_USERNAME')
# app.config['MAIL_PASSWORD']=os.environ.get('MAIL_PASSWORD')
# app.config['MAIL_PORT']=587
# app.config['MAIL_USE_TLS']=True
# Tried using the cfg file configuration
#app.config.from_pyfile(os.path.split(os.getcwd())[0],'config.cfg')

app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'yusharth@gmail.com',
    MAIL_PASSWORD = 'Yush@1999',
))


mail = Mail(app)

s=URLSafeTimedSerializer(app.config['SECRET_KEY'])

from imp_calc import routes, models, errors

'''
To make changes in database if it shows application context error you can do the following things:
>>> from imp_calc import app # remember imp_calc is your app name as the whole thing is converted into package
>>> from flask import current_app # this one is a property of flask
>>> app
<Flask 'imp_calc'>
>>> current_app
<LocalProxy unbound> #This error was we supposed to get
>>> current_app.config 
Traceback (most recent call last):
RuntimeError: Working outside of application context.
>>> app.config
<Config {'ENV': 'production', 'DEBUG': True, 'TESTING': False, 'PROPAGATE_EXCEPTIONS': None, 'SECRET_KEY': None, 'PERMANENT_SESSION_LIFETIME': datetime.timedelta(days=31), 'USE_X_SENDFILE': False, 'SERVER_NAME': None, 'APPLICATION_ROOT': '/', 'SESSION_COOKIE_NAME': 'session', 'SESSION_COOKIE_DOMAIN': None, 'SESSION_COOKIE_PATH': None, 'SESSION_COOKIE_HTTPONLY': True, 'SESSION_COOKIE_SECURE': False, 'SESSION_COOKIE_SAMESITE': None, 'SESSION_REFRESH_EACH_REQUEST': True, 'MAX_CONTENT_LENGTH': None, 'SEND_FILE_MAX_AGE_DEFAULT': None, 'TRAP_BAD_REQUEST_ERRORS': None, 'TRAP_HTTP_EXCEPTIONS': False, 'EXPLAIN_TEMPLATE_LOADING': False, 'PREFERRED_URL_SCHEME': 'http', 'JSON_AS_ASCII': None, 'JSON_SORT_KEYS': None, 'JSONIFY_PRETTYPRINT_REGULAR': None, 'JSONIFY_MIMETYPE': None, 'TEMPLATES_AUTO_RELOAD': None, 'MAX_COOKIE_SIZE': 4093, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///site.db', 'SQLALCHEMY_ENGINE_OPTIONS': {}, 'SQLALCHEMY_ECHO': False, 'SQLALCHEMY_BINDS': {}, 'SQLALCHEMY_RECORD_QUERIES': False, 'SQLALCHEMY_TRACK_MODIFICATIONS': False}>
>>> with app.app_context():                              # Creates an application context and install it on the thread
...     print(current_app.config)						 # current_app installed- no more errors
...
<Config {'ENV': 'production', 'DEBUG': True, 'TESTING': False, 'PROPAGATE_EXCEPTIONS': None, 'SECRET_KEY': None, 'PERMANENT_SESSION_LIFETIME': datetime.timedelta(days=31), 'USE_X_SENDFILE': False, 'SERVER_NAME': None, 'APPLICATION_ROOT': '/', 'SESSION_COOKIE_NAME': 'session', 'SESSION_COOKIE_DOMAIN': None, 'SESSION_COOKIE_PATH': None, 'SESSION_COOKIE_HTTPONLY': True, 'SESSION_COOKIE_SECURE': False, 'SESSION_COOKIE_SAMESITE': None, 'SESSION_REFRESH_EACH_REQUEST': True, 'MAX_CONTENT_LENGTH': None, 'SEND_FILE_MAX_AGE_DEFAULT': None, 'TRAP_BAD_REQUEST_ERRORS': None, 'TRAP_HTTP_EXCEPTIONS': False, 'EXPLAIN_TEMPLATE_LOADING': False, 'PREFERRED_URL_SCHEME': 'http', 'JSON_AS_ASCII': None, 'JSON_SORT_KEYS': None, 'JSONIFY_PRETTYPRINT_REGULAR': None, 'JSONIFY_MIMETYPE': None, 'TEMPLATES_AUTO_RELOAD': None, 'MAX_COOKIE_SIZE': 4093, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///site.db', 'SQLALCHEMY_ENGINE_OPTIONS': {}, 'SQLALCHEMY_ECHO': False, 'SQLALCHEMY_BINDS': {}, 'SQLALCHEMY_RECORD_QUERIES': False, 'SQLALCHEMY_TRACK_MODIFICATIONS': False}>
>>> ctx = app.app_context()								 # Convenient way to do is by storing the context in a variable
>>> current_app.config
Traceback (most recent call last):
RuntimeError: Working outside of application context.
>>> ctx.push()											 # Installing the context using the variable

	USE WHATEVER YOU WANT TO IN THIS

>>> ctx.pop()											 #do this after using current app
'''

#logging smtp errors to the mail
# from logging.handlers import SMTPHandler
# if not app.debug:
#     if app.config['MAIL_SERVER']:
#         auth = None
#         if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
#             auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
#         secure = None
#         if app.config['MAIL_USE_TLS']:
#             secure = ()
#         mail_handler = SMTPHandler(
#             mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
#             fromaddr='no-reply@' + app.config['MAIL_SERVER'],
#             toaddrs=app.config['ADMINS'], subject='imp_calc Failure',
#             credentials=auth, secure=secure)
#         mail_handler.setLevel(logging.ERROR)
#         app.logger.addHandler(mail_handler)   