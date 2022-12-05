from flask import Flask , session
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

# mail = Mail(app)

s=URLSafeTimedSerializer(app.config['SECRET_KEY'])

admin = Admin(app)

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    
from imp_calc import routes, models, errors
from .models import User,Logs
from .routes import current_user
from flask_admin import AdminIndexView, expose


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
# We created this modelView for users
# def user_admin():
#     return User.query.filter_by(role='a')
# def user_manager():
#     return User.query.filter_by(role='m')
# def user_user():
#     return User.query.filter_by(role='u')
# def get_user_roles():
#     print("Thius us current_user",current_user)
#     if current_user and current_user.is_authenticated:
#         print("This is current user role",login.current_user.role)
#         if login.current_user.role == 'a':
#             form_choices = {
#         'role': [ ('a', 'Admin'), ('m', 'Manager'), ('u', 'User') ]
#         }
#         elif login.current_user.role == 'm':
#             form_choices = {
#             'role': [
#             ('u', 'User')
#             ]
#         }



class UserView(ModelView):
        # _roles = []
        # if login.current_user and login.current_user.is_authenticated:
        #     if login.current_user.role == 'a':
        #         _roles =  [('a', 'Admin'), ('m', 'Manager'), ('u', 'User')]
        #     elif login.current_user.role == 'm':
        #         _roles = [('u', 'User')]
        # return _roles
    column_exclude_list = ['logs', 'password_hash',]
    form_excluded_columns = ['logs']
    can_edit = True

    def form_choices(self):
        print("Thius us current_user",current_user)
        if current_user and current_user.is_authenticated:
            print("This is current user role",login.current_user.role)
            if login.current_user.role == 'a':
                form_choices = {
            'role': [ ('a', 'Admin'), ('m', 'Manager'), ('u', 'User') ]
            }
            elif login.current_user.role == 'm':
                form_choices = {
                'role': [
                ('u', 'User')
                ]
            } 
    
    def on_model_change(self, form, User, is_created=False):
        User.password = form.password_hash.data
    
    def is_accessible(self):
        return (login.current_user.role == 'a' or login.current_user.role == 'm' )

    form_overrides = dict(
        passhash=MyPassField,
    )
    form_widget_args = dict(
        passhash=dict(
            placeholder='Enter new password here to change password',
        ),
    )
    # if current_user:
    #     form_choices(current_user)
    # else:
    #     pass
    # def get_form_choices(self):
    #     if self.session.query(self.model).filter(self.model.role == 'a'):
    #         form_choices = {
    #                 'role': [ ('a', 'Admin'), ('m', 'Manager'), ('u', 'User') ]
    #                 }
    #     elif self.session.query(self.model).filter(self.model.rol=='m'):
    #         form_choices = {
    #                 'role': [ ('u', 'User') ]
    #                 }

    # def get_form_choices(self):
    #     if self.session.query(self.model).filter(self.model.role == 'a'):
    #         form_choices = {
    #                 'role': [ ('a', 'Admin'), ('m', 'Manager'), ('u', 'User') ]
    #                 }
    #     elif self.session.query(self.model).filter(self.model.rol=='m'):
    #         form_choices = {
    #                 'role': [ ('u', 'User') ]
    #                 }

    # get_form_choices(present_role = session["role"])

    #This code is good for filtring the queries by role = u but we aren't able to do things beyond that
    def get_query(self):
        if login.current_user.role == 'm':
            return self.session.query(self.model).filter(
                       self.model.role == 'u')
        else:
            return self.session.query(self.model)


"""class UserViewAdmins(ModelView):
    column_exclude_list = ['logs', 'password_hash',]
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
    )"""
    #This code is good for filtring the queries by role = u but we aren't able to do things beyond that
#####################################
class LogsView(ModelView):
    can_view_details = True
    can_edit = False
    can_create = False
    can_delete = False
    def is_accessible(self):
        return login.current_user.role == 'a' or login.current_user.role == 'm'

    # def get_query(self):
    #     if login.current_user.role == 'm':
    #         return self.session.query(self.model).filter(
    #                    User.role == 'u')
    #     else:
    #         return self.session.query(self.model)

    def get_query(self):

        if login.current_user.role == 'm':
            logList = self.model.query.join(User, User.id == self.model.user_id).filter(User.role == 'u')
            return logList
        
        elif login.current_user.role == 'u':
        	logList = self.model.query.join(User, User.id == self.model.user_id).filter(User.id == login.current_user.id)
        	return logList
        
        else:
        	logList = self.model.query.join(User, User.id == self.model.user_id)
        	return logList



#    This query isn't working and giving some issues it might be because of the "session execute" we rather want sesion 
admin.add_view(UserView(User, db.session))
admin.add_view(LogsView(Logs, db.session))