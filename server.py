from flask import Flask, render_template, redirect, flash, session, request, url_for
from flask_login.utils import login_user, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_required, set_login_view
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

    return render_template("login.html",
                            form=form)


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


# ----- BEGIN: PROCESS SCENES ----- #

@app.route("/add-scenes", methods=["GET", "POST"])
def add_scenes():
    """Prompts user for play, then scrapes the Folger scene number and descriptions for that play and passes the data to verify_scenes()."""

    form = ChoosePlayForm()
    if form.validate_on_submit():
        play_shortname = form.play.data
        play = get_play_by_shortname(play_shortname)
        scenes = parse_folger_scene_descriptions(play)

        return render_template("scenes-verify.html",
                                play=play,
                                scenes=scenes)

    return render_template("choose-play.html",
                            form=form)
    

@app.route("/add-scenes-to-db", methods = ["POST"])
def add_scenes_to_db():
    """Use the form data from /process-scenes to add scene information to the database."""

    play_title = request.form.get("play")
    play = get_play_by_title(play_title)
    scene_count = request.form.get("scene_count")
    scene_count = int(scene_count) + 1

    scenes = {}
    for i in range(scene_count):
        scene = {}
        scene["act"] = request.form.get(f"act-{i}")
        scene["scene"] = request.form.get(f"scene-{i}")
        scene["title"] = request.form.get(f"title-{i}")
        scene["description"] = request.form.get(f"description-{i}")
        scenes[i] = scene

        db_scene = get_scene(act=scene["act"], scene=scene["scene"], play=play, title=scene["title"], description=scene["description"])

    return redirect(f"/view-scenes-{play.shortname}")


@app.route("/edit-scenes", methods=["GET", "POST"])
def edit_scenes():
    """Given a Shakespeare play by the user, edit the existing scenes in the database."""

    form = ChoosePlayForm()
    page_title = "Edit Scenes"
    if form.validate_on_submit():
        play_shortname = form.play.data
        play = get_play_by_shortname(play_shortname)
        scenes = get_all_scenes_by_play(play)

        return render_template("scenes-edit.html",
                                play=play,
                                scenes=scenes)

    return render_template("choose-play.html",
                            page_title = page_title,
                            form=form)


@app.route("/scene-edit/<scene_num>", methods=["GET", "POST"])
def scene_page_edit(scene_num):
    """Use the scene number to retrieve and edit a specific Scene object."""

    scene = Scene.query.get(scene_num)
    form = SceneForm(obj=scene)

    if form.is_submitted():
        scene.title = form.title.data
        scene.description = form.description.data
        db.session.merge(scene)
        db.session.commit()

        return redirect(f"/view-scene/{scene_num}")
    
    return render_template("scene-edit.html", form=form)


@app.route("/edit-scenes-in-db", methods = ["POST"])
def edit_scenes_in_db():
    """Use the form data from /edit-scenes to edit scene information to the database."""

    play_title = request.form.get("play")
    play = get_play_by_title(play_title)
    shortname = play.shortname
    scene_count = request.form.get("scene_count")
    scene_count = int(scene_count) + 1

    scenes = {}
    for i in range(scene_count):
        scene_id = request.form.get(f"id-{i}")
        scene = Scene.query.get(scene_id)
        title = request.form.get(f"title-{i}")
        description = request.form.get(f"description-{i}")
        if title != None or description != None:
            update_scene(scene, title, description)

    return redirect(f"/view-scenes-{play.shortname}")


@app.route("/view-scenes", methods=["GET", "POST"])
def view_scenes():
    """Display a form for the user to choose a play, then displays the list of associated scenes."""

    form = ChoosePlayForm()
    page_title = "View Scenes"
    if form.validate_on_submit():
        play_shortname = form.play.data
        play = get_play_by_shortname(play_shortname)
        scenes = get_all_scenes_by_play(play)

        return render_template("scenes-view.html",
                                play=play,
                                scenes=scenes)

    return render_template("choose-play.html",
                            page_title = page_title,
                            form=form)


@app.route("/view-scenes/<shortname>", methods=["GET", "POST"])
def view_scenes_by_play(shortname):
    """Given a /view-scenes URL including a play shortname, display that play's associated scenes."""

    play = get_play_by_shortname(shortname)
    if not type(play) == Play: # if get_play_by_shortname returns error, send user to main view_scenes function
        return redirect("/view-scenes")

    scenes = get_all_scenes_by_play(play)

    return render_template("scenes-view.html",
                        play=play,
                        scenes=scenes)


@app.route("/view-scene/<scene_num>", methods=["GET", "POST"])
def view_scene(scene_num):

    scene = Scene.query.get(scene_num)

    return render_template("scene.html",
                            scene=scene)

