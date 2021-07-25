from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp
from wtforms import ValidationError
from ..models import User
import re

class LoginForm(FlaskForm):
    """Form for user log-in."""

    email = StringField("Email", validators=[DataRequired(), Length(5, 64), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Log In")


class RegistrationForm(FlaskForm):
    """Form for user registration."""

    email = StringField("Email", validators=[DataRequired(), Length(5, 64), Email("Please enter a valid email address.")])
    username = StringField("Username", validators=[DataRequired(), Length(1, 64),
                                                    Regexp("^[A-Za-z][A-za-z0-9_]*$", 0,
                                                    "Usernames must have only letters, numbers, and underscores.")])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, message="Password must be between 6 and 64 characters long."), EqualTo("password2", message="Passwords must match.")])
    password2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Register Account")

    def validate_email(self, field):
        if User.query.filter(User.email == field.data).first():
            raise ValidationError("Email already registered.")

    def validate_password(self, field):
        password = field.data
        if (not re.search("[a-z]", password) or not re.search("A-Z", password)) and not re.search("[0-9]", password):
            raise ValidationError("Passwords must include both letters and numbers.")
        
    def validate_username(self, field):
        if User.query.filter(User.username == field.data).first():
            raise ValidationError("Username already in use.")


class RequestPasswordResetForm(FlaskForm):
    """Form for user to request a password reset email."""

    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    """Form for user to reset their password."""

    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, message="Password must be between 6 and 64 characters long."), EqualTo("password2", message="Passwords must match.")])
    password2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Register Account")

    def validate_password(self, field):
        password = field.data
        if (not re.search("[a-z]", password) or not re.search("A-Z", password)) and not re.search("[0-9]", password):
            raise ValidationError("Passwords must include both letters and numbers.")