from imp_calc import db, bcrypt, login_manager,app
from flask_login import UserMixin
import jwt
from time import time
from datetime import datetime
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.orm import sessionmaker, relationship




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Models
class User(db.Model, UserMixin):
    """docstring for User"""
    id = db.Column(db.Integer(),primary_key = True)
    is_activate = db.Column(db.Boolean, default=True)
    username = db.Column(db.String(length=12),nullable = False, unique = True)
    role = db.Column(db.String(length=1),nullable=False)    
    password_hash = db.Column(db.String(length=60),nullable = False)
    created_at = db.Column(db.DateTime, nullable = False, default= datetime.utcnow)
    logs = relationship("Logs", backref="UserLogs")

    @property
    def is_active(self):
        return self.is_activate
    
    @property
    def password(self):
        return self.password
             
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

class Logs(db.Model):
    # id = db.Column(db.Integer,db.ForeignKey('user.id') )   #primary key
    # log_id = db.Column(db.Integer, primary_key=True)       #foreign key -> renamed "user_id"
    id = db.Column(db.Integer, primary_key=True) 
    user_id =  db.Column(db.Integer,db.ForeignKey('user.id'))
    activity = db.Column(db.String(length=50),nullable = False)
    dt_string = db.Column(db.String(length=60),nullable = False)



# class MyModelView(ModelView):
#     def is_accessible(self):
#         return False
#         # if current_user.id==1:
#         #     return True
#         # else:
#         #     

# admin.add_view(ModelView(User,db.session))


# class Role(db.Model):
#     __tablename__ = 'roles'
#     id = db.Column(db.Integer(), primary_key=True)
#     name = db.Column(db.String(50), unique=True)


# # Define the UserRoles association table
# class UserRoles(db.Model):
#     __tablename__ = 'user_roles'
#     id = db.Column(db.Integer(), primary_key=True)
#     user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
#     role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

# if current_user.id==1:
#                 admin.add_view(ModelView(Logs, db.session))
#                 admin.add_view(ModelView(User, db.session))
#             if current_user.id>1 and current_user.id<=3:
#                 admin.add_view(ModelView(Logs, db.session))