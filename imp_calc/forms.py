from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from imp_calc.models import User
from imp_calc.routes import current_user
import re
#regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')

class RegisterFormA(FlaskForm):
    def validate_password(self, password1):
        if not any(char.isdigit() for char in password1.data):
            raise ValidationError('Password must contain at least one number.')
        if not any(char.isupper() for char in password1.data):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not any(char.islower() for char in password1.data):
            raise ValidationError('Password must contain at least one lowercase letter.')

    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username')

    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email Address already exists! Please try a different email address')

    def validate_password(self, password1):
        if not any(char.isdigit() for char in password1.data):
            raise ValidationError('Password must contain at least one number.')
        if not any(char.isupper() for char in password1.data):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not any(char.islower() for char in password1.data):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'[^A-Za-z0-9]', password1.data):
            raise ValidationError('Password must contain at least one special character.')

    username = StringField(label='User Name:', validators = [Length(min=1,max=30), DataRequired()])
    role = SelectField(label='Role', choices=[('a', 'Admin'), ('m', 'Manager'), ('u', 'User')])
    # role = StringField(label='Role:',validators=[DataRequired()])
    password1 = PasswordField(label='Password:',validators= [Length(min = 8), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1',message='Both passwords must be equal'),validate_password, DataRequired()])
    submit = SubmitField(label='Create Account')

class RegisterFormM(FlaskForm):

    def validate_password(self, password1):
        if not any(char.isdigit() for char in password1.data):
            raise ValidationError('Password must contain at least one number.')
        if not any(char.isupper() for char in password1.data):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not any(char.islower() for char in password1.data):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'[^A-Za-z0-9]', password1.data):
            raise ValidationError('Password must contain at least one special character.')

    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username')

    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email Address already exists! Please try a different email address')

    username = StringField(label='User Name:', validators = [Length(min=1,max=30), DataRequired()])
    role = SelectField(label='Role', choices=[('u', 'User')])
    # role = StringField(label='Role:',validators=[DataRequired()])
    password1 = PasswordField(label='Password:',validators= [Length(min = 6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1',message='Both passwords must be equal'),validate_password, DataRequired()])
    submit = SubmitField(label='Create Account')

class UpdateFormA(FlaskForm):

    def validate_password(self, password1):
        if not any(char.isdigit() for char in password1.data):
            raise ValidationError('Password must contain at least one number.')
        if not any(char.isupper() for char in password1.data):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not any(char.islower() for char in password1.data):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'[^A-Za-z0-9]', password1.data):
            raise ValidationError('Password must contain at least one special character.')


    username = StringField(label='User Name:', validators = [Length(min=1,max=30), DataRequired()])
    is_activate = BooleanField(label='Is Active:', default=True)
    role = SelectField(label='Role', choices=[('a', 'Admin'), ('m', 'Manager'), ('u', 'User')])
    password1 = PasswordField(label='Password:',validators= [validate_password,Length(min = 6), DataRequired()])
    submit = SubmitField(label='Update Account')

class UpdateFormM(FlaskForm):

    def validate_password(self, password1):
        if not any(char.isdigit() for char in password1.data):
            raise ValidationError('Password must contain at least one number.')
        if not any(char.isupper() for char in password1.data):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not any(char.islower() for char in password1.data):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'[^A-Za-z0-9]', password1.data):
            raise ValidationError('Password must contain at least one special character.')

    username = StringField(label='User Name:', validators = [Length(min=1,max=30), DataRequired()])
    is_activate = BooleanField(label='Is Active:', default=True, false_values=('', 0, '0'))
    role = SelectField(label='Role', choices=[('u', 'User')])
    password1 = PasswordField(label='Password:',validators= [validate_password,Length(min = 6), DataRequired()])
    submit = SubmitField(label='Update Account')

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