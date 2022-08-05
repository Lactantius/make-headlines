"""All forms"""

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired, NumberRange, Optional, URL, Length


class RewriteForm(FlaskForm):
    """Form for submitting a rewrite to the server"""

    text = StringField(
        "New Headline", validators=[InputRequired(), Length(min=1, max=500)]
    )
