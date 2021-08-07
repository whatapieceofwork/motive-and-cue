from app import db
from app.decorators import admin_required, permission_required
from app.main.folger_parser import parse_folger_characters, parse_folger_scene_descriptions, parse_folger_scenes
from app.main.forms import *
from app.main.moviedb_parser import parse_moviedb_cast, parse_moviedb_crew, parse_moviedb_film, parse_moviedb_film_details, parse_moviedb_person, get_moviedb_film_id
from app.main.crud import *
from app.models import *
from datetime import datetime
from flask import abort, flash, g, redirect, render_template, request, session, url_for, render_template_string
from flask_login import current_user, login_required
from . import main


@main.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
    g.search_form = SearchForm()


@main.route("/")
@main.route("/index/")
def index():
    """Display index page."""

    title = "Home"
    return render_template("index.html",
                            current_time=datetime.utcnow(), title=title)
 
 
@main.route("/browse/")
def browse():
    """Display browse page."""

    title = "Browse"
    return render_template("browse.html")


@main.route("/admin", methods=["GET", "POST"])
@login_required
@admin_required
def admin_index():
    """Display administrator-facing index page; return 403 if user not an admin."""

    title="Admin"
    return render_template("admin.html", title=title)


@main.route("/edit-profile", methods=["GET", "POST"])
@login_required
def profile_edit():
    """Display form to edit user profile page."""

    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.about = form.about.data
        db.session.add(current_user._get_current_object())
        db.session.commit()

        flash("Your profile has been successfully updated.", "success")
        return redirect(url_for(".profile", username=current_user.username))

    form.name.data = current_user.name
    form.about.data = current_user.about

    title="Edit Profile"
    return render_template("profile-edit.html", form=form, title=title)


@main.route("/edit-profile/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def profile_edit_admin(id):
    """Display form for administrator to edit user profile page."""

    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)

    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.name = form.name.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.about = form.about.data
        db.session.add(user)
        db.session.commit()

        flash("The profile has been successfully updated.", "success")
        return redirect(url_for(".profile", username=user.username))

    form.email.data = user.email
    form.username.data = user.username
    form.name.data = user.name
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.about.data = user.about

    title = "Edit User Profile"
    return render_template("profile-edit.html", form=form, user=user, title=title)


@main.route("/user/<username>")
def profile(username):
    """Given a username in the URL, display user profile page or return 404."""

    user = get_user_by_username(username)
    if not user:
        abort(404)

    title = user.username
    return render_template("profile.html", user=user, title=title)


@main.route("/about")
def about():
    """Display the About page."""

    title = "About"
    return render_template("about.html", title=title)

@main.route("/search", methods=["GET", "POST"])
def search():

    title = "Search"
    advanced_search_form = AdvancedSearchForm()
    results = []

    if request.method == "POST" or request.method == "GET":
        if not g.search_form.validate() and not advanced_search_form.validate():
            flash("Search error. Please try again.", "error")
            return redirect(url_for('main.index'))
 
        # prioritize search queries made from the Search page
        if advanced_search_form.search_field.query.data:
            query = advanced_search_form.search_field.query.data
            advanced_search_form.search_field.query.data = query #set default value of search to current query
        else:
            query = g.search_form.query.data
            advanced_search_form.search_field.query.data = query

        #####
        # TO IMPLEMENT: NARROW SEARCH BY CHOSEN FACETS
        #####

        results += Character.query.whooshee_search(query).order_by(Character.id.desc()).all()
        results += Film.query.whooshee_search(query).order_by(Film.id.desc()).all()
        results += Interpretation.query.whooshee_search(query).order_by(Interpretation.id.desc()).all()
        results += Job.query.whooshee_search(query).order_by(Job.id.desc()).all()
        results += Person.query.whooshee_search(query).order_by(Person.id.desc()).all()
        results += Play.query.whooshee_search(query).order_by(Play.id.desc()).all()
        results += Question.query.whooshee_search(query).order_by(Question.id.desc()).all()
        results += Scene.query.whooshee_search(query).order_by(Scene.id.desc()).all()
    
    return render_template("search.html", title=title, results=results, query=query, advanced_search_form=advanced_search_form)

