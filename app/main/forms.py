
from app.models import *
from app.main.crud import get_roles
from flask import current_app, request
from flask_wtf import FlaskForm
from wtforms import BooleanField, FormField, IntegerField, SelectField, StringField, SubmitField, ValidationError
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Email, Length, Regexp
from wtforms_alchemy import model_form_factory
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField

play_titles = {"AWW": "All's Well That Ends Well", "Ant": "Antony and Cleopatra", "AYL": "As You Like It", "Err": "The Comedy of Errors", "Cor": "Coriolanus", "Cym": "Cymbeline", "Ham": "Hamlet", "1H4": "Henry IV, Part 1", "2H4": "Henry IV, Part 2", "H5": "Henry V", "1H6": "Henry VI, Part 1", "2H6": "Henry VI, Part 2", "3H6": "Henry VI, Part 3", "H8": "Henry VIII", "JC": "Julius Caesar", "Jn": "King John", "Lr": "King Lear", "LLL": "Love's Labor's Lost", "Mac": "Macbeth", "MM": "Measure for Measure", "MV": "The Merchant of Venice", "Wiv": "The Merry Wives of Windsor", "MND": "A Midsummer Night's Dream", "Ado": "Much Ado About Nothing", "Oth": "Othello", "Per": "Pericles", "R2": "Richard II", "R3": "Richard III", "Rom": "Romeo and Juliet", "Shr": "The Taming of the Shrew", "Tmp": "The Tempest", "Tim": "Timon of Athens", "Tit": "Titus Andronicus", "Tro": "Troilus and Cressida", "TN": "Twelfth Night", "TGV": "The Two Gentlemen of Verona", "TNK": "The Two Noble Kinsmen", "WT": "The Winter's Tale"}

BaseModelForm = model_form_factory(FlaskForm)

class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session

class OrderFormMixin(object):
    """Ordered fields are added to the end of the form."""
    """Adapted from https://gist.github.com/rombr/89d4d9db0229237f40bbd46482764918"""
    
    def __init__(self, *args, **kwargs):
        super(OrderFormMixin, self).__init__(*args, **kwargs)

        order_before = getattr(self.meta, "order_before", [])
        order_after = getattr(self.meta, "order_after", [])
        add_before = {}
        add_after = {}
        new_fields = {}
    
        if order_before:
            for field_name in order_before:
                if field_name in self._fields:
                    add_before[field_name] = self._fields[field_name]
            new_fields.update(add_before)

        if order_after:
            for field_name in order_after:
                if field_name in self._fields:
                    add_after[field_name] = self._fields[field_name]

        for field_name in self._fields:
            if field_name not in add_before and field_name not in add_after:
                new_fields[field_name] = self._fields[field_name]
                
        if add_after:
           new_fields.update(add_after)

        self._fields = new_fields


class EditProfileForm(FlaskForm):
    name = StringField("Name", validators=[Length(0, 64)])
    about = TextAreaField("About Me")
    submit = SubmitField("Submit")


class EditProfileAdminForm(ModelForm):

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


class ChoosePlayForm(FlaskForm):
    """Select Shakespeare play."""

    title_list = [(key, value) for key, value in play_titles.items()]
    play = SelectField("Play", validators=[DataRequired()], choices=title_list, default="Ham")
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


class CharacterForm(FlaskForm):
    """Form to create or edit a Character object."""

    id = StringField('ID')
    name = StringField('Name')
    gender = IntegerField("Gender")
    submit = SubmitField("Submit")






# ----- BEGIN: QUESTION FORM ----- #

def make_question_form(db_play=None, db_question=None): 
    """Create a dynamic Question form that narrows selections down by the given parameters."""
    # Parameters are given a "db_" prefix to avoid confusion with form and object field names.

    class QuestionForm(OrderFormMixin, ModelForm):
        """A dynamic Question form. Uses Question class fields as well as custom-ordered additional fields."""

        def __init__(self, db_play, db_question=None):
            super().__init__(obj=db_question)  # The parent FlaskWTForms-Alchemy ModelForm class accepts an existing database object as a form model
            self.db_play =  db_play
            self.db_question = db_question

        class Meta: # Supplies parameters to OrderFormMixin to arrange additional fields
            model = Question
            order_before = ["play"]
            order_after = ["scenes", "characters", "submit"]

        if db_question: # Used when an existing Question is used as the model object for the form
            play = QuerySelectField('Play', 
                                    query_factory=Play.query.all,
                                    default=db_question.play) # Defaults to the existing Question's play
            characters = QuerySelectMultipleField('Characters', 
                                    query_factory=Character.query.filter(Character.play_id == db_play.id).order_by(Character.id).all,
                                    default=db_question.characters) # Defaults to the existing Question's question
        else:
            play = QuerySelectField('Play', 
                                query_factory=Play.query.all,
                                default=db_play)
            characters = QuerySelectMultipleField('Characters', 
                                    query_factory=Character.query.filter(Character.play_id == db_play.id).all,
                                    default=db_question)

        scenes = QuerySelectMultipleField('Related Scenes', 
                                query_factory=Scene.query.filter(Scene.play_id == db_play.id).order_by(Scene.act, Scene.scene).all)

        submit = SubmitField("Submit")

    if db_question:
        form = QuestionForm(db_play, db_question)
    else:
        form = QuestionForm(db_play)

    return form

