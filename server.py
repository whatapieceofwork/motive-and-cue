from flask import Flask, render_template, redirect, flash, session, request, url_for
from flask_login.utils import login_user, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_required, set_login_view
from flask_sqlalchemy.utils import parse_version
from sqlalchemy.sql import exists
from bs4 import BeautifulSoup
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import jinja2
import os
import requests
import json
from crud import *
from data_model import *
from folger_parser import *
from moviedb_parser import *
from seed import *
from forms import *
from collections import namedtuple, OrderedDict
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms_alchemy import model_form_factory, ModelFormField
BaseModelForm = model_form_factory(FlaskForm)

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
            print(f"************ ORDERBEFORE {order_before}")
            for field_name in order_before:
                print(f"*********FIELD_NAME {field_name}")
                print(f"**********{self._fields}")
                if field_name in self._fields:
                    print(f"************* BEFORE IN SELF TRUE")
                    add_before[field_name] = self._fields[field_name]
            new_fields.update(add_before)

        if order_after:
            print(f"************ ORDERAFTER {order_after}")
            for field_name in order_after:
                if field_name in self._fields:
                    print(f"************* AFTER IN SELF TRUE")
                    add_after[field_name] = self._fields[field_name]

        for field_name in self._fields:
            if field_name not in add_before and field_name not in add_after:
                new_fields[field_name] = self._fields[field_name]
                
        if add_after:
           new_fields.update(add_after)

        self._fields = new_fields


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


FLASK_KEY = os.environ["FLASK_KEY"]
MOVIEDB_API_KEY = os.environ["MOVIEDB_API_KEY"]
db = SQLAlchemy()

app = Flask(__name__)
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True
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
    """Displays index page."""

    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
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
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Thank you for registering! Please log in.")
        return redirect("/login")
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
    """Prompts user for play name, passes play name to appropriate function."""
    form = ChoosePlayForm()

    return render_template("choose-play.html", 
                            form=form, 
                            play_titles = play_titles)


# ----- BEGIN: SCENE VIEWS ----- #

@app.route("/scenes/", methods=["GET", "POST"])
@app.route("/scenes/<string:shortname>", methods=["GET", "POST"])
@app.route("/scenes/<int:id>", methods=["GET", "POST"])
def view_scenes(shortname=None, id=None):
    """Display all scenes, scenes by play shortname, or a specific scene by scene id. Prompt for play if not given in URL."""

    if shortname:
        play = get_play_by_shortname(shortname)
        if not type(play) == Play:
            flash("Please select a valid play.")
            return redirect("/scenes")
        scenes = get_all_scenes_by_play(play)
        return render_template("scenes-view.html", play=play, scenes=scenes)
        
    elif id:
        scene = Scene.query.get(id)
        return render_template("scene.html", scene=scene)

    form = ChoosePlayForm()
    if form.validate_on_submit():
        shortname = form.play.data
        play = get_play_by_shortname(shortname)
        if not type(play) == Play:
            flash("Please select a valid play.")

        return redirect(f"/scenes/{shortname}")

    return render_template("scenes-view.html", 
                            form=form)


@app.route("/scenes/add/", methods=["GET", "POST"])
@app.route("/scenes/add/<string:shortname>", methods=["GET", "POST"])
def add_scenes(shortname=None):
    """Add scenes by play shortname. Prompt for play if not given in URL."""

    if shortname:
        play = get_play_by_shortname(shortname)
        if not type(play) == Play:
            flash("Please select a valid play.")
            return redirect("/scenes/add")
        scenes = parse_folger_scene_descriptions(play)
        return render_template("scenes-edit.html", 
                                play=play, 
                                scenes=scenes)

    form = ChoosePlayForm()
    if form.validate_on_submit():
        shortname = form.play.data
        return redirect(f"/scenes/add/{shortname}")

    return render_template("scenes-edit.html", 
                            form=form)


