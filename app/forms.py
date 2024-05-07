from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, DecimalField
from wtforms.validators import DataRequired, Optional


# LOGIN FORM
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    phone_number = StringField("Phone Number", validators=[Optional()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")
