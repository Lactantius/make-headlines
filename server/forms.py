"""All forms"""

from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField
from wtforms.validators import InputRequired, NumberRange, Optional, URL, Length


class RewriteForm(FlaskForm):
    """Form for submitting a rewrite to the server"""

    text = StringField(
        "Change it to:", validators=[InputRequired(), Length(min=1, max=500)]
    )


class LoginForm(FlaskForm):
    """Form for logging in"""

    username = StringField("Username", validators=[InputRequired()])

    password = PasswordField("Password", validators=[InputRequired()])


class SignupForm(FlaskForm):
    """Form for signing up"""

    username = StringField(
        "Username", validators=[InputRequired(), Length(min=3, max=50)]
    )

    email = EmailField("Email", validators=[InputRequired()])

    password = PasswordField("Password", validators=[InputRequired()])