# ----- BEGIN: SCENE VIEWS ----- #

@main.route("/scenes/", methods=["GET", "POST"])
@main.route("/scenes/<string:shortname>/", methods=["GET", "POST"])
@main.route("/scenes/<int:id>/", methods=["GET", "POST"])
def view_scenes(shortname=None, id=None):
    """Display all scenes, scenes by play shortname, or a specific scene by scene id. Prompt for play if not given in URL."""

    if shortname:
        if shortname not in play_titles.keys():
            flash("Please select a valid play.")
            return redirect("/scenes/")
        play = get_play_by_shortname(shortname)
        scenes = get_all_scenes_by_play(play)

        title = f"{play.title} Scenes"
        return render_template("scenes-view.html", play=play, scenes=scenes, title=title)

    elif id:
        scene = Scene.query.get(id)
        title = f"Act {scene.act}, Scene {scene.scene} from {scene.play.title}"
        return render_template("scene.html", scene=scene, title=title)

    form = ChoosePlayForm()
    if form.validate_on_submit():
        shortname = form.play.data
        if shortname not in play_titles.keys():
            flash("Please select a valid play.")
        
        play = get_play_by_shortname(shortname)

        return redirect(f"/scenes/{shortname}/")

    title = "Scenes"
    return render_template("scenes-view.html", form=form, title=title)


@main.route("/scenes/add/", methods=["GET", "POST"])
@main.route("/scenes/add/<string:shortname>/", methods=["GET", "POST"])
@login_required
@admin_required
def add_scenes(shortname=None):
    """Add scenes by play shortname using Folger scene information. Prompt for play if not given in URL."""

    if shortname:
        if shortname not in play_titles.keys():
            flash("Please select a valid play.")
            return redirect("/scenes/add/")
        
        play = get_play_by_shortname(shortname)
        scenes = parse_folger_scene_descriptions(play)

        title = "Add Scenes"
        return render_template("scenes-edit.html", play=play, scenes=scenes, title=title)

    form = ChoosePlayForm()
    if form.validate_on_submit():
        shortname = form.play.data
        return redirect(f"/scenes/add/{shortname}/")

    title = "Add Scenes"
    return render_template("scenes-edit.html", form=form, title=title)


@main.route("/scenes/edit/", methods=["GET", "POST"])
@main.route("/scenes/edit/<string:shortname>/", methods=["GET", "POST"])
@main.route("/scenes/edit/<int:id>/", methods=["GET", "POST"])
@login_required
@admin_required
def edit_scenes(shortname=None, id=None):
    """Edit all scenes by play shortname, or a specific scene by scene id. Prompt for play if not given in URL."""

    if shortname and request.method == "POST": # If the user submitted scene information related to a given play, proces that information
        if shortname not in play_titles.keys():
            flash("Please select a valid play.")
            return redirect("/scenes/edit/")

        play = get_play_by_shortname(shortname)
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
        if shortname not in play_titles.keys():
            flash("Please select a valid play.")
            return redirect("/scenes/")       
     
        play = get_play_by_shortname(shortname)
        scenes = get_all_scenes_by_play(play)
        characters = get_all_characters_by_play(play)

        title = f"Edit {play.title} Scenes"
        return render_template("scenes-edit.html", play=play, scenes=scenes, characters=characters, title=title)
    
    elif id: # Edit a single scene
        scene = Scene.query.get(id)
        form = SceneForm(obj=scene)

        if form.is_submitted():
            scene.title = form.title.data
            scene.description = form.description.data
            db.session.merge(scene)
            db.session.commit()

            return redirect(f"/scenes/{id}/")
    
        title = f"Edit Act {scene.act}, Scene {scene.scene} from {scene.play.title}"
        return render_template("scenes-edit.html", scene=scene, form=form, title=title)

    else:
        form = ChoosePlayForm()
        if form.validate_on_submit():
            shortname = form.play.data
            return redirect(f"/scenes/edit/{shortname}/")

    title = "Edit Scenes"
    return render_template("choose-play.html", form=form, title=title)

# ----- END: SCENE ROUTES ----- #


# ----- BEGIN: CHARACTER ROUTES ----- #

