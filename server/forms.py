"""All forms"""

from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField
from wtforms.validators import InputRequired, NumberRange, Optional, URL, Length


class RewriteForm(FlaskForm):
    """Form for submitting a rewrite to the server"""

    text = StringField(
        "Change it to:",
        validators=[InputRequired(), Length(min=4, max=500)],
        render_kw={"placeholder": "Something overdramatic happened"},
    )


class LoginForm(FlaskForm):
    """Form for logging in"""

    username = StringField(
        "Username",
        validators=[InputRequired()],
        render_kw={"placeholder": "Enter your username or email"},
    )

    password = PasswordField(
        "Password",
        validators=[InputRequired()],
        render_kw={"placeholder": "Enter your password"},
    )


class SignupForm(FlaskForm):
    """Form for signing up"""

    username = StringField(
        "Username",
        validators=[InputRequired(), Length(min=3, max=50)],
        render_kw={"placeholder": "Enter a new username"},
    )

    email = EmailField(
        "Email",
        validators=[InputRequired()],
        render_kw={"placeholder": "Enter your email"},
    )

    password = PasswordField(
        "Password",
        validators=[InputRequired()],
        render_kw={"placeholder": "Enter a password"},
    )
