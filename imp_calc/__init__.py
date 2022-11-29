from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt 
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_admin import Admin
import flask_login as login
import os
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from datetime import timedelta
from flask_admin.contrib.sqla import ModelView
from flask_wtf import Form

from wtforms import TextField, BooleanField
from wtforms.validators import Required
app = Flask(__name__,template_folder='templates', static_folder='static')
app.debug = True

# Setting up my database

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY']= '0b843376d6f247b8a5e38df2'
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes = 5)

#creating a sqlalchemy instance
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

login_manager.login_view = "login"
login_manager.login_message_category="info"

# mail = Mail(app)

s=URLSafeTimedSerializer(app.config['SECRET_KEY'])
admin = Admin(app)

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    
from imp_calc import routes, models, errors
from .models import User,Logs
from .routes import current_user


''' all for user privilidges and password manipulation'''




class MyPassField(TextField):
    def process_data(self, value):
        self.data = ''  # even if password is already set, don't show hash here
        # or else it will be double-hashed on save
        self.orig_hash = value

    def process_formdata(self, valuelist):
        value = ''
        if valuelist:
            value = valuelist[0]
        if value:
            self.data = generate_password_hash(value)
        else:
            self.data = self.orig_hash

class UserView(ModelView):
    column_exclude_list = ['logs',]
    form_excluded_columns = ['logs']
    can_edit = True
    
    def on_model_change(self, form, User, is_created=False):
    	   User.password = form.password_hash.data
    
    def is_accessible(self):
        return login.current_user.role == 'a'

    form_overrides = dict(
        passhash=MyPassField,
    )
    form_widget_args = dict(
        passhash=dict(
            placeholder='Enter new password here to change password',
        ),
    )


class LogsView(ModelView):
    can_view_details = True
    can_edit = False
    can_create = False
    can_delete = False
    def is_accessible(self):
        return login.current_user.role == 'a' or login.current_user == 'm'


admin.add_view(UserView(User, db.session))
admin.add_view(LogsView(Logs, db.session))

# if current_user.role == 'a':
#     admin.add_view(UserView(User, db.session))
#     admin.add_view(LogsView(Logs, db.session))
# elif current_user.role == 'm':
#     admin.add_view(LogsView(Logs, db.session))