@app.route("/scenes/edit/", methods=["GET", "POST"])
@app.route("/scenes/edit/<string:shortname>", methods=["GET", "POST"])
@app.route("/scenes/edit/<int:id>", methods=["GET", "POST"])
def edit_scenes(shortname=None, id=None):
    """Edit all scenes by play shortname, or a specific scene by scene id."""

    if shortname and request.method == "POST":
        play = get_play_by_shortname(shortname)
        if not type(play) == Play:
            flash("Please select a valid play.")
            return redirect("/scenes/edit")
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

        return redirect(f"/scenes/{shortname}")

    elif shortname:
        play = get_play_by_shortname(shortname)
        if not type(play) == Play:
            flash("Please select a valid play.")
            return redirect("/scenes")
        scenes = get_all_scenes_by_play(play)
        characters = get_all_characters_by_play(play)

        return render_template("scenes-edit.html", 
                                play=play, 
                                scenes=scenes,
                                characters=characters)
    
    elif id:
        scene = Scene.query.get(id)
        form = SceneForm(obj=scene)

        if form.is_submitted():
            scene.title = form.title.data
            scene.description = form.description.data
            db.session.merge(scene)
            db.session.commit()

            return redirect(f"/scenes/{id}")
    
        return render_template("scenes-edit.html",
                                scene=scene,
                                form=form)

    else:
        form = ChoosePlayForm()
        if form.validate_on_submit():
            shortname = form.play.data
            return redirect(f"/scenes/edit/{shortname}")

    return render_template("choose-play.html", 
                    form=form)

# ----- END: SCENE VIEWS ----- #


# ----- BEGIN: CHARACTER VIEWS ----- #

@app.route("/characters/", methods=["GET", "POST"])
@app.route("/characters/<string:shortname>", methods=["GET", "POST"])
@app.route("/characters/<int:id>", methods=["GET", "POST"])
def view_characters(shortname=None, id=None):
    """Display all characters, characters by play shortname, or a specific character by character id. Prompt for play if not given in URL."""

    if shortname:
        play = get_play_by_shortname(shortname)
        if not type(play) == Play:
            flash("Please select a valid play.")
            return redirect("/characters")
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
            return redirect("/characters")

        return redirect(f"/characters/{shortname}")

    return render_template("characters-view.html", 
                            form=form)


@app.route("/characters/add/", methods=["GET", "POST"])
@app.route("/characters/add/<string:shortname>", methods=["GET", "POST"])
def add_characters(shortname=None):
    """Add characters by play shortname. Prompt for play if not given in URL."""

    if shortname:
        play = get_play_by_shortname(shortname)
        if not type(play) == Play:
            flash("Please select a valid play.")
            return redirect("/characters/add")
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
        return redirect(f"/characters/add/{shortname}")

    return render_template("choose-play.html", 
                            form=form)


@app.route("/characters/edit/", methods=["GET", "POST"])
@app.route("/characters/edit/<string:shortname>", methods=["GET", "POST"])
@app.route("/characters/edit/<int:id>", methods=["GET", "POST"])
def edit_characters(shortname=None, id=None):
    """Edit all characters by play shortname, or a specific character by character id."""

    if shortname and request.method == "POST":
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

        return redirect(f"/characters/{shortname}")

    elif shortname:
        play = get_play_by_shortname(shortname)
        if not type(play) == Play:
            flash("Please select a valid play.")
            return redirect("/characters/edit")

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

            return redirect(f"/characters/{id}")
    
        return render_template("character-edit.html",
                                character=character,
                                form=form)

    else:
        form = ChoosePlayForm()
        if form.validate_on_submit():
            shortname = form.play.data
            return redirect(f"/characters/edit/{shortname}")

    return render_template("characters-edit.html", 
                    form=form)

# ----- END: CHARACTER VIEWS ----- #


# ----- BEGIN: CHOICE VIEWS ----- #

@app.route("/choices/", methods=["GET", "POST"])
@app.route("/choices/<string:shortname>", methods=["GET", "POST"])
@app.route("/choices/<int:id>", methods=["GET", "POST"])
def view_choices(shortname=None, id=None):
    """Display all choices, choices by play shortname, or a specific choice by choice id. Prompt for play if not given in URL."""

    if shortname:
        play = get_play_by_shortname(shortname)
        if not type(play) == Play:
            flash("Please select a valid play.")
            return redirect("/choices")
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
            return redirect("/choices")

        return redirect(f"/choices/{shortname}")

    return render_template("choices-view.html", 
                            form=form)


@app.route("/choices/add/", methods=["GET", "POST"])
@app.route("/choices/add/<string:shortname>", methods=["GET", "POST"])
def add_choices(shortname=None):
    """Add choices by play shortname. Prompt for play if not given in URL."""

    if shortname:
        play = get_play_by_shortname(shortname)
        if not type(play) == Play:
            flash("Please select a valid play.")
            return redirect("/choices/add")
        choices = get_all_choices_by_play(play)
        scenes = get_all_scenes_by_play(play)
        characters = get_all_characters_by_play(play)
        return render_template("choices-edit.html", 
                                play=play, 
                                choices=choices,
                                characters=characters,
                                scenes=scenes)

    form = ChoosePlayForm()
    if form.validate_on_submit():
        shortname = form.play.data
        return redirect(f"/choices/add/{shortname}")

    return render_template("choose-play.html", 
                            form=form)