@main.route("/characters/", methods=["GET", "POST"])
@main.route("/characters/<string:shortname>/", methods=["GET", "POST"])
@main.route("/characters/<int:id>/", methods=["GET", "POST"])
def view_characters(shortname=None, id=None):
    """Display all characters, characters by play shortname, or a specific character by character id. Prompt for play if not given in URL."""

    if shortname:
        if shortname not in play_titles.keys():
            flash("Please select a valid play.")
            return redirect("/characters/")

        play = get_play_by_shortname(shortname)
        characters = get_all_characters_by_play(play)

        title = f"{play.title} Characters"
        return render_template("characters-view.html", play=play, characters=characters, title=title)
        
    elif id:
        character = Character.query.get(id)

        title = f"{character.name} from {character.play.title}"
        return render_template("character.html", character=character, title=title)

    form = ChoosePlayForm()
    if form.validate_on_submit():
        shortname = form.play.data
        play = get_play_by_shortname(shortname)

        return redirect(f"/characters/{shortname}/")

    title = "Characters"
    return render_template("characters-view.html", form=form, title=title)


@main.route("/characters/add/", methods=["GET", "POST"])
@main.route("/characters/add/<string:shortname>/", methods=["GET", "POST"])
@login_required
@admin_required
def add_characters(shortname=None):
    """Add characters by play shortname using Folger character information. Prompt for play if not given in URL."""

    if shortname:
        if shortname not in play_titles.keys():
            flash("Please select a valid play.")
            return redirect("/characters/add/")

        play = get_play_by_shortname(shortname)
        characters = get_all_characters_by_play(play)
        scenes = get_all_scenes_by_play(play)

        title = f"Add {play.title} Characters"
        return render_template("characters-edit.html", play=play, characters=characters, 
                                genders=GENDERS, scenes=scenes, title=title)

    form = ChoosePlayForm()
    if form.validate_on_submit():
        shortname = form.play.data
        return redirect(f"/characters/add/{shortname}/")

    title = "Add Characters"
    return render_template("characters-edit.html", form=form, title=title)


@main.route("/characters/edit/", methods=["GET", "POST"])
@main.route("/characters/edit/<string:shortname>/", methods=["GET", "POST"])
@main.route("/characters/edit/<int:id>/", methods=["GET", "POST"])
@login_required
@admin_required
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
                character = update_character(character=existing_character, name=name, gender=gender, img=img)
            else:
                character = add_character(name=name, play=play, gender=gender)

            if quote and scene:
                add_quote(play=play, character=character, scene=scene, text=quote)

        title = f"Edit {play.title} Characters"
        return redirect(f"/characters/{shortname}/")

    elif shortname:
        if shortname not in play_titles.keys():
            flash("Please select a valid play.")
            return redirect("/characters/edit/")

        play = get_play_by_shortname(shortname)
        characters = get_all_characters_by_play(play)
        scenes = get_all_scenes_by_play(play)

        title = f"Edit {play.title} Characters"
        return render_template("characters-edit.html", play=play, scenes=scenes, 
                                characters=characters, genders=GENDERS, title=title)
    
    elif id:
        character = Character.query.get(id)
        form = CharacterForm(obj=character)

        if form.is_submitted():
            character.name = form.name.data
            character.gender = form.gender.data
            img = request.files["image"]
            if img:
                img = cloudinary_url(img)
                character.img = img
            db.session.merge(character)
            db.session.commit()

            return redirect(f"/characters/{id}/")
    
        title = f"Edit {character.name} from {character.play.title}"
        return render_template("characters-edit.html", character=character, form=form, title=title)

    else:
        form = ChoosePlayForm()
        if form.validate_on_submit():
            shortname = form.play.data
            return redirect(f"/characters/edit/{shortname}/")

    title = "Edit Characters"
    return render_template("characters-edit.html", form=form, title=title)

# ----- END: CHARACTER ROUTES ----- #


# ----- BEGIN: QUESTION VIEWS ----- #

