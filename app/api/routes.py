from app import db
from app.api import api
from app.api.auth import token_auth
from app.schemas import *
from app.main.crud import add_interpretation, add_question, get_play_by_shortname, add_character
from app.main.forms import play_titles
from app.models import *
from flask import abort, request
from marshmallow import ValidationError


# ----- BEGIN: GET ROUTES ----- #

@api.route("/characters/", methods=['GET'])
@api.route("/characters/<int:id>/", methods=['GET'])
@api.route("/characters/<string:shortname>/", methods=['GET'])
def api_get_characters(id=None, shortname=None):
    """Return character information in JSON format. Results can be narrowed down by character ID or play shortname."""

    if id:
        character = character_schema.dump(Character.query.get_or_404(id))
        return {"character": character}
    elif shortname and shortname in play_titles.keys():
        play = get_play_by_shortname(shortname)
        characters = characters_schema.dump(Character.query.filter(Character.play_id == play.id))
        return {"characters": characters}
    else:
        characters = characters_schema.dump(Character.query.all())
        return {"characters": characters}


@api.route("/questions/", methods=['GET'])
@api.route("/questions/<int:id>/", methods=['GET'])
@api.route("/questions/<string:shortname>/", methods=['GET'])
def api_get_questions(id=None, shortname=None):
    """Return question information in JSON format. Results can be narrowed down by question ID or play shortname."""

    if id:
        question = question_schema.dump(Choice.query.get_or_404(id))
        return {"question": question}
    elif shortname and shortname in play_titles.keys():
        play = get_play_by_shortname(shortname)
        questions = questions_schema.dump(Choice.query.filter(Choice.play_id == play.id))
        return {"questions": questions}
    else:
        questions = questions_schema.dump(Choice.query.all())
        return {"questions": questions}


@api.route("/films/", methods=['GET'])
@api.route("/films/<int:id>/", methods=['GET'])
@api.route("/films/<string:shortname>/", methods=['GET'])
def api_get_films(id=None, shortname=None):
    """Return film information in JSON format. Results can be narrowed down by film ID or play shortname."""

    if id:
        film = film_schema.dump(Film.query.get_or_404(id))
        return {"film": film}
    elif shortname and shortname in play_titles.keys():
        play = get_play_by_shortname(shortname)
        films = films_schema.dump(Film.query.filter(Film.play_id == play.id))
        return {"films": films}
    else:
        films = films_schema.dump(Film.query.all())
        return {"films": films}


@api.route("/interpretations/", methods=['GET'])
@api.route("/interpretations/<int:id>/", methods=['GET'])
@api.route("/interpretations/<string:shortname>/", methods=['GET'])
def api_get_interpretations(id=None, shortname=None):
    """Return interpretation information in JSON format. Results can be narrowed down by interpretation ID or play shortname."""

    if id:
        interpretation = interpretation_schema.dump(Interpretation.query.get_or_404(id))
        return {"interpretation": interpretation}
    elif shortname and shortname in play_titles.keys():
        play = get_play_by_shortname(shortname)
        interpretations = interpretations_schema.dump(Interpretation.query.filter(Interpretation.play_id == play.id))
        return {"interpretations": interpretations}
    else:
        interpretations = interpretations_schema.dump(Interpretation.query.all())
        return {"interpretations": interpretations}


@api.route("/plays/", methods=['GET'])
@api.route("/plays/<int:id>/", methods=['GET'])
def api_get_plays(id=None):
    """Return play information in JSON format."""

    if id:
        play = play_schema.dump(Play.query.get_or_404(id))
        return {"play": play}
    else:
        plays = plays_schema.dump(Play.query.all())
        return {"plays": plays}


@api.route("/scenes/", methods=['GET'])
@api.route("/scenes/<int:id>/", methods=['GET'])
@api.route("/scenes/<string:shortname>/", methods=['GET'])
def api_get_scenes(id=None, shortname=None):
    """Return scene information in JSON format. Results can be narrowed down by scene ID or play shortname."""

    if id:
        scene = scene_schema.dump(Scene.query.get_or_404(id))
        return {"scene": scene}
    elif shortname and shortname in play_titles.keys():
        play = get_play_by_shortname(shortname)
        scenes = scenes_schema.dump(Scene.query.filter(Scene.play_id == play.id))
        return {"scenes": scenes}
    else:
        scenes = scenes_schema.dump(Scene.query.all())
        return {"scenes": scenes}

# ----- END: GET ROUTES ----- #


# ----- BEGIN: POST ROUTES ----- #

@api.route("/characters/", methods=["POST"])
@token_auth.login_required
def api_add_character():
    data = request.get_json()
    if not data:
        return {"message": "No input data given"}, 400

    name = data["name"]
    play_shortname = data["play"]
    play = get_play_by_shortname(play_shortname)
    gender = data["gender"]
    word_count = data["word_count"]
    character = add_character(name=name, play=play, gender=gender, word_count=word_count)

    result = character_schema.dump(Character.query.get(character.id))
    return {"message": "Created new character.", "character": result}


@api.route("/questions/", methods=["POST"])
@token_auth.login_required
def api_add_question():
    data = request.get_json()
    if not data:
        return {"message": "No input data given"}, 400
    title = data["title"]
    play_shortname = data["play"]
    play = get_play_by_shortname(play_shortname)
    description = data["description"]

    question = add_question(title=title, play=play, description=description)

    result = question_schema.dump(Question.query.get(question.id))
    return {"message": "Created new question.", "question": result}


@api.route("/interpretations/", methods=["POST"])
@token_auth.login_required
def api_add_interpretation():
    data = request.get_json()
    if not data:
        return {"message": "No input data given"}, 400

    question_id = data["question"]
    question = Question.query.get(question_id)
    play_shortname = data["play"]
    play = get_play_by_shortname(play_shortname)
    title = data["title"]
    description = data["description"]
    film_id = data["film"]
    film = Film.query.get(film_id)
    time_start = data["time_start"]
    time_end = data["time_end"]

    interpretation = add_interpretation(question=question, play=play, title=title, 
                    description=description, film=film, time_start=time_start, time_end=time_end)

    result = interpretation_schema.dump(Interpretation.query.get(interpretation.id))
    return {"message": "Created new interpretation.", "interpretation": result}

# ----- END: POST ROUTES ----- #