from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from app import app
from models import User


class LoginForm(FlaskForm):
    username = StringField('Username ', validators=[DataRequired()])
    password = PasswordField('Password ', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign in')


def get_choices():
    answer = []

    for key in app.config['NEWS_WEBSITES'].keys():
        answer.append([key, key])

    return answer


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class EditForm(FlaskForm):
    changePassword = BooleanField('Check this if you want to change your password')
    newsTopic = SelectField('News Topic', choices=get_choices())
    submitChanges = SubmitField("Submit changes")

class ForgottenPassword(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    newPassword = PasswordField('New Password', validators=[DataRequired()])
    submitPassword = SubmitField('Submit password')


class ConfirmPassForm(FlaskForm):
    currentPassword = PasswordField("Current password", validators=[DataRequired()])
    newPassword = PasswordField("New password", validators=[DataRequired()])
    newPassword2 = PasswordField("Repeat new password",
                                 validators=[DataRequired(), EqualTo('newPassword',
                                                                     message='Must be equal to your new password.')])
    submitPassword = SubmitField("Submit password")
