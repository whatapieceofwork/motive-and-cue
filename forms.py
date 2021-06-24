from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import validators
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
import crud

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(6, 60), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Log in")

class RegistrationForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(6, 60), Email()])
    username = StringField("Username", validators=[DataRequired(), Length(3, 60),
                            Regexp("^[A-Za-z][A-Za-z0-9_]*$", 0,
                            "Usernames can only include letters, numbers, and underscores.")])
    password = PasswordField("Password", validators=[DataRequired(), EqualTo("password2", message="Passwords must match.")])
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        email = field.data
        if crud.user_email_taken(email):
            raise ValidationError("That email is already in use.")

    def validate_username(self, field):
        username = field.data
        if crud.username_taken(username):
            raise ValidationError("Username already taken.")