@main.route("/questions/", methods=["GET", "POST"])
@main.route("/questions/<string:shortname>/", methods=["GET", "POST"])
@main.route("/questions/<int:id>/", methods=["GET", "POST"])
def view_questions(shortname=None, id=None):
    """Display all questions, questions by play shortname, or a specific question by question id. Prompt for play if not given in URL."""

    if shortname:
        if shortname not in play_titles.keys():
            flash("Please select a valid play.")
            return redirect("/questions/")

        play = get_play_by_shortname(shortname)
        questions = get_all_questions_by_play(play)

        title = f"Textual Questions from {play.title}"
        return render_template("questions-view.html", play=play, questions=questions, title=title)
        
    elif id:
        question = Question.query.get(id)

        title = f"{question.title}"
        return render_template("question.html", question=question, title=title)

    form = ChoosePlayForm()
    if form.validate_on_submit():
        shortname = form.play.data
        play = get_play_by_shortname(shortname)
        if shortname not in play_titles.keys():
            flash("Please select a valid play.")
            return redirect("/questions/")

        return redirect(f"/questions/{shortname}/")

    title = "Textual Questions"
    return render_template("questions-view.html", form=form, title=title)


@main.route("/questions/add/", methods=["GET", "POST"])
@main.route("/questions/add/<string:shortname>/", methods=["GET", "POST"])
@login_required
@admin_required
def add_questions(shortname=None):
    """Add questions by play shortname. Prompt for play if not given in URL."""

    if shortname:
        if shortname not in play_titles.keys():
            flash("Please select a valid play.")
            return redirect("/questions/add/")

        play = get_play_by_shortname(shortname)
        form = make_question_form(db_play=play)

        if form.is_submitted():
            title = form.title.data
            description = form.description.data
            db_characters = form.characters.data
            db_scenes = form.scenes.data
            img = request.files["image"]
            if img:
                img = cloudinary_url(img)

            question = add_question(play=play, title=title, description=description, img=img)
            for character in db_characters:
                get_question_character(question=question, character=character)
            for scene in db_scenes:
                get_question_scene(question=question, scene=scene)

            return redirect(f"/questions/{question.id}/")

        questions = get_all_questions_by_play(play)
        scenes = get_all_scenes_by_play(play)
        characters = get_all_characters_by_play(play)

        title = f"Edit {play.title} Questions"
        return render_template("questions-edit.html", form=form, play=play, questions=questions, 
                                characters=characters, scenes=scenes, title=title)

    form = ChoosePlayForm()
    if form.validate_on_submit():
        shortname = form.play.data
        return redirect(f"/questions/add/{shortname}/")

    title = "Textual Questions"
    return render_template("choose-play.html", form=form, title=title)


@main.route("/questions/edit/", methods=["GET", "POST"])
@main.route("/questions/edit/<string:shortname>/", methods=["GET", "POST"])
@main.route("/questions/edit/<int:id>/", methods=["GET", "POST"])
@login_required
@admin_required
def edit_questions(shortname=None, id=None):
    """Edit all questions by play shortname, or a specific question by question id."""

    if shortname:
        if shortname not in play_titles.keys():
            flash("Please select a valid play.")
            return redirect("/questions/edit/")

        play = get_play_by_shortname(shortname)
        questions = get_all_questions_by_play(play)

        title = f"Edit Textual Questions from {play.title}"
        return render_template("/questions-edit.html", questions=questions, play=play, title=title)
    
    elif id:
        question = Question.query.get(id)
        play = question.play
        form = make_question_form(db_play=play, db_question=question)

        if form.is_submitted():
            play = form.play.data
            title = form.title.data
            description = form.description.data
            db_characters = form.characters.data
            db_scenes = form.scenes.data
            img = request.files["image"]
            if img:
                img = cloudinary_url(img)

            existing_question = Question.query.get(question.id)
            if existing_question:
                question = update_question(question=existing_question, title=title, description=description, img=img)
            else:
               question = add_question(play=play, title=title, description=description, img=img)

            for character in db_characters:
                get_question_character(question=question, character=character)
            for scene in db_scenes:
                get_question_scene(question=question, scene=scene)

            return redirect(f"/questions/{id}/")

        title = f"Edit {question.title}"
        return render_template("questions-edit.html", question=question, form=form, title=title)

    form = ChoosePlayForm()
    if form.validate_on_submit():
        shortname = form.play.data
        return redirect(f"/questions/edit/{shortname}/")

    title = "Edit Textual Questions"
    return render_template("questions-edit.html", form=form, title=title)

