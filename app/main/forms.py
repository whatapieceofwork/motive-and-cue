
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp
from wtforms import ValidationError
from ..models import User, Role
import re

class EditProfileForm(FlaskForm):
    name = StringField("Name", validators=[Length(0, 64)])
    about = TextAreaField("About Me")
    submit = SubmitField("Submit")


class EditProfileAdminForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField("Username", validators=[DataRequired(), Length(1, 64),
                                                    Regexp("^[A-Za-z][A-za-z0-9_]*$", 0,
                                                    "Usernames must have only letters, numbers, and underscores.")])
    confirmed = BooleanField("Confirmed")
    role = SelectField("Role", coerce=int)
    name = StringField("Name", validators=[Length(0, 64)])
    about = TextAreaField("About")
    submit = SubmitField("Submit")

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user
    
    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter(User.email == field.data).first():
            raise ValidationError("Email already registered.")

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter(User.username == field.data).first():
            raise ValidationError("Username already in use.")