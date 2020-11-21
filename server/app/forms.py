from flask_wtf import FlaskForm
from wtforms import BooleanField

class LoginForm(FlaskForm):
  remember_me = BooleanField('Show info section')