# ----- END: QUESTION VIEWS ----- #


# ----- BEGIN: INTERPRETATION VIEWS ----- #

@main.route("/interpretations/", methods=["GET", "POST"])
@main.route("/interpretations/<string:shortname>/", methods=["GET", "POST"])
@main.route("/interpretations/<int:id>/", methods=["GET", "POST"])
def view_interpretations(shortname=None, id=None):
    """Display all interpretations, interpretations by play shortname, or a specific interpretation by interpretation id. Prompt for play if not given in URL."""

    if shortname:
        if shortname not in play_titles.keys():
            flash("Please select a valid play.")
            return redirect("/interpretations/")

        play = get_play_by_shortname(shortname)
        interpretations = get_all_interpretations_by_play(play)

        title = f"{play.title} Film Interpretations"
        return render_template("interpretations-view.html", play=play, interpretations=interpretations, title=title)
        
    elif id:
        interpretation = Interpretation.query.get(id)

        title = f"{interpretation.title}"
        return render_template("interpretation.html", interpretation=interpretation, title=title)

    form = ChoosePlayForm()
    if form.validate_on_submit():
        shortname = form.play.data
        play = get_play_by_shortname(shortname)

        return redirect(f"/interpretations/{shortname}/")

    title = "Film Interpretations"
    return render_template("interpretations-view.html", form=form, title=title)


@main.route("/interpretations/add/", methods=["GET", "POST"])
@main.route("/interpretations/add/<string:shortname>/", methods=["GET", "POST"])
@main.route("/interpretations/add/<int:question_id>/", methods=["GET", "POST"])
@login_required
@admin_required
def add_interpretations(shortname=None, question_id=None):
    """Add interpretations by play shortname or by related Question ID. Prompt for play if not given in URL."""

    if shortname or question_id: 
        if shortname:
            if shortname not in play_titles.keys():
                flash("Please select a valid play.")
                return redirect("/interpretations/add/")

            play = get_play_by_shortname(shortname)
            form = make_interpretation_form(db_play=play)

        if question_id:
            question = Question.query.get(question_id)
            play = question.play
            shortname = question.play.shortname
            if shortname not in play_titles.keys():
                flash("Please select a valid play.")
                return redirect("/interpretations/add/")

            play = get_play_by_shortname(shortname)
            form = make_interpretation_form(db_play=play, db_question=question)              
        
        if form.is_submitted():
            film = form.film.data
            title = form.title.data
            description = form.description.data
            time_start = form.time_start.data
            time_end = form.time_end.data  
            question = form.question.data
 
            interpretation = add_interpretation(question=question, play=play, film=film, title=title, 
                                    description=description, time_start=time_start, time_end=time_end)

            return redirect(f"/interpretations/{interpretation.id}/")

    else:
        form = ChoosePlayForm()
        if form.validate_on_submit():
            shortname = form.play.data
            return redirect(f"/interpretations/add/{shortname}/")

    title = "Add Film Interpretations"
    return render_template("interpretations-edit.html", form=form, title=title) 


@main.route("/interpretations/edit/", methods=["GET", "POST"])
@main.route("/interpretations/edit/<string:shortname>/", methods=["GET", "POST"])
@main.route("/interpretations/edit/<int:id>/", methods=["GET", "POST"])
def edit_interpretations(shortname=None, id=None):
    """Edit all interpretations by play shortname, or a specific interpretation by interpretation id."""

    if shortname:
        play = get_play_by_shortname(shortname)
        interpretations = get_all_interpretations_by_play(play)

        title = f"Edit {play.title} Film Interpretations"
        return render_template("/interpretations-edit.html", interpretations=interpretations,
                                play=play, title=title)

    elif id:
        interpretation = Interpretation.query.get(id)
        form = make_interpretation_form(db_interpretation=interpretation, db_play=interpretation.play, db_question=interpretation.question, db_object=interpretation)

        if form.is_submitted():
            play = form.play.data
            question = form.question.data
            film = form.film.data
            title = form.title.data
            description = form.description.data
            time_start = form.time_start.data
            time_end = form.time_end.data

            existing_interpretation = Interpretation.query.get(interpretation.id)
            if existing_interpretation:
                interpretation = update_interpretation(interpretation=existing_interpretation, play=play, film=film, title=title, description=description, time_start=time_start, time_end=time_end)
            else:
               interpretation = add_interpretation(question=question, play=play, film=film, title=title, description=description, time_start=time_start, time_end=time_end)

            return redirect(f"/interpretations/{interpretation.id}/")

        title = f"Edit {interpretation.title}"
        return render_template("interpretations-edit.html", interpretation=interpretation, form=form, title=title)

    form = ChoosePlayForm()
    if form.validate_on_submit():
        shortname = form.play.data
        return redirect(f"/interpretations/edit/{shortname}/")

    title = "Edit Film Interpretations"
    return render_template("interpretations-edit.html", form=form, title=title)