# ----- END: PROCESS SCENES ----- #


# ----- BEGIN: PROCESS CHARACTERS ----- #

@app.route("/add-characters", methods=["GET", "POST"])
def add_characters():
    """Prompts user for play, then scrapes the Folger character information and passes the data to verify_characters()."""

    form = ChoosePlayForm()
    if form.validate_on_submit():
        play_shortname = form.play.data
        play = get_play_by_shortname(play_shortname)
        characters = parse_folger_characters(play)
        scenes = get_all_scenes_by_play(play)

        return render_template("characters-verify.html",
                                play=play,
                                characters=characters,
                                genders=GENDERS,
                                scenes=scenes)

    return render_template("choose-play.html",
                            form=form)


@app.route("/add-characters-to-db", methods = ["POST"])
def add_characters_to_db():
    """Use the form data from /process-characters to add character information to the database."""

    play_title = request.form.get("play")
    play = get_play_by_title(play_title)
    characters = []
    character_count = request.form.get("character_count")
    character_count = int(character_count) + 1
    for i in range(character_count):
        character = {}
        character["name"] = request.form.get(f"name-{i}")
        character["gender"] = request.form.get(f"gender-{i}")
        db_character = get_character(name=character["name"], gender=character["gender"], play=play)
        quote = request.form.get(f"quote-{i}")
        quote_scene = request.form.get(f"quote-scene-{i}")
        scene = Scene.query.get(quote_scene)
        add_quote(play=play, character=character, scene=quote_scene, text=quote)
        characters.append(character)

    return redirect(f"/view-characters/{play.shortname}")


@app.route("/edit-characters", methods=["GET", "POST"])
def edit_characters():
    """Given a Shakespeare play by the user, edit the existing characters in the database."""

    form = ChoosePlayForm()
    page_title = "Edit Characters"
    if form.validate_on_submit():
        play_shortname = form.play.data
        play = get_play_by_shortname(play_shortname)
        characters = get_all_characters_by_play(play)
        scenes = get_all_scenes_by_play(play)

        return render_template("characters-edit.html",
                                play=play,
                                characters=characters,
                                genders=GENDERS,
                                scenes=scenes)

    return render_template("choose-play.html",
                            page_title = page_title,
                            form=form)


@app.route("/edit-characters-<shortname>", methods=["GET", "POST"])
def edit_characters_by_play(shortname):
    """Given a /view-characters URL including a play shortname, edit that play's associated characters."""

    play = get_play_by_shortname(shortname)
    if not type(play) == Play: # if get_play_by_shortname returns error, send user to main view_characters function
        return redirect("/edit-characters")

    characters = get_all_characters_by_play(play)

    return render_template("characters-edit.html",
                            play=play,
                            characters=characters,
                            genders=GENDERS)


@app.route("/edit-characters-in-db", methods = ["POST"])
def edit_characters_in_db():
    """Use the form data from /edit-characters to edit character information to the database."""

    play_title = request.form.get("play")
    play = get_play_by_title(play_title)
    character_count = request.form.get("character_count")
    character_count = int(character_count) + 1

    characters = {}
    for i in range(character_count):
        character_id = request.form.get(f"id-{i}")
        character = Character.query.get(character_id)
        name = request.form.get(f"name-{i}")
        gender = request.form.get(f"gender-{i}")
        quote = request.form.get(f"quote-{i}")
        quote_scene = request.form.get(f"quote-scene-{i}")

        if name or gender:
            update_character(character, name, gender)
        if quote and quote_scene:
            scene = Scene.query.get(quote_scene)
            add_quote(play=play, character=character, scene=scene, text=quote)

    return redirect(f"/view-characters-{play.shortname}")


@app.route("/view-characters", methods=["GET", "POST"])
def view_characters():
    """Display a form for the user to choose a play, then displays the list of associated characters."""

    form = ChoosePlayForm()
    page_title = "View Characters"
    if form.validate_on_submit():
        play_shortname = form.play.data
        play = get_play_by_shortname(play_shortname)
        character_count = Character.query.filter(Character.play_id == play.id).count()
        added_characters = (character_count == 0) # if no characters were associated with play, explain that characters shown were just added

        characters = get_all_characters_by_play(play)

        return render_template("characters-view.html",
                                added_characters=added_characters,
                                play=play,
                                characters=characters,
                                genders=GENDERS)

    return render_template("choose-play.html",
                            page_title = page_title,
                            form=form)