@app.route("/choices/edit/", methods=["GET", "POST"])
@app.route("/choices/edit/<string:shortname>", methods=["GET", "POST"])
@app.route("/choices/edit/<int:id>", methods=["GET", "POST"])
def edit_choices(shortname=None, id=None):
    """Edit all choices by play shortname, or a specific choice by choice id."""

    if shortname:
        play = get_play_by_shortname(shortname)
        choices = get_all_choices_by_play(play)

        return render_template("/choices-edit.html", 
                                choices=choices,
                                play=play)
    
    elif id:
        choice = Choice.query.get(id)
        class ChoiceForm(OrderFormMixin, ModelForm):
            class Meta:
                model = Choice
                order_before = ["play"]
                order_after = ["characters", "scenes", "submit"]
    
            play = QuerySelectField('Related Play', 
                                            query_factory=Play.query.all)
            characters = QuerySelectMultipleField('Related Characters', 
                                            query_factory=Character.query.all)
            scenes = QuerySelectMultipleField('Related Scenes', 
                                            query_factory=Scene.query.all)
            submit = SubmitField("Submit")

        form = ChoiceForm(obj=choice)

        if form.is_submitted():
            title = form.title.data
            desc = form.desc.data
            play = form.play.data
            db_characters = form.characters.data
            db_scenes = form.scenes.data

            if not choice:
                choice = add_choice(play=play, title=title, desc=desc)

            for character in db_characters:
                get_choice_character(choice=choice, character=character)

            for scene in db_scenes:
                get_choice_scene(choice=choice, scene=scene)


            return redirect(f"/choices/{id}")

    
        return render_template("choices-edit.html",
                                choice=choice,
                                form=form)

    form = ChoosePlayForm()
    if form.validate_on_submit():
        shortname = form.play.data
        return redirect(f"/choices/edit/{shortname}")

    return render_template("choices-edit.html", 
                    form=form)

# ----- END: CHOICE VIEWS ----- #


# ----- BEGIN: PROCESS FILM ----- #

@app.route("/add-film")
def add_new_film():
    """Prompts user for play and MovieDB ID to add film information via API."""

    return render_template("film-add.html",
                            play_titles = play_titles)


@app.route("/process-film")
def process_film():
    """Given a MovieDB film URL by the user, query the MovieDB API for film info and pass to verification page."""

    play_shortname = request.args.get("play_titles")
    play = get_play_by_shortname(play_shortname)
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


@app.route("/add-film-to-db", methods = ["POST"])
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


@app.route("/add-interpretation", methods=["GET", "POST"])
def add_interpretations():

    class InterpretationForm(OrderFormMixin, ModelForm):
        class Meta:
            model = Interpretation
            order_before = ["choice", "film"]
            order_after = ["submit"]
    
        choice = QuerySelectField('Related Choices',
                                query_factory=Choice.query.all)
        film = QuerySelectMultipleField('Related Film',
                        query_factory=Film.query.all)
        submit = SubmitField("Submit")

    form = InterpretationForm()

    if form.is_submitted():
        interpretation = Interpretation()
        interpretation.title = form.title.data
        interpretation.description = form.description.data
        interpretation.time_start = form.time_start.data
        interpretation.time_end = form.time_end.data
        db_choice = form.choice.data
        interpretation.choice_id = db_choice.id

        db.session.add(interpretation)
        db.session.commit()

        return redirect("/view-interpretations")

    return render_template("interpretations-add.html",
                            form=form)


@app.route("/view-interpretations", methods=["GET", "POST"])
def view_interpretations():

    interpretations = Interpretation.query.all()

    return render_template("interpretations-view.html",
                            interpretations=interpretations)


@app.route("/test-forms", methods=["GET", "POST"])
def test_forms():
    """A view for testing forms."""

    hamlet = get_play_by_title("Hamlet")
    characters = get_all_characters_by_play(hamlet)
    char = namedtuple("Char", ['id', 'name'])
    character_list = {str(character.id) : character.name for character in characters}

    scene1 = Scene.query.get(1)
    scenes = get_all_scenes_by_play(hamlet)
    form = SceneForm(obj=scene1)

    if form.is_submitted():
        scene1.title = form.title.data
        scene1.description = form.description.data
        db.session.merge(scene1)
        db.session.commit()

    return render_template('test-forms.html', form=form)





    
if __name__ == '__main__':
    app.debug = True
    app.url_map.strict_slashes = False
    connect_to_db(app)
    app.run(host='0.0.0.0')
    seed_hamlet()