# ----- END: INTERPRETATION VIEWS ----- #


# ----- BEGIN: PEOPLE VIEWS ----- #

@main.route("/people/", methods=["GET", "POST"])
@main.route("/people/<int:id>/", methods=["GET", "POST"])
def view_people(shortname=None, id=None):
    """Display all people, or a specific person by id."""

    if id:
        person = Person.query.get(id)

        title = f"{person.fname} {person.lname}"
        return render_template("person.html", person=person, title=title)
        
    else:
        people = Person.query.all()

        title = "People"
        return render_template("people-view.html", people=people, title=title)

# ----- END: PEOPLE VIEWS ----- #


# ----- BEGIN: PLAY VIEWS ----- #

@main.route("/plays/", methods=["GET", "POST"])
@main.route("/plays/<string:shortname>/", methods=["GET", "POST"])
@main.route("/plays/<int:id>/", methods=["GET", "POST"])
def view_plays(shortname=None, id=None):
    """Display all plays, or a specific play by shortname or id."""

    if shortname or id:
        if shortname:
            if shortname not in play_titles.keys():
                flash("Please select a valid play.")
                return redirect("/interpretations/add/")
            play = get_play_by_shortname(shortname)

        elif id:
            play = Play.query.get(id)

        scenes = get_all_scenes_by_play(play)

        title = play.title
        return render_template("play.html", play=play, title=title, scenes=scenes)
        
    else:
        plays = Play.query.all()

        title = "Plays"
        return render_template("plays-view.html", plays=plays, title=title)

# ----- END: PLAY VIEWS ----- #


# ----- BEGIN: FILM VIEWS ----- #

@main.route("/films/", methods=["GET", "POST"])
@main.route("/films/<string:shortname>/", methods=["GET", "POST"])
@main.route("/films/<int:id>/", methods=["GET", "POST"])
def view_films(shortname=None, id=None):
    """Display all films, films by related play shortname, or a specific film by id."""

    if shortname:
        if shortname not in play_titles.keys():
            flash("Please select a valid play.")
            return redirect("/films/")

        play = get_play_by_shortname(shortname)        
        films = get_films_by_play(play)

        title = f"{play.title} Films"
        return render_template("films-view.html", films=films, play=play, title=title)

    elif id:
        film = Film.query.get(id)
        play = film.play
        parts_played = CharacterActor.query.filter(CharacterActor.film_id == film.id).all()
        hamlet_age = None
        if play.title == "Hamlet":
            hamlet = Character.query.filter(Character.name == "Hamlet").first()
            hamlet_actor = CharacterActor.query.filter((CharacterActor.film_id == film.id) & (CharacterActor.character == hamlet)).first()
            hamlet_actor = hamlet_actor.person
            hamlet_age = calculate_age_during_film(hamlet_actor, film)

        title = f"{film.title} - {film.release_date}"
        return render_template("film.html", film=film, play=play, parts_played=parts_played, hamlet_age=hamlet_age, title=title)
        
    else:
        films = Film.query.all()
        form = ChoosePlayForm()
        if form.validate_on_submit():
            shortname = form.play.data
            if shortname not in play_titles.keys():
                flash("Please select a valid play.")
                return redirect(f"/films/")

            return redirect(f"/films/{shortname}/")

        title = "Films"
        return render_template("films-view.html", films=films, form=form, title=title)


