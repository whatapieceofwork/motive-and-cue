from app import db
from app.api import api
from app.data_schemas import *
from app.main.crud import get_play_by_shortname
from app.main.forms import play_titles
from app.models import *


@api.route("/characters/", methods=['GET'])
@api.route("/characters/<int:id>/", methods=['GET'])
@api.route("/characters/<string:shortname>/", methods=['GET'])
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


@api.route("/questions/", methods=['GET'])
@api.route("/questions/<int:id>/", methods=['GET'])
@api.route("/questions/<string:shortname>/", methods=['GET'])
def api_get_questions(id=None, shortname=None):
    """Return question information in JSON format. Results can be narrowed down by question ID or play shortname."""

    if id:
        question = question_schema.dump(Choice.query.get(id))
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
        film = film_schema.dump(Film.query.get(id))
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
        interpretation = interpretation_schema.dump(Interpretation.query.get(id))
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
        play = play_schema.dump(Play.query.get(id))
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
        scene = scene_schema.dump(Scene.query.get(id))
        return {"scene": scene}
    elif shortname and shortname in play_titles.keys():
        play = get_play_by_shortname(shortname)
        scenes = scenes_schema.dump(Scene.query.filter(Scene.play_id == play.id))
        return {"scenes": scenes}
    else:
        scenes = scenes_schema.dump(Scene.query.all())
        return {"scenes": scenes}