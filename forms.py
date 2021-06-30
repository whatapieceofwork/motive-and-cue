from flask_wtf import FlaskForm
from wtforms import validators, StringField, FormField, FieldList, IntegerField, Form, ValidationError, PasswordField, BooleanField, SubmitField
from wtforms.fields.core import IntegerField, SelectField, SelectMultipleField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, Optional
from wtforms_sqlalchemy.orm import model_form
from werkzeug.datastructures import MultiDict



play_titles = {"AWW": "All's Well That Ends Well", "Ant": "Antony and Cleopatra", "AYL": "As You Like It", "Err": "The Comedy of Errors", "Cor": "Coriolanus", "Cym": "Cymbeline", "Ham": "Hamlet", "1H4": "Henry IV, Part 1", "2H4": "Henry IV, Part 2", "H5": "Henry V", "1H6": "Henry VI, Part 1", "2H6": "Henry VI, Part 2", "3H6": "Henry VI, Part 3", "H8": "Henry VIII", "JC": "Julius Caesar", "Jn": "King John", "Lr": "King Lear", "LLL": "Love's Labor's Lost", "Mac": "Macbeth", "MM": "Measure for Measure", "MV": "The Merchant of Venice", "Wiv": "The Merry Wives of Windsor", "MND": "A Midsummer Night's Dream", "Ado": "Much Ado About Nothing", "Oth": "Othello", "Per": "Pericles", "R2": "Richard II", "R3": "Richard III", "Rom": "Romeo and Juliet", "Shr": "The Taming of the Shrew", "Tmp": "The Tempest", "Tim": "Timon of Athens", "Tit": "Titus Andronicus", "Tro": "Troilus and Cressida", "TN": "Twelfth Night", "TGV": "The Two Gentlemen of Verona", "TNK": "The Two Noble Kinsmen", "WT": "The Winter's Tale"}


class LoginForm(FlaskForm):
    """Log in user."""

    email = StringField("Email", validators=[DataRequired(), Length(6, 60), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Log in")


class RegistrationForm(FlaskForm):
    """Allow user to register account."""

    email = StringField("Email", validators=[DataRequired(), Length(6, 60), Email()])
    username = StringField("Username", validators=[DataRequired(), Length(3, 60),
                            Regexp("^[A-Za-z][A-Za-z0-9_]*$", 0,
                            "Usernames can only include letters, numbers, and underscores.")])
    password = PasswordField("Password", validators=[DataRequired(), EqualTo("password2", message="Passwords must match.")])
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        email = field.data
        if user_email_taken(email):
            raise ValidationError("That email is already in use.")

    def validate_username(self, field):
        username = field.data
        if username_taken(username):
            raise ValidationError("Username already taken.")


class ChoosePlayForm(FlaskForm):
    """Select Shakespeare play."""

    title_list = [(key, value) for key, value in play_titles.items()]
    play = SelectField("Play", validators=[DataRequired()], choices=title_list, default="Ham")
    submit = SubmitField("Submit")


class CreateChoiceForm(FlaskForm):
    """Create a new Choice. Requires scene and character lists to be passed in when form is instantiated."""

    title = StringField("Title", validators=[DataRequired(), Length(1, 100)])
    desc = TextAreaField("Description", validators=[DataRequired(), Length(1, 1000)])
    quote = TextAreaField("Quote", validators=[Length(1, 1000)])
    scenes = SelectMultipleField("Related Scenes", coerce=int)
    characters = SelectMultipleField("Related Characters", coerce=int)
    submit = SubmitField("Submit")


class SceneForm(FlaskForm):
    """Edit the scene list for a play. Requires a list of scene numbers to be passed in when form is instantiated."""

    id = IntegerField("ID")
    act = IntegerField("Act", validators=[DataRequired(), Length(1, 3)])
    scene = IntegerField("Scene", validators=[DataRequired(), Length(1, 3)])
    title = StringField("Title", validators=[Length(1, 100)])
    description = TextAreaField("Description", validators=[Length(1, 1000)])
    quote = TextAreaField("Quote", validators=[Length(1, 1000)])
    submit = SubmitField("Submit")


class InterpretationForm(FlaskForm):
    """Form to create or edit an Interpretation object."""

    id = IntegerField("ID")
    act = IntegerField("Act", validators=[DataRequired(), Length(1, 3)])
    scene = IntegerField("Scene", validators=[DataRequired(), Length(1, 3)])
    title = StringField("Title", validators=[Length(1, 100)])
    description = TextAreaField("Description", validators=[Length(1, 1000)])
    quote = TextAreaField("Quote", validators=[Length(1, 1000)])
    submit = SubmitField("Submit")


# class ChoiceForm(FlaskForm):
#     """Form to create or edit a Choice object."""

#     id = IntegerField("ID")
#     title = StringField("Title", validators=[Length(1, 100)])
#     description = TextAreaField("Description", validators=[Length(1, 1000)])
#     submit = SubmitField("Submit")


class CharacterForm(FlaskForm):
    """Form to create or edit a Character object."""

    id = StringField('ID')
    name = StringField('Name')
    gender = IntegerField("Gender")
    submit = SubmitField("Submit")