@main.route("/films/add")
@main.route("/questions/add/<string:shortname>/", methods=["GET", "POST"])
@login_required
@admin_required
def add_films():
    """Prompts user for play and MovieDB ID to add film information via API."""

    title = "Add a Film"
    return render_template("films-add.html", play_titles=play_titles, title=title)


@main.route("/process-film/")
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

    title = "Verify Film Information"
    return render_template("films-verify.html", details=details, cast=cast, crew=crew,
                            play=play, genders=GENDERS, character_names=character_names, title=title)


@main.route("/add-film-to-db/", methods = ["POST"])
def add_film_to_db():
    """Use the form data from /process-film to add film information to the database."""

    film = {}
    film["play"] = request.form.get("play")
    film["title"] = request.form.get("title")
    film["overview"] = request.form.get("overview")
    # film["tagline"] = request.form.get("tagline") # seeing persistent errors with tagline saving
    film["poster_path"] = request.form.get("poster_path")
    film["release_date"] = request.form.get("release_date")
    film["language"] = request.form.get("language")
    film["length"] = request.form.get("length")
    film["film_moviedb_id"] = request.form.get("film_moviedb_id")
    film["film_imdb_id"] = request.form.get("film_imdb_id")
    # film["watch_providers"] = request.form.get("watch_providers") # seeing persistent errors with watch_providers saving

    play = get_play_by_title(film["play"])
    db_film = get_film(play=play, moviedb_id=film["film_moviedb_id"], imdb_id=film["film_imdb_id"], title=film["title"], 
                        release_date=film["release_date"], language=film["language"], length=film["length"], overview=film["overview"], 
                        poster_path=film["poster_path"])
    
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
                get_person_job(db_person, db_film, "Actor")
            for part_name in person["parts"]:
                get_character_actor(person=db_person, character_name=part_name, film=db_film)

            people.append(person)

    title = "Add Film"
    return redirect(f"/films/{db_film.id}")


@main.route("/films/edit/", methods=["GET", "POST"])
@main.route("/films/edit/<string:shortname>/", methods=["GET", "POST"])
@main.route("/films/edit/<int:id>/", methods=["GET", "POST"])
def edit_films(shortname=None, id=None):
    """Edit all films, films by play shortname, or a specific film by film id."""

    films = Film.query.all()
    form = None
    
    if id:
        film = Film.query.get(id)
        form = make_film_form(film)
    elif shortname:
        play = get_play_by_shortname(shortname)
        films = Film.query.filter(Film.play_id == play.id).all()
    else:
        form = ChoosePlayForm()

    if form.validate_on_submit():
        film = Film.query.get(id)

        film.title = form.title.data
        film.moviedb_id = form.moviedb_id.data
        film.imdb_id = form.imdb_id.data
        film.play = form.play.data
        film.overview = form.overview.data
        # film.tagline = form.tagline.data
        film.poster_path = form.poster_path.data
        film.release_date = form.release_date.data
        # film.watch_providers = form.watch_providers.data
        db.session.merge(film)
        db.session.commit()

        return redirect(f"/films/{id}/")

    return render_template("films-edit.html", films=films, form=form)
# ----- END: PROCESS FILM ----- #


# ----- BEGIN: TEST ROUTES ----- #

#  REMOVE BEFORE LAUNCH!!
@main.route("/reboot")
def test_reboot():
    """A wonderfully dangerous route to dump and rebuild the database for testing."""

    from app.main.seed import make_admin

    db.session.commit() # closes existing database connections to prevent issues when dropping tables
    db.drop_all()
    db.create_all()
    whooshee.reindex()
    make_admin()
    
    flash("Good job, you successfully broke everything!", "success")

    return redirect("/index/")

#  REMOVE BEFORE LAUNCH!!
@main.route("/refresh")
def test_refresh():
    """A much less dangerous route to update tables."""

    db.create_all()
    os.system(f"flask db migrate -m 'Migration {datetime.utcnow()}'")
    os.system("flask db upgrade")
    whooshee.reindex()
    flash("Tables re-created.", "success")

    return redirect("/index/")

# ----- END: TEST ROUTES ----- #
