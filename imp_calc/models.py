from imp_calc import db, bcrypt, login_manager,app
from flask_login import UserMixin
import jwt
from time import time
from datetime import datetime


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