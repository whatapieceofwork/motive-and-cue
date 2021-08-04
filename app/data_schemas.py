from marshmallow import Schema, fields

class PlaySchema(Schema):
    """Marshmallow serialization schema for Play data objects."""

    characters = fields.Nested(lambda: CharacterSchema(many=True, only=["id", "name"]))
    # questions = fields.Nested(lambda: QuestionSchema(many=True, only=["id", "title"]))
    films = fields.Nested(lambda: FilmSchema(many=True, only=["id", "title", "release_date"]))

    class Meta:
        fields = ("id", "title", "characters", "films")
        ordered = True

play_schema = PlaySchema()
plays_schema = PlaySchema(many=True)


class CharacterSchema(Schema):
    """Marshmallow serialization schema for Character data objects."""

    play = fields.Nested(lambda: PlaySchema(only=["id", "title"]))

    class Meta:
        fields = ("id", "name", "gender", "play")
        ordered = True

character_schema = CharacterSchema()
characters_schema = CharacterSchema(many=True)


class QuestionSchema(Schema):
    """Marshmallow serialization schema for Question data objects."""

    play = fields.Nested(lambda: PlaySchema(only=["id", "title"]))

    class Meta:
        fields = ("id", "title", "description", "play")
        ordered = True

question_schema = QuestionSchema()
questions_schema = QuestionSchema(many=True)


class FilmSchema(Schema):
    """Marshmallow serialization schema for Film data objects."""

    play = fields.Nested(lambda: PlaySchema(only=["id", "title"]))

    class Meta:
        fields = ("id", "play", "moviedb_id", "imdb_id", "title", "language", "length", "poster_path", "release_date")
        ordered = True

film_schema = FilmSchema()
films_schema = FilmSchema(many=True)


class InterpretationSchema(Schema):
    """Marshmallow serialization schema for Interpretation data objects."""

    play = fields.Nested(lambda: PlaySchema(only=["id", "title"]))
    question = fields.Nested(lambda: QuestionSchema(only=["id", "title"]))
    film = fields.Nested(lambda: FilmSchema(only=["id", "title", "release_date"]))

    class Meta:
        fields = ("id", "play", "film", "question", "title", "description")
        ordered = True

interpretation_schema = InterpretationSchema()
interpretations_schema = InterpretationSchema(many=True)


class PersonSchema(Schema):
    """Marshmallow serialization schema for Person data objects."""

    class Meta:
        fields = ("id", "moviedb_id", "imdb_id", "fname", "lname", "gender", "photo_path", "birthday")
        ordered = True

person_schema = PersonSchema()
people_schema = PersonSchema(many=True) 


class JobSchema(Schema):
    """Marshmallow serialization schema for Job data objects."""

    people = fields.Nested(lambda: PersonSchema(only=["id", "fname", "lname"]))

    class Meta:
        fields = ("id", "title", "people")
        ordered = True

job_schema = JobSchema()
jobs_schema = JobSchema(many=True)


class SceneSchema(Schema):
    """Marshmallow serialization schema for Scene data objects."""

    play = fields.Nested(lambda: PlaySchema(only=["id", "title"]))

    class Meta:
        fields = ("id", "play", "act", "scene", "title", "description")
        ordered = True

scene_schema = SceneSchema()
scenes_schema = SceneSchema(many=True)


class TopicSchema(Schema):
    """Marshmallow serialization schema for Topic data objects."""

    scenes = fields.Nested(lambda: SceneSchema(many=True, only=["id", "play", "act", "scene"]))
    characters = fields.Nested(lambda: CharacterSchema(many=True, only=["id", "name"]))

    class Meta:
        fields = ("id", "title", "description", "scenes", "characters")
        ordered = True

topic_schema = TopicSchema()
topics_schema = TopicSchema(many=True)


class QuoteSchema(Schema):
    """Marshmallow serialization schema for Quote data objects."""

    character = fields.Nested(lambda: CharacterSchema(only=["id", "name"]))
    scene = fields.Nested(lambda: SceneSchema(only=["id", "act", "scene"]))
    play = fields.Nested(lambda: PlaySchema(only=["id", "title"]))

    class Meta:
        fields = ("id", "text", "character", "scene", "play")
        ordered = True

quote_schema = QuoteSchema()
quotes_schema = QuoteSchema(many=True)


# class UserSchema(Schema):
#     id = fields.Int(dump_only=True)
#     username = fields.Str()
#     email = fields.Email()