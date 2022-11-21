from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from imp_calc.models import User

class RegisterForm(FlaskForm):

    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username')

    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email Address already exists! Please try a different email address')

    username = StringField(label='User Name:', validators = [Length(min=1,max=30), DataRequired()])
    email_address = StringField(label='Email Address:',validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password:',validators= [Length(min = 6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')

class LoginForm(FlaskForm):
	username = StringField(label='User Name:', validators=[DataRequired()])
	password = PasswordField(label='Password:', validators=[DataRequired()])
	submit = SubmitField(label='Sign In')

class EmailForm(FlaskForm):
    email_address = StringField(label='Email Address:',validators=[Email(), DataRequired()])
    submit = SubmitField(label='Submit')
    
class ChangePasswordForm(FlaskForm):
    """docstring for ChangePasswordForm"""
    password_old = PasswordField('Enter Old Password', validators=[DataRequired()])
    password_new1 = PasswordField('Enter New Password', validators=[DataRequired()])
    password_new2 = PasswordField('Confirm New Password',validators=[EqualTo('password_new1'), DataRequired()])
    submit = SubmitField('Confirm Change Password')