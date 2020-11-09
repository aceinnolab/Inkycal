from flask_wtf import FlaskForm
from wtforms import BooleanField

#from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
#from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    #username = StringField('api-key', validators=[DataRequired()])
    #modules = SelectField(u'modules', choices = [(_[0], _[1]) for _ in modules])
    remember_me = BooleanField('Show info section')
    #submit = SubmitField('Sign In')
