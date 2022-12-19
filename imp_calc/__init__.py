from flask import Flask , session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt 
from flask_login import LoginManager
from flask_migrate import Migrate
import flask_login as login
import os
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from datetime import timedelta
from flask_wtf import Form
from flask import render_template
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
login_manager.login_message_category= "info"
login_manager.login_message = ('User is not active, Please contact Administrator or Manager')
# mail = Mail(app);.

s=URLSafeTimedSerializer(app.config['SECRET_KEY'])
s
    
from imp_calc import routes, models, errors

# def get_user_roles():

#     # default role is a user
#     _roles = [('a', 'Admin'), ('m', 'Manager'), ('u', 'User')]
#     if current_user and current_user.is_authenticated:
#         print(current_user)
#         if current_user.has_role('a'):
#             print('Current user is an admin')
#             _roles = [('a', 'Admin'), ('m', 'Manager'), ('u', 'User')]
#         elif current_user.has_role('m'):
#             print('Current user is a manager')
#             _roles = [('u', 'User')]

#     print(f"Roles assigned to role choices: {_roles}")
#     return _roles


# class MyPassField(TextField):
#     def process_data(self, value):
#         self.data = ''  # even if password is already set, don't show hash here
#         # or else it will be double-hashed on save
#         self.orig_hash = value

#     def process_formdata(self, valuelist):
#         value = ''
#         if valuelist:
#             value = valuelist[0]
#         if value:
#             self.data = generate_password_hash(value)
#         else:
#             self.data = self.orig_hash

# class UserView(ModelView):
#         # _roles = []
#         # if login.current_user and login.current_user.is_authenticated:
#         #     if login.current_user.role == 'a':
#         #         _roles =  [('a', 'Admin'), ('m', 'Manager'), ('u', 'User')]
#         #     elif login.current_user.role == 'm':
#         #         _roles = [('u', 'User')]
#         # return _roles
#     print(current_user)
#     form_choices = {
#         'role': get_user_roles()
#         }
#     column_exclude_list = ['logs', 'password_hash',]
#     form_excluded_columns = ['logs']
#     can_edit = True
    
#     def on_model_change(self, form, User, is_created=False):
#         User.password = form.password_hash.data
    
#     def is_accessible(self):
#         return (current_user.role == 'a' or current_user.role == 'm' )

#     form_overrides = dict(
#         passhash=MyPassField,
#     )
#     form_widget_args = dict(
#         passhash=dict(
#             placeholder='Enter new password here to change password',
#         ),
#     )
# class LogsView(ModelView):
#     can_view_details = True
#     can_edit = False
#     can_create = False
#     can_delete = False
#     def is_accessible(self):
#         return current_user.role == 'a' or current_user.role == 'm'

#     def get_query(self):

#         if current_user.role == 'm':
#             logList = self.model.query.join(User, User.id == self.model.user_id).filter(User.role == 'u')
#             return logList
        
#         elif current_user.role == 'u':
#             logList = self.model.query.join(User, User.id == self.model.user_id).filter(User.id == current_user.id)
#             return logList
        
#         else:
#             logList = self.model.query.join(User, User.id == self.model.user_id)
#             return logList

# admin.add_view(UserView(User, db.session))
# admin.add_view(LogsView(Logs, db.session))