# ----- END: QUESTION FORM ----- #


# ----- BEGIN: INTERPRETATION FORM ----- #


def make_interpretation_form(db_interpretation=None, db_play=None, db_question=None, db_object=None): 
    """Create a dynamic Interpretation form that narrows selections down by the given parameters."""
    # Parameters are given a "db_" prefix to avoid confusion with form and object field names.

    class InterpretationForm(OrderFormMixin, ModelForm):
        """A dynamic Interpretation form. Uses Interpretation class fields as well as custom-ordered additional fields."""

        def __init__(self, db_play, db_question=None, db_object=None):
            super().__init__(obj=db_object)  # The parent FlaskWTForms-Alchemy ModelForm class accepts an existing database object as a form model
            self.db_play =  db_play
            self.db_question = db_question
            self.db_interpretation = db_interpretation

        class Meta: # Supplies parameters to OrderFormMixin to arrange additional fields
            model = Interpretation
            order_before = ["delete", "play", "question", "film"]
            order_after = ["scenes", "submit"]

        if db_interpretation: # Used when an existing Interpretation is used as the model object for the form
            play = QuerySelectField("Play", 
                                    query_factory=Play.query.all,
                                    default=db_interpretation.play) # Defaults to the existing Interpretation's play
            question = QuerySelectField("Question", 
                                    query_factory=Question.query.filter(Question.play_id == db_play.id).all,
                                    default=db_interpretation.question) # Defaults to the existing Interpretation's question

        else:
            play = QuerySelectField("Play", 
                                query_factory=Play.query.all,
                                default=db_play)
            question = QuerySelectField('Question', 
                                    query_factory=Question.query.filter(Question.play_id == db_play.id).all,
                                    default=db_question)

        delete = BooleanField(label="Delete record?")
        film = QuerySelectField('Related Film', 
                                query_factory=Film.query.filter(Film.play_id == db_play.id).all)
        scenes = QuerySelectMultipleField('Related Scenes', 
                                query_factory=Scene.query.filter(Scene.play_id == db_play.id).order_by(Scene.act, Scene.scene).all)

        submit = SubmitField("Submit")

    if db_object:
        form = InterpretationForm(db_play, db_question, db_object)
    else:
        form = InterpretationForm(db_play, db_question)

    return form

# ----- END: INTERPRETATION FORM ----- #

class SearchForm(FlaskForm):

    query = StringField("Search", validators=[DataRequired()])
    # submit = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        if "formdata" not in kwargs:
            kwargs["formdata"] = request.args
        
        #bypass Flask-WTF's CSRF validation for this form
        if "csrf_enabled" not in kwargs:
            kwargs["csrf_enabled"] = False

        super(SearchForm, self).__init__(*args, **kwargs)


class SearchFacetsForm(FlaskForm):

    character = BooleanField("Character", default="checked")
    film = BooleanField("Film", default="checked")
    interpretation = BooleanField("Interpretation", default="checked")
    job = BooleanField("Job", default="checked")
    person = BooleanField("Person", default="checked")
    play = BooleanField("Play", default="checked")
    scene = BooleanField("Scene", default="checked")
    question = BooleanField("Question", default="checked")


class AdvancedSearchForm(FlaskForm):

    search_field = FormField(SearchForm)
    search_facets = FormField(SearchFacetsForm)
    submit = SubmitField("Submit")


def make_film_form(db_film=None): 
    """Create a dynamic Film form that narrows selections down by the given parameters."""
    # Parameters are given a "db_" prefix to avoid confusion with form and object field names.

    class FilmForm(OrderFormMixin, ModelForm):
        """A dynamic Film form. Uses Film class fields as well as custom-ordered additional fields."""

        def __init__(self, db_film=None):
            super().__init__(obj=db_film)  # The parent FlaskWTForms-Alchemy ModelForm class accepts an existing database object as a form model

        class Meta: # Supplies parameters to OrderFormMixin to arrange additional fields
            model = Film
            order_before = ["delete"]
            order_after = ["submit"]

        if db_film: # Used when an existing Film is used as the model object for the form
            play = QuerySelectField("Play", 
                                    query_factory=Play.query.all,
                                    default=db_film.play) # Defaults to the existing Film's play

        else:
            play = QuerySelectField("Play", 
                                query_factory=Play.query.all,
                                default=db_film.play)

        delete = BooleanField(label="Delete record?")

        submit = SubmitField("Submit")

    if db_film:
        form = FilmForm(db_film)
    else:
        form = FilmForm()

    return form