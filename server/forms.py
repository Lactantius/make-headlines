"""All forms"""

from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField
from wtforms.validators import (
    EqualTo,
    InputRequired,
    NumberRange,
    Optional,
    URL,
    Length,
)


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
        validators=[InputRequired(), Length(min=10)],
        render_kw={"placeholder": "Enter a password"},
    )


class ProfileEditForm(FlaskForm):
    """Form for signing up"""

    username = StringField(
        "Username", validators=[InputRequired(), Length(min=3, max=50)]
    )

    email = EmailField("Email", validators=[InputRequired()])

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[InputRequired()],
        render_kw={"placeholder": "Confirm your password"},
    )


class ChangePasswordForm(FlaskForm):
    """Form for changing passwords"""

    current = PasswordField(
        "Current Password",
        validators=[InputRequired()],
        render_kw={"placeholder": "Enter your current password"},
    )

    new = PasswordField(
        "New Password",
        validators=[InputRequired(), Length(min=10)],
        render_kw={"placeholder": "Enter a new password"},
    )

    confirm = PasswordField(
        "Confirm Password",
        validators=[
            InputRequired(),
            Length(min=10),
            EqualTo("new", message="Passwords must match"),
        ],
        render_kw={"placeholder": "Repeat the new password"},
    )
