
from bs4 import BeautifulSoup
from datetime import datetime
from flask import Flask, render_template, redirect, flash, session, request, url_for, jsonify
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_required, set_login_view
from flask_login.utils import login_user, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.utils import parse_version
from marshmallow import Schema, fields
from sqlalchemy.orm.session import object_session
from sqlalchemy.sql import exists
from werkzeug.security import generate_password_hash, check_password_hash
import jinja2
import json
import os
import requests
from data_models import *
from data_schemas import *
from crud import *
from folger_parser import *
from moviedb_parser import *
from seed import *
from collections import namedtuple, OrderedDict


FLASK_KEY = os.environ["FLASK_KEY"]
MOVIEDB_API_KEY = os.environ["MOVIEDB_API_KEY"]
db = SQLAlchemy()

app = Flask(__name__)
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True
app.config['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_POOL_RECYCLE'] = 54000  # Recycle connection pool every 15 minutes 
app.config['SQLALCHEMY_POOL_SIZE'] = 10
app.secret_key = FLASK_KEY

Bootstrap(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
def index():
    """Display index page."""

    return render_template("index.html")


@app.route("/login/", methods=["GET", "POST"])
def login():
    """Prompt the user to log in."""

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get("next")
            if not next or not next.startswith("/"):
                next = ("/")
            return redirect(next)
        else:
            flash("Invalid username or password. Please try again.")
            return render_template("login.html", form=form)

    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    """Log out a logged-in user."""

    logout_user()
    flash("You have been logged out. Thanks for visiting!")
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user."""

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Thank you for registering! Please log in.")
        return redirect("/login/")
    return render_template("register.html", 
                            form=form)


@app.route("/my-account")
@login_required
def my_account():
    """Display account information for logged-in users."""

    return render_template("my-account.html", 
                            user=current_user)


@app.route("/choose-play")
def choose_play():
    """Prompts user for play name, passes play name to appropriate function. Will be deprecated."""
    form = ChoosePlayForm()

    return render_template("choose-play.html", 
                            form=form, 
                            play_titles = play_titles)


# ----- BEGIN: SCENE VIEWS ----- #

@app.route("/scenes/", methods=["GET", "POST"])
@app.route("/scenes/<string:shortname>/", methods=["GET", "POST"])
@app.route("/scenes/<int:id>/", methods=["GET", "POST"])
def view_scenes(shortname=None, id=None):
    """Display all scenes, scenes by play shortname, or a specific scene by scene id. Prompt for play if not given in URL."""

    if shortname:
        if shortname not in play_titles.keys():
            flash("Please select a valid play.")
            return redirect("/scenes/")
        play = get_play_by_shortname(shortname)
        scenes = get_all_scenes_by_play(play)
        return render_template("scenes-view.html", play=play, scenes=scenes)

    elif id:
        scene = Scene.query.get(id)
        return render_template("scene.html", scene=scene)

    form = ChoosePlayForm()
    if form.validate_on_submit():
        shortname = form.play.data
        if shortname not in play_titles.keys():
            flash("Please select a valid play.")
        
        play = get_play_by_shortname(shortname)

        return redirect(f"/scenes/{shortname}/")

    return render_template("scenes-view.html", 
                            form=form)


@app.route("/scenes/add/", methods=["GET", "POST"])
@app.route("/scenes/add/<string:shortname>/", methods=["GET", "POST"])
def add_scenes(shortname=None):
    """Add scenes by play shortname using Folger scene information. Prompt for play if not given in URL."""

    if shortname:
        play = get_play_by_shortname(shortname)
        if not type(play) == Play:
            flash("Please select a valid play.")
            return redirect("/scenes/add/")
        scenes = parse_folger_scene_descriptions(play)
        return render_template("scenes-edit.html", 
                                play=play, 
                                scenes=scenes)

    form = ChoosePlayForm()
    if form.validate_on_submit():
        shortname = form.play.data
        return redirect(f"/scenes/add/{shortname}/")

    return render_template("scenes-edit.html", 
                            form=form)


@app.route("/scenes/edit/", methods=["GET", "POST"])
@app.route("/scenes/edit/<string:shortname>/", methods=["GET", "POST"])
@app.route("/scenes/edit/<int:id>/", methods=["GET", "POST"])
def edit_scenes(shortname=None, id=None):
    """Edit all scenes by play shortname, or a specific scene by scene id. Prompt for play if not given in URL."""

    if shortname and request.method == "POST": # If the user submitted scene information related to a given play, proces that information
        play = get_play_by_shortname(shortname)
        if not type(play) == Play:
            flash("Please select a valid play.")
            return redirect("/scenes/edit/")
        scene_count = request.form.get("scene_count")
        scene_count = int(scene_count) + 1

        for i in range(scene_count):
            scene_id = request.form.get(f"id-{i}")
            act_num = request.form.get(f"act-{i}")
            scene_num = request.form.get(f"scene-{i}")
            title = request.form.get(f"title-{i}")
            description = request.form.get(f"description-{i}")
            quote = request.form.get(f"quote-{i}")
            quote_character = request.form.get(f"quote-character-{i}")
            if quote_character:
                character = Character.query.get(quote_character)
            
            existing_scene = Scene.query.get(scene_id)
            if existing_scene:
                scene = update_scene(scene=existing_scene, title=title, description=description)
            else:
                scene = add_scene(act=act_num, scene=scene_num, play=play, title=title, description=description)

            if quote and quote_character:
                add_quote(play=play, character=character, scene=scene, text=quote)

        return redirect(f"/scenes/{shortname}/")

    elif shortname: # Edit all scenes for a given play
        play = get_play_by_shortname(shortname)
        if not type(play) == Play:
            flash("Please select a valid play.")
            return redirect("/scenes/")

        existing_scenes = Scene.query.all()
        if existing_scenes:
            scenes = get_all_scenes_by_play(play)
        else:
            scenes = parse_folger_scene_descriptions(play)

        characters = get_all_characters_by_play(play)

        return render_template("scenes-edit.html", 
                                play=play, 
                                scenes=scenes,
                                characters=characters)
    
    elif id: # Edit a single scene
        scene = Scene.query.get(id)
        form = SceneForm(obj=scene)

        if form.is_submitted():
            scene.title = form.title.data
            scene.description = form.description.data
            db.session.merge(scene)
            db.session.commit()

            return redirect(f"/scenes/{id}/")
    
        return render_template("scenes-edit.html",
                                scene=scene,
                                form=form)

    else: # Choose a play to edit scenes for
        form = ChoosePlayForm()
        if form.validate_on_submit():
            shortname = form.play.data
            return redirect(f"/scenes/edit/{shortname}/")

    return render_template("choose-play.html", 
                    form=form)

# ----- END: SCENE VIEWS ----- #


# ----- BEGIN: CHARACTER VIEWS ----- #

@app.route("/characters/", methods=["GET", "POST"])
@app.route("/characters/<string:shortname>/", methods=["GET", "POST"])
@app.route("/characters/<int:id>/", methods=["GET", "POST"])
def view_characters(shortname=None, id=None):
    """Display all characters, characters by play shortname, or a specific character by character id. Prompt for play if not given in URL."""

    if shortname:
        play = get_play_by_shortname(shortname)
        if not type(play) == Play:
            flash("Please select a valid play.")
            return redirect("/characters/")
        characters = get_all_characters_by_play(play)
        return render_template("characters-view.html", play=play, characters=characters)
        
    elif id:
        character = Character.query.get(id)
        return render_template("character.html", character=character)

    form = ChoosePlayForm()
    if form.validate_on_submit():
        shortname = form.play.data
        play = get_play_by_shortname(shortname)
        if not type(play) == Play:
            flash("Please select a valid play.")
            return redirect("/characters/")

        return redirect(f"/characters/{shortname}/")

    return render_template("characters-view.html", 
                            form=form)


@app.route("/characters/add/", methods=["GET", "POST"])
@app.route("/characters/add/<string:shortname>/", methods=["GET", "POST"])
def add_characters(shortname=None):
    """Add characters by play shortname using Folger character information. Prompt for play if not given in URL."""

    if shortname:
        play = get_play_by_shortname(shortname)
        if not type(play) == Play:
            flash("Please select a valid play.")
            return redirect("/characters/add/")
        characters = get_all_characters_by_play(play)
        scenes = get_all_scenes_by_play(play)
        return render_template("characters-edit.html", 
                                play=play, 
                                characters=characters,
                                genders=GENDERS,
                                scenes=scenes)

    form = ChoosePlayForm()
    if form.validate_on_submit():
        shortname = form.play.data
        return redirect(f"/characters/add/{shortname}/")

    return render_template("choose-play.html", 
                            form=form)


@app.route("/characters/edit/", methods=["GET", "POST"])
@app.route("/characters/edit/<string:shortname>/", methods=["GET", "POST"])
@app.route("/characters/edit/<int:id>/", methods=["GET", "POST"])
def edit_characters(shortname=None, id=None):
    """Edit all characters by play shortname, or a specific character by character id."""

    if shortname and request.method == "POST": # If the user submitted character information related to a given play, proces that information
        play = get_play_by_shortname(shortname)
        character_count = request.form.get("character_count")
        character_count = int(character_count) + 1
    
        for i in range(character_count):
            character_id = request.form.get(f"id-{i}")
            name = request.form.get(f"name-{i}")
            gender = request.form.get(f"gender-{i}")
            quote = request.form.get(f"quote-{i}")
            quote_scene = request.form.get(f"quote-scene-{i}")
            scene = Scene.query.get(quote_scene)

            existing_character = Character.query.get(character_id)
            if existing_character:
                character = update_character(character=existing_character, name=name, gender=gender)
            else:
                character = add_character(name=name, play=play, gender=gender)

            if quote and scene:
                add_quote(play=play, character=character, scene=scene, text=quote)

        return redirect(f"/characters/{shortname}/")

    elif shortname:
        play = get_play_by_shortname(shortname)
        if not type(play) == Play:
            flash("Please select a valid play.")
            return redirect("/characters/edit/")

        characters = get_all_characters_by_play(play)
        scenes = get_all_scenes_by_play(play)

        return render_template("characters-edit.html", 
                                play=play, 
                                scenes=scenes,
                                characters=characters,
                                genders=GENDERS)
    
    elif id:
        character = Character.query.get(id)
        form = CharacterForm(obj=character)

        if form.is_submitted():
            character.name = form.name.data
            character.gender = form.gender.data
            db.session.merge(character)
            db.session.commit()

            return redirect(f"/characters/{id}/")
    
        return render_template("characters-edit.html",
                                character=character,
                                form=form)

    else:
        form = ChoosePlayForm()
        if form.validate_on_submit():
            shortname = form.play.data
            return redirect(f"/characters/edit/{shortname}/")

    return render_template("characters-edit.html", 
                    form=form)

# ----- END: CHARACTER VIEWS ----- #


# ----- BEGIN: CHOICE FORM ----- #

def make_choice_form(db_play=None, db_choice=None): 
    """Create a dynamic Choice form that narrows selections down by the given parameters."""
    # Parameters are given a "db_" prefix to avoid confusion with form and object field names.

    class ChoiceForm(OrderFormMixin, ModelForm):
        """A dynamic Choice form. Uses Choice class fields as well as custom-ordered additional fields."""

        def __init__(self, db_play, db_choice=None):
            super().__init__(obj=db_choice)  # The parent FlaskWTForms-Alchemy form class accepts an existing database object as a form model
            self.db_play =  db_play
            self.db_choice = db_choice

        class Meta: # Supplies paramters to OrderFormMixin to arrange additional fields
            model = Choice
            order_before = ["play"]
            order_after = ["scenes", "characters", "submit"]

        if db_choice: # Used when an existing Choice is used as the model object for the form
            play = QuerySelectField('Play', 
                                    query_factory=Play.query.all,
                                    default=db_choice.play) # Defaults to the existing Choice's play
            characters = QuerySelectMultipleField('Characters', 
                                    query_factory=Character.query.filter(Character.play_id == db_play.id).order_by(Character.id).all,
                                    default=db_choice.characters) # Defaults to the existing Choice's choice
        else:
            play = QuerySelectField('Play', 
                                query_factory=Play.query.all,
                                default=db_play)
            characters = QuerySelectMultipleField('Characters', 
                                    query_factory=Character.query.filter(Character.play_id == db_play.id).all,
                                    default=db_choice)

        scenes = QuerySelectMultipleField('Related Scenes', 
                                query_factory=Scene.query.filter(Scene.play_id == db_play.id).order_by(Scene.act, Scene.scene).all)

        submit = SubmitField("Submit")

    if db_choice:
        form = ChoiceForm(db_play, db_choice)
    else:
        form = ChoiceForm(db_play)

    return form

# ----- END: CHOICE FORM ----- #

# ----- BEGIN: CHOICE VIEWS ----- #

@app.route("/choices/", methods=["GET", "POST"])
@app.route("/choices/<string:shortname>/", methods=["GET", "POST"])
@app.route("/choices/<int:id>/", methods=["GET", "POST"])
def view_choices(shortname=None, id=None):
    """Display all choices, choices by play shortname, or a specific choice by choice id. Prompt for play if not given in URL."""

    if shortname:
        play = get_play_by_shortname(shortname)
        if not type(play) == Play:
            flash("Please select a valid play.")
            return redirect("/choices/")
        choices = get_all_choices_by_play(play)
        return render_template("choices-view.html", play=play, choices=choices)
        
    elif id:
        choice = Choice.query.get(id)
        return render_template("choice.html", choice=choice)

    form = ChoosePlayForm()
    if form.validate_on_submit():
        shortname = form.play.data
        play = get_play_by_shortname(shortname)
        if not type(play) == Play:
            flash("Please select a valid play.")
            return redirect("/choices/")

        return redirect(f"/choices/{shortname}/")

    return render_template("choices-view.html", 
                            form=form)


@app.route("/choices/add/", methods=["GET", "POST"])
@app.route("/choices/add/<string:shortname>/", methods=["GET", "POST"])
def add_choices(shortname=None):
    """Add choices by play shortname. Prompt for play if not given in URL."""

    if shortname:
        play = get_play_by_shortname(shortname)
        if not type(play) == Play:
            flash("Please select a valid play.")
            return redirect("/choices/add/")
        
        # class ChoiceForm(OrderFormMixin, ModelForm):
        #     class Meta:
        #         model = Choice
        #         order_before = ["play"]
        #         order_after = ["characters", "scenes", "submit"]

        #     play = QuerySelectField('Related Play', 
        #                                     query_factory=Play.query.all)
        #     characters = QuerySelectMultipleField('Related Characters', 
        #                                     query_factory=Character.query.order_by(Character.id).all)
        #     scenes = QuerySelectMultipleField('Related Scenes', 
        #                                     query_factory=Scene.query.order_by(Scene.act, Scene.scene).all)
        #     submit = SubmitField("Submit")

        # form = ChoiceForm()

        form = make_choice_form(db_play=play)

        if form.is_submitted():
            title = form.title.data
            description = form.description.data
            db_characters = form.characters.data
            db_scenes = form.scenes.data

            choice = add_choice(play=play, title=title, description=description)
            for character in db_characters:
                get_choice_character(choice=choice, character=character)
            for scene in db_scenes:
                get_choice_scene(choice=choice, scene=scene)

            return redirect(f"/choices/{choice.id}/")

        choices = get_all_choices_by_play(play)
        scenes = get_all_scenes_by_play(play)
        characters = get_all_characters_by_play(play)
        return render_template("choices-edit.html", 
                                form=form,
                                play=play, 
                                choices=choices,
                                characters=characters,
                                scenes=scenes)

    form = ChoosePlayForm()
    if form.validate_on_submit():
        shortname = form.play.data
        return redirect(f"/choices/add/{shortname}/")

    return render_template("choose-play.html", 
                            form=form)


@app.route("/choices/edit/", methods=["GET", "POST"])
@app.route("/choices/edit/<string:shortname>/", methods=["GET", "POST"])
@app.route("/choices/edit/<int:id>/", methods=["GET", "POST"])
def edit_choices(shortname=None, id=None):
    """Edit all choices by play shortname, or a specific choice by choice id."""

    if shortname:
        play = get_play_by_shortname(shortname)
        if not type(play) == Play:
            flash("Please select a valid play.")
            return redirect("/choices/edit/")

        choices = get_all_choices_by_play(play)

        return render_template("/choices-edit.html", 
                                choices=choices,
                                play=play)
    
    elif id:
        choice = Choice.query.get(id)
        play = choice.play
        form = make_choice_form(db_play=play, db_choice=choice)

        if form.is_submitted():
            play = form.play.data
            title = form.title.data
            description = form.description.data
            db_characters = form.characters.data
            db_scenes = form.scenes.data

            existing_choice = Choice.query.get(choice.id)
            if existing_choice:
                choice = update_choice(choice=existing_choice, title=title, description=description)
            else:
               choice = add_choice(play=play, title=title, description=description)

            for character in db_characters:
                get_interpretation_character(interpretation=interpretation, character=character)
            for scene in db_scenes:
                get_choice_scene(choice=choice, scene=scene)

            return redirect(f"/choices/{id}/")

        return render_template("choices-edit.html",
                                choice=choice,
                                form=form)

    form = ChoosePlayForm()
    if form.validate_on_submit():
        shortname = form.play.data
        return redirect(f"/choices/edit/{shortname}/")

    return render_template("choices-edit.html", 
                    form=form)

# ----- END: CHOICE VIEWS ----- #


# ----- BEGIN: INTERPRETATION FORM ----- #

def make_interpretation_form(db_interpretation=None, db_play=None, db_choice=None, db_object=None): 
    """Create a dynamic Interpretation form that narrows selections down by the given parameters."""
    # Parameters are given a "db_" prefix to avoid confusion with form and object field names.

    class InterpretationForm(OrderFormMixin, ModelForm):
        """A dynamic Interpretation form. Uses Interpretation class fields as well as custom-ordered additional fields."""

        def __init__(self, db_play, db_choice=None, db_object=None):
            super().__init__(obj=db_object)  # The parent FlaskWTForms-Alchemy form class accepts an existing database object as a form model
            self.db_play =  db_play
            self.db_choice = db_choice
            self.db_interpretation = db_interpretation

        class Meta: # Supplies paramters to OrderFormMixin to arrange additional fields
            model = Interpretation
            order_before = ["delete", "play", "choice", "film"]
            order_after = ["scenes", "submit"]

        if db_interpretation: # Used when an existing Interpretation is used as the model object for the form
            play = QuerySelectField('Play', 
                                    query_factory=Play.query.all,
                                    default=db_interpretation.play) # Defaults to the existing Interpretation's play
            choice = QuerySelectField('Choice', 
                                    query_factory=Choice.query.filter(Choice.play_id == db_play.id).all,
                                    default=db_interpretation.choice) # Defaults to the existing Interpretation's choice

        else:
            play = QuerySelectField('Play', 
                                query_factory=Play.query.all,
                                default=db_play)
            choice = QuerySelectField('Choice', 
                                    query_factory=Choice.query.filter(Choice.play_id == db_play.id).all,
                                    default=db_choice)

        delete = BooleanField(label="Delete record?")
        film = QuerySelectField('Related Film', 
                                query_factory=Film.query.filter(Film.play_id == db_play.id).all)
        scenes = QuerySelectMultipleField('Related Scenes', 
                                query_factory=Scene.query.filter(Scene.play_id == db_play.id).order_by(Scene.act, Scene.scene).all)

        submit = SubmitField("Submit")

    if db_object:
        form = InterpretationForm(db_play, db_choice, db_object)
    else:
        form = InterpretationForm(db_play, db_choice)

    return form

# ----- END: INTERPRETATION FORM ----- #

# ----- BEGIN: INTERPRETATION VIEWS ----- #

@app.route("/interpretations/", methods=["GET", "POST"])
@app.route("/interpretations/<string:shortname>/", methods=["GET", "POST"])
@app.route("/interpretations/<int:id>/", methods=["GET", "POST"])
def view_interpretations(shortname=None, id=None):
    """Display all interpretations, interpretations by play shortname, or a specific interpretation by interpretation id. Prompt for play if not given in URL."""

    if shortname:
        play = get_play_by_shortname(shortname)
        if not type(play) == Play:
            flash("Please select a valid play.")
            return redirect("/interpretations/")
        interpretations = get_all_interpretations_by_play(play)
        return render_template("interpretations-view.html", play=play, interpretations=interpretations)
        
    elif id:
        interpretation = Interpretation.query.get(id)
        return render_template("interpretation.html", interpretation=interpretation)

    form = ChoosePlayForm()
    if form.validate_on_submit():
        shortname = form.play.data
        play = get_play_by_shortname(shortname)
        if not type(play) == Play:
            flash("Please select a valid play.")
            return redirect("/interpretations/")

        return redirect(f"/interpretations/{shortname}/")

    return render_template("interpretations-view.html", 
                            form=form)


@app.route("/interpretations/add/", methods=["GET", "POST"])
@app.route("/interpretations/add/<string:shortname>/", methods=["GET", "POST"])
@app.route("/interpretations/add/<int:choice_id>/", methods=["GET", "POST"])
def add_interpretations(shortname=None, choice_id=None):
    """Add interpretations by play shortname or by related Choice ID. Prompt for play if not given in URL."""

    if shortname or choice_id: 
        if shortname:
            play = get_play_by_shortname(shortname)
            if not type(play) == Play:
                flash("Please select a valid play.")
                return redirect("/interpretations/add/")
            form = make_interpretation_form(db_play=play)

        if choice_id:
            choice = Choice.query.get(choice_id)
            play = choice.play
            shortname = choice.play.shortname
            if not type(play) == Play:
                flash("Please select a valid play.")
                return redirect("/interpretations/add/")
            form = make_interpretation_form(db_play=play, db_choice=choice)              
        
        if form.is_submitted():
            film = form.film.data
            title = form.title.data
            description = form.description.data
            time_start = form.time_start.data
            time_end = form.time_end.data  
            choice = form.choice.data
 
            interpretation = add_interpretation(choice=choice, play=play, film=film, title=title, description=description, time_start=time_start, time_end=time_end)

            return redirect(f"/interpretations/{interpretation.id}/")

    else:
        form = ChoosePlayForm()
        if form.validate_on_submit():
            shortname = form.play.data
            return redirect(f"/interpretations/add/{shortname}/")

    return render_template("interpretations-edit.html",
                                    form=form) 


@app.route("/interpretations/edit/", methods=["GET", "POST"])
@app.route("/interpretations/edit/<string:shortname>/", methods=["GET", "POST"])
@app.route("/interpretations/edit/<int:id>/", methods=["GET", "POST"])
def edit_interpretations(shortname=None, id=None):
    """Edit all interpretations by play shortname, or a specific interpretation by interpretation id."""

    if shortname:
        play = get_play_by_shortname(shortname)
        interpretations = get_all_interpretations_by_play(play)

        return render_template("/interpretations-edit.html", 
                                interpretations=interpretations,
                                play=play)

    elif id:
        interpretation = Interpretation.query.get(id)
        form = make_interpretation_form(db_interpretation=interpretation, db_play=interpretation.play, db_choice=interpretation.choice, db_object=interpretation)

        if form.is_submitted():
            play = form.play.data
            choice = form.choice.data
            film = form.film.data
            title = form.title.data
            description = form.description.data
            time_start = form.time_start.data
            time_end = form.time_end.data

            existing_interpretation = Interpretation.query.get(interpretation.id)
            if existing_interpretation:
                interpretation = update_interpretation(interpretation=existing_interpretation, play=play, film=film, title=title, description=description, time_start=time_start, time_end=time_end)
            else:
               interpretation = add_interpretation(choice=choice, play=play, film=film, title=title, description=description, time_start=time_start, time_end=time_end)

            return redirect(f"/interpretations/{interpretation.id}/")

    
        return render_template("interpretations-edit.html",
                                interpretation=interpretation,
                                form=form)

    form = ChoosePlayForm()
    if form.validate_on_submit():
        shortname = form.play.data
        return redirect(f"/interpretations/edit/{shortname}/")

    return render_template("interpretations-edit.html", 
                    form=form)

# ----- END: INTERPRETATION VIEWS ----- #


# ----- BEGIN: PLAY VIEWS ----- #

@app.route("/plays/", methods=["GET", "POST"])
@app.route("/plays/<string:shortname>/", methods=["GET", "POST"])
@app.route("/plays/<int:id>/", methods=["GET", "POST"])
def view_plays(shortname=None, id=None):
    """Display all plays, or a specific play by shortname or id."""

    if shortname or id:
        if shortname:
            play = get_play_by_shortname(shortname)
        elif id:
            play = Play.query.get(id)

        if not type(play) == Play:
            flash("Please select a valid play.")
            return redirect("/plays/")   
        else:
            return render_template("play.html", play=play)
        
    else:
        plays = Play.query.all()
        return render_template("plays-view.html", plays=plays)

# ----- END: PLAY VIEWS ----- #


# ----- BEGIN: FILM VIEWS ----- #

@app.route("/films/", methods=["GET", "POST"])
@app.route("/films/<string:shortname>/", methods=["GET", "POST"])
@app.route("/films/<int:id>/", methods=["GET", "POST"])
def view_films(shortname=None, id=None):
    """Display all films, films by related play shortname, or a specific film by id."""

    if shortname:
        play = get_play_by_shortname(shortname)
        if not type(play) == Play:
            flash("Please select a valid play.")
            return redirect("/films/")
        
        films = get_films_by_play(play)
        return render_template("films-view.html", films=films, play=play)

    elif id:
        film = Film.query.get(id)
        play = film.play
        parts_played = PartPlayed.query.filter(PartPlayed.film_id == film.id).all()
        hamlet_age = None
        if play.title == "Hamlet":
            hamlet = Character.query.filter(Character.name == "Hamlet").first()
            hamlet_actor = PartPlayed.query.filter((PartPlayed.film_id == film.id) & (PartPlayed.character == hamlet)).first()
            hamlet_actor = hamlet_actor.person
            hamlet_age = calculate_age_during_film(hamlet_actor, film)
        return render_template("film.html", film=film, play=play, parts_played=parts_played, hamlet_age=hamlet_age)
        
    else:
        films = Film.query.all()
        form = ChoosePlayForm()
        if form.validate_on_submit():
            shortname = form.play.data
            play = get_play_by_shortname(shortname)
            if not type(play) == Play:
                flash("Please select a valid play.")

            return redirect(f"/films/{shortname}/")

        return render_template("films-view.html", films=films, form=form)

# ----- END: PLAY VIEWS ----- #


# ----- BEGIN: PROCESS FILM ----- #

@app.route("/add-film/")
def add_new_film():
    """Prompts user for play and MovieDB ID to add film information via API."""

    return render_template("film-add.html",
                            play_titles = play_titles)


@app.route("/process-film/")
def process_film():
    """Given a MovieDB film URL by the user, query the MovieDB API for film info and pass to verification page."""

    play_shortname = request.args.get("play_titles")
    play = get_play_by_shortname(play_shortname)
    if not play.characters and not play.scenes:
        seed_play(play)
    film_url = request.args.get("film-url")

    film_id = get_moviedb_film_id(film_url)
    details, cast, crew = parse_moviedb_film(film_id, play)

    character_names = [character.name for character in play.characters]
    character_names.sort()

    return render_template("film-verify.html",
                            details=details,
                            cast=cast,
                            crew=crew,
                            play=play,
                            genders=GENDERS,
                            character_names=character_names,
                            )


@app.route("/add-film-to-db/", methods = ["POST"])
def add_film_to_db():
    """Use the form data from /process-film to add film information to the database."""

    film = {}
    film["play"] = request.form.get("play")
    film["title"] = request.form.get("title")
    film["poster_path"] = request.form.get("poster_path")
    film["release_date"] = request.form.get("release_date")
    film["language"] = request.form.get("language")
    film["length"] = request.form.get("length")
    film["film_moviedb_id"] = request.form.get("film_moviedb_id")
    film["film_imdb_id"] = request.form.get("film_imdb_id")

    play = get_play_by_title(film["play"])
    db_film = get_film(play=play, moviedb_id=film["film_moviedb_id"], imdb_id=film["film_imdb_id"], title=film["title"], release_date=film["release_date"], language=film["language"], length=film["length"], poster_path=film["poster_path"])
    
    people = []
    person_count = request.form.get("person_count")
    person_count = int(person_count) + 1
    for i in range(person_count):
        person = {}
        person["exclude"] = request.form.get(f"exclude-{i}")

        if not person["exclude"]:
            person["fname"] = request.form.get(f"fname-{i}")
            person["lname"] = request.form.get(f"lname-{i}")
            person["photo_path"] = request.form.get(f"photo_path-{i}")
            person["birthday"] = request.form.get(f"birthday-{i}")
            if not person["birthday"]:
                person["birthday"] = None
            person["gender"] = request.form.get(f"gender-{i}")
            person["moviedb_id"] = request.form.get(f"person_moviedb_id-{i}")
            person["imdb_id"] = request.form.get(f"person_imdb_id-{i}")

            person["parts"] = []
            part_count = request.form.get(f"part_count-{i}")
            part_count = int(part_count) + 1
            for j in range(part_count):
                person["parts"].append(request.form.get(f"part-{i}-{j}"))

            db_person = get_person(person["moviedb_id"], person["imdb_id"], person["fname"], person["lname"], person["birthday"], person["gender"], person["photo_path"])
            if person["parts"]:
                get_job_held(db_person, db_film, "Actor")
            for part_name in person["parts"]:
                get_part_played(person=db_person, character_name=part_name, film=db_film)

            people.append(person)

    return render_template("submit-form.html",
                            film=film,
                            people=people)

# ----- END: PROCESS FILM ----- #


# ----- BEGIN: API ROUTES ----- #

# @app.route("/api/users", methods=['GET'])
# @app.route("/api/users/<int:id>", methods=['GET'])
# def api_get_users(id=None):
#     if id:
#         user = user_schema.dump(User.query.get(id))
#         return {"user": user}
#     else:
#         users = users_schema.dump(User.query.all())
#         return {"users": users}

@app.route("/api/characters/", methods=['GET'])
@app.route("/api/characters/<int:id>/", methods=['GET'])
@app.route("/api/characters/<string:shortname>/", methods=['GET'])
def api_get_characters(id=None, shortname=None):
    """Return character information in JSON format. Results can be narrowed down by character ID or play shortname."""

    if id:
        character = character_schema.dump(Character.query.get(id))
        return {"character": character}
    elif shortname and shortname in play_titles.keys():
        play = get_play_by_shortname(shortname)
        characters = characters_schema.dump(Character.query.filter(Character.play_id == play.id))
        return {"characters": characters}
    else:
        characters = characters_schema.dump(Character.query.all())
        return {"characters": characters}


@app.route("/api/choices/", methods=['GET'])
@app.route("/api/choices/<int:id>/", methods=['GET'])
@app.route("/api/choices/<string:shortname>/", methods=['GET'])
def api_get_choices(id=None, shortname=None):
    """Return choice information in JSON format. Results can be narrowed down by choice ID or play shortname."""

    if id:
        choice = choice_schema.dump(Choice.query.get(id))
        return {"choice": choice}
    elif shortname and shortname in play_titles.keys():
        play = get_play_by_shortname(shortname)
        choices = choices_schema.dump(Choice.query.filter(Choice.play_id == play.id))
        return {"choices": choices}
    else:
        choices = choices_schema.dump(Choice.query.all())
        return {"choices": choices}


@app.route("/api/films/", methods=['GET'])
@app.route("/api/films/<int:id>/", methods=['GET'])
@app.route("/api/films/<string:shortname>/", methods=['GET'])
def api_get_films(id=None, shortname=None):
    """Return film information in JSON format. Results can be narrowed down by film ID or play shortname."""

    if id:
        film = film_schema.dump(Film.query.get(id))
        return {"film": film}
    elif shortname and shortname in play_titles.keys():
        play = get_play_by_shortname(shortname)
        films = films_schema.dump(Film.query.filter(Film.play_id == play.id))
        return {"films": films}
    else:
        films = films_schema.dump(Film.query.all())
        return {"films": films}


@app.route("/api/interpretations/", methods=['GET'])
@app.route("/api/interpretations/<int:id>/", methods=['GET'])
@app.route("/api/interpretations/<string:shortname>/", methods=['GET'])
def api_get_interpretations(id=None, shortname=None):
    """Return interpretation information in JSON format. Results can be narrowed down by interpretation ID or play shortname."""

    if id:
        interpretation = interpretation_schema.dump(Interpretation.query.get(id))
        return {"interpretation": interpretation}
    elif shortname and shortname in play_titles.keys():
        play = get_play_by_shortname(shortname)
        interpretations = interpretations_schema.dump(Interpretation.query.filter(Interpretation.play_id == play.id))
        return {"interpretations": interpretations}
    else:
        interpretations = interpretations_schema.dump(Interpretation.query.all())
        return {"interpretations": interpretations}


@app.route("/api/plays/", methods=['GET'])
@app.route("/api/plays/<int:id>/", methods=['GET'])
def api_get_plays(id=None):
    """Return play information in JSON format."""

    if id:
        play = play_schema.dump(Play.query.get(id))
        return {"play": play}
    else:
        plays = plays_schema.dump(Play.query.all())
        return {"plays": plays}


@app.route("/api/scenes/", methods=['GET'])
@app.route("/api/scenes/<int:id>/", methods=['GET'])
@app.route("/api/scenes/<string:shortname>/", methods=['GET'])
def api_get_scenes(id=None, shortname=None):
    """Return scene information in JSON format. Results can be narrowed down by scene ID or play shortname."""

    if id:
        scene = scene_schema.dump(Scene.query.get(id))
        return {"scene": scene}
    elif shortname and shortname in play_titles.keys():
        play = get_play_by_shortname(shortname)
        scenes = scenes_schema.dump(Scene.query.filter(Scene.play_id == play.id))
        return {"scenes": scenes}
    else:
        scenes = scenes_schema.dump(Scene.query.all())
        return {"scenes": scenes}

# ----- END: API ROUTES ----- #

@app.route("/search/")
def search_page():
    """Displays search page, returns results."""

    return render_template("search.html",
                            play_titles = play_titles)


if __name__ == '__main__':
    app.debug = True
    app.url_map.strict_slashes = False
    connect_to_db(app)
    app.run(host='0.0.0.0')