from imp_calc import db, bcrypt, login_manager,app
from flask_login import UserMixin
import jwt
from time import time
from datetime import datetime


#Working at 2:16:37 on YT course. Keep Doing Yusharth You are doing great
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Models
class User(db.Model, UserMixin):
    """docstring for User"""
    id = db.Column(db.Integer(),primary_key = True)
    username = db.Column(db.String(length=12),nullable = False, unique = True)
    email_address = db.Column(db.String(length=50),nullable = False, unique = True)
    password_hash = db.Column(db.String(length=60),nullable = False)
    created_at = db.Column(db.DateTime, nullable = False, default= datetime.utcnow)

    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


#this table is obsolete right now i.e. not used anywhere can be deleted even but left    |
#aside because more enhancements and developments work need to be done around            |
#no time for bugs and discrepancy reduction                                             \l/

# class Profile(db.Model):
#     # Id : Field which stores unique id for every row in
#     # database table.
#     # first_name: Used to store the first name if the user
#     # last_name: Used to store last name of the user
#     # Age: Used to store the age of the user
#     id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(20), unique=False, nullable=False)
#     last_name = db.Column(db.String(20), unique=False, nullable=False)
#     age = db.Column(db.Integer, nullable=False)     
#     owner = db.Column(db.Integer(),db.ForeignKey('user.id'))
#     # repr method represents how one object of this datatable   
#     # will look like
#     def __repr__(self):
#         return f"Name : {self.first_name}, Age: {self.age}"

        '''
    username ="Miguel",    email_address ="Grinber@gmail.com", password_hash = "1234567" ,items =  '''

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
...     print(current_app.config)                        # current_app installed- no more errors
...
<Config {'ENV': 'production', 'DEBUG': True, 'TESTING': False, 'PROPAGATE_EXCEPTIONS': None, 'SECRET_KEY': None, 'PERMANENT_SESSION_LIFETIME': datetime.timedelta(days=31), 'USE_X_SENDFILE': False, 'SERVER_NAME': None, 'APPLICATION_ROOT': '/', 'SESSION_COOKIE_NAME': 'session', 'SESSION_COOKIE_DOMAIN': None, 'SESSION_COOKIE_PATH': None, 'SESSION_COOKIE_HTTPONLY': True, 'SESSION_COOKIE_SECURE': False, 'SESSION_COOKIE_SAMESITE': None, 'SESSION_REFRESH_EACH_REQUEST': True, 'MAX_CONTENT_LENGTH': None, 'SEND_FILE_MAX_AGE_DEFAULT': None, 'TRAP_BAD_REQUEST_ERRORS': None, 'TRAP_HTTP_EXCEPTIONS': False, 'EXPLAIN_TEMPLATE_LOADING': False, 'PREFERRED_URL_SCHEME': 'http', 'JSON_AS_ASCII': None, 'JSON_SORT_KEYS': None, 'JSONIFY_PRETTYPRINT_REGULAR': None, 'JSONIFY_MIMETYPE': None, 'TEMPLATES_AUTO_RELOAD': None, 'MAX_COOKIE_SIZE': 4093, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///site.db', 'SQLALCHEMY_ENGINE_OPTIONS': {}, 'SQLALCHEMY_ECHO': False, 'SQLALCHEMY_BINDS': {}, 'SQLALCHEMY_RECORD_QUERIES': False, 'SQLALCHEMY_TRACK_MODIFICATIONS': False}>
>>> ctx = app.app_context()                              # Convenient way to do is by storing the context in a variable
>>> current_app.config
Traceback (most recent call last):
RuntimeError: Working outside of application context.
>>> ctx.push()                                           # Installing the context using the variable

    USE WHATEVER YOU WANT TO IN THIS

>>> ctx.pop()                                            #do this after using current app
''' 