@app.route("/view-characters-<shortname>", methods=["GET", "POST"])
def view_characters_by_play(shortname):
    """Given a /view-characters URL including a play shortname, display that play's associated characters."""

    play = get_play_by_shortname(shortname)
    if not type(play) == Play: # if get_play_by_shortname returns error, send user to main view_characters function
        return redirect("/view-characters")

    character_count = Character.query.filter(Character.play_id == play.id).count()
    added_characters = (character_count == 0) # if no characters were associated with play, explain that characters shown were just added
    characters = get_all_characters_by_play(play)

    return render_template("characters-view.html",
                            added_characters=added_characters,
                            play=play,
                            characters=characters,
                            genders=GENDERS)


@app.route("/view-character/<character_id>", methods=["GET", "POST"])
def character_page(character_id):
    """Given a character ID, display information about that character."""

    character = Character.query.get(character_id)

    return render_template("character-page.html",
                            character=character)

# ----- END: PROCESS CHARACTERS ----- #


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


# ----- BEGIN: PROCESS CHOICE ----- #

@app.route("/add-choices", methods=["GET", "POST"])
def add_choices():
    """Prompts user for play, then allows user to create a new related Choice object."""

    form = ChoosePlayForm()
    if form.validate_on_submit():
        play_shortname = form.play.data

        return redirect(f"/add-choices-{play_shortname}")

    return render_template("choose-play.html",
                            form=form)


@app.route("/add-choices-<shortname>", methods=["GET", "POST"])
def add_choices_by_play(shortname):
    """Given an /add-choices URL including a play shortname, display form to create a new Choice object."""

    play = get_play_by_shortname(shortname)
    scenes = get_all_scenes_by_play(play)
    characters = get_all_characters_by_play(play)
    scene_list = [(scene.id, f"{scene.act}.{scene.scene}: {scene.title}") for scene in scenes]
    character_list = [(character.id, character.name) for character in characters]
    
    form = CreateChoiceForm()
    form.scenes.choices = scene_list
    form.characters.choices = character_list

    class ChoiceForm(ModelForm):
        class Meta:
            model = Choice
            include_primary_keys = True


    if form.validate_on_submit():
        title = form.title.data
        desc = form.desc.data
        quote = form.quote.data
        scene_ids = form.scenes.data
        character_ids = form.characters.data

        choice = get_choice(play=play, title=title)
        if not choice:
            choice = add_choice(play=play, title=title, desc=desc)
        else:
            choice = update_choice(choice=choice, title=title, desc=desc)

        if scene_ids:
            for scene_id in scene_ids:
                scene = Scene.query.get(scene_id)
                add_choice_scene(choice, scene)
        if character_ids:
            for character_id in character_ids:
                character = Character.query.get(character_id)
                add_choice_character(choice, character)


        return redirect(f"/view-choices-{shortname}")

    return render_template("choices-add.html",
                            form=form)


@app.route("/view-choices", methods=["GET", "POST"])
def view_choices():
    """Prompts user for play, then display that play's associated choices."""

    form = ChoosePlayForm()
    if form.validate_on_submit():
        play_shortname = form.play.data

        return redirect(f"/view-choices-{play_shortname}")

    return render_template("choose-play.html",
                            form=form)


@app.route("/view-choices-<shortname>", methods=["GET", "POST"])
def view_choices_by_play(shortname):
    """Given a /view-choices URL including a play shortname, display that play's associated choices."""

    play = get_play_by_shortname(shortname)
    if not type(play) == Play: # if get_play_by_shortname returns error, send user to main view function
        return redirect("/view-choices")

    choices = get_all_choices_by_play(play)
    interpretations = get_all_interpretations_by_play(play)

    return render_template("choices-view.html",
                            choices=choices,
                            interpretations=interpretations,
                            play=play)


@app.route("/view-choice/<choice_id>", methods=["GET", "POST"])
def view_choice(choice_id):
    """Given a /view-choices URL including a choice ID, display that Choice"""

    choice = Choice.query.get(choice_id)

    return render_template("choice.html",
                            choice=choice)

@app.route("/choice-edit/<choice_id>", methods=["GET", "POST"])
def choice_page_edit(choice_id):
    """Given a Choice ID, retrieve and edit a specific Choice object."""

    choice = Choice.query.get(choice_id)

    class ChoiceForm(OrderFormMixin, ModelForm):
        class Meta:
            model = Choice
            order_after = ["submit"]

        submit = SubmitField("Submit")

    form = ChoiceForm(obj=choice)

    if form.is_submitted():
        choice = Choice.query.get(choice_id)
        choice.title = form.title.data
        choice.description = form.desc.data

        db.session.merge(choice)
        db.session.commit()

        return redirect(f"/view-choice/{choice_id}")

    return render_template("choice-edit.html",
                            form=form)


# ----- END: PROCESS CHOICE ----- #


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
    connect_to_db(app)
    app.run(host='0.0.0.0')
    seed_hamlet()