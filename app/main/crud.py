from werkzeug.utils import ImportStringError
from app import db
from app.main.folger_parser import parse_folger_characters, parse_folger_scene_descriptions, parse_folger_scenes
from app.main.forms import *
from app.main.moviedb_parser import parse_moviedb_film_details
from app.models import *
from sqlalchemy.sql import exists
from werkzeug.security import generate_password_hash
import random

# ----- BEGIN USER AUTHENTICATION FUNCTIONS ----- #

def create_user(email, username, password=None, password_hash=None, name=None, about=None):
    """Create and return a new User object."""

    if password:
        password_hash = generate_password_hash(password)
    user = User(email=email, username=username, password_hash=password_hash, name=name, about=about)
    db.session.add(user)
    db.session.commit()

    return user


def get_user(id):
    """Given an ID, return the User object or None."""

    return User.query.get(id)


def get_user_by_email(email):
    """Given an email, return the User obejct or None."""

    return User.query.filter(User.email == email).first()


def get_user_by_username(username):
    """Given a username, return the User object or None."""

    user = User.query.filter(User.username == username).first()
    return user


def get_roles():
    """Update and return the current list of roles."""

    Role.insert_roles()
    roles = Role.query.all()
    return roles

# ----- END USER AUTHENTICATION FUNCTIONS ----- #

# ----- BEGIN: AUTHORIZATION FUNCTIONS ----- #
# Functions related to user accounts and authentication.

def user_email_taken(email):
    """Check if an email is taken and returns True or False."""

    existing_email = db.session.query(exists().where(User.email == email)).scalar()
    
    return existing_email


def username_taken(username):
    """Check if a username is taken and returns True or False."""

    existing_username = db.session.query(exists().where(User.username == username)).scalar()
    
    return existing_username

# ----- END: AUTHORIZATION FUNCTIONS ----- #


# ----- BEGIN: ADD FUNCTIONS ----- #
# For creating new database records

def add_character(name, play, gender=None, word_count=None, img=None):
    """Create and return a new Character database record."""

    character = Character(name=name, gender=gender, play_id=play.id, word_count=word_count, img=img)

    db.session.add(character)
    db.session.commit()

    print(f"********* Created {character} *********")
    return character


def add_all_characters(play):
    """Given a play, create and return a group of new Character database records."""

    characters = parse_folger_characters(play)

    for character_name, word_count in characters.values():
        character = get_character(name=character_name, play=play, word_count=word_count)
        db.session.add(character)
    
    db.session.commit()

    return Character.query.filter(Character.play_id == play.id).all()


def add_question(play, title, description, img=None):
    """Create and return a new Question database record."""

    question = Question(play_id=play.id, title=title, description=description, img=img)

    db.session.add(question)
    db.session.commit()

    print(f"********* Created {question} *********")
    return question


def add_question_character(question, character):
    """Create and return a new CharacterQuestion database record."""

    question_character = CharacterQuestion(question_id=question.id, character_id=character.id)

    db.session.add(question_character)
    db.session.commit()

    print(f"********* Created {question_character} *********")
    return question_character
    
    
def add_question_scene(question, scene):
    """Create and return a new SceneQuestion database record."""

    question_scene = SceneQuestion(question_id=question.id, scene_id=scene.id)

    db.session.add(question_scene)
    db.session.commit()

    print(f"********* Created {question_scene} *********")
    return question_scene


def add_film(play, moviedb_id, imdb_id, title, release_date, language, overview, length, poster_path):
    """Create and return a new Film database record."""

    film = Film(play_id=play.id, moviedb_id=moviedb_id, imdb_id=imdb_id, title=title, release_date=release_date, 
                language=language, overview=overview, length=length, poster_path=poster_path)

    db.session.add(film)
    db.session.commit()

    print(f"Created {film} *********")
    return film


def add_job(title):
    """Create and return a new Job database record."""

    job = Job(title=title)

    db.session.add(job)
    db.session.commit()

    print(f"********* Created {job} *********")
    return job


def add_person_job(film, job, person):
    """Create and return a new PersonJob database record."""

    personjob = PersonJob(film_id=film.id, job_id=job.id, person_id=person.id)
    
    db.session.add(personjob)
    db.session.commit()

    print(f"********* Created {personjob} *********")
    return personjob


def add_interpretation(question, play, title, description, film, time_start, time_end, img):
    """Create and return a new Interpretation database record."""

    interpretation = Interpretation(question_id=question.id, play_id=play.id, film_id=film.id, 
        title=title, description=description, time_start=time_start, time_end=time_end, img=img)

    db.session.add(interpretation)
    db.session.commit()

    print(f"********* Created {interpretation} *********")
    return interpretation


def add_character_interpretation(interpretation, character):
    """Create and return a new CharacterInterpretation database record."""

    character_interpretation = CharacterInterpretation(interpretation_id=interpretation.id, character_id=character.id)

    db.session.add(character_interpretation)
    db.session.commit()

    print(f"********* Created {character_interpretation} *********")
    return character_interpretation


def add_scene_interpretation(interpretation, scene):
    """Create and return a new SceneInterpretation database record."""

    scene_interpretation = SceneInterpretation(interpretation_id=interpretation.id, scene_id=scene.id)

    db.session.add(scene_interpretation)
    db.session.commit()

    print(f"********* Created {scene_interpretation} *********")
    return scene_interpretation


def add_character_actor(person, character_name, film, img=None):
    """Create and return a new CharacterActor database relationship record."""

    play = get_play_by_film(film)
    character = get_character(name=character_name, play=play)

    print(f"**** IN ADD_PART_PLAYED, play = {play}, person={person}, character_name={character_name}")

    character_actor=CharacterActor(person_id=person.id, character_id=character.id, film_id=film.id, img=img)

    db.session.add(character_actor)
    db.session.commit()

    print(f"********* Created {character_actor} *********")
    return character_actor


def add_person(moviedb_id, imdb_id, fname, lname, birthday, gender, photo_path):
    """Create and a return a new Person database record."""

    person = Person(moviedb_id=moviedb_id, imdb_id=imdb_id, fname=fname, lname=lname,
                    birthday=birthday, gender=gender, photo_path=photo_path)

    db.session.add(person)
    db.session.commit()

    print(f"********* Created {person} *********")
    return person


def add_play(title, shortname, img=None):
    """Create and return a new Play database record."""

    play = Play(title=title, shortname=shortname, img=img)
    db.session.add(play)
    db.session.commit()

    print(f"********* Created {play} *********")
    return play


def add_quote(play, character, scene, text, img=None):
    """Create and return a new Quote database record."""

    quote = Quote(play_id=play.id, character_id=character.id, scene_id=scene.id, text=text, img=img)
    db.session.add(quote)
    db.session.commit()


def add_scene(act, scene, play, title, description=None, img=None):
    """Create and return a new Scene database record."""

    scene = Scene(act=act, scene=scene, title=title, description=description, play_id=play.id, img=img)
    db.session.add(scene)
    db.session.commit()

    print(f"********* Created {scene} *********")
    return scene


def add_all_scenes(play):
    """Given a play, create and return new Scene database records."""

    scenes = parse_folger_scenes(play)

    for scene in scenes.values():
        db_scene = get_scene(act=scene["act"], scene=scene["scene"], play=play)
        db.session.add(db_scene)
    
    db.session.commit()

    return Scene.query.filter(Scene.play_id == play.id).all()


def add_topic(title, description, img=None):
    """Create and return a new Topic database record."""

    topic = Topic(title=title, description=description, img=img)

    db.session.add(topic)
    db.session.commit()

    print(f"********* Created {topic} *********")
    return topic

# ----- END: ADD FUNCTIONS ----- #


# ----- BEGIN: GET FUNCTIONS ----- #
# For retrieving existing database records or creating new ones

def get_character(name, play, gender=2, word_count=None, img=None):
    """Given a character name, gender, and play, return the Character object."""

    existing_character = db.session.query(exists().where((Character.name == name) & (Character.play_id == play.id))).scalar()
    
    if existing_character:
        character = Character.query.filter((Character.name == name) & (Character.play_id == play.id)).first()
    else:
        character = add_character(name=name, play=play, gender=gender, word_count=word_count, img=img)
    
    return character


def get_all_characters_by_play(play):
    """Given a play, return any existing related Character objects in the database."""

    existing_characters = db.session.query(exists().where(Character.play_id == play.id)).scalar()

    if existing_characters:
        characters = Character.query.filter(Character.play_id == play.id).order_by(Character.id).all()
    else:
        add_all_characters(play)
        characters = Character.query.filter(Character.play_id == play.id).order_by(Character.id).all()
    return characters


def get_question(play, title):
    """Given a play and question title, return the Question database record."""

    existing_question = db.session.query(exists().where((Question.play_id == play.id) & (Question.title == title))).scalar()

    if existing_question:
        return Question.query.filter((Question.play_id == play.id) & (Question.title == title)).first()
    else:
        return None


def get_all_questions_by_play(play):
    """Given a play, return any existing related Question objects in the database."""

    existing_questions = db.session.query(exists().where(Question.play_id == play.id)).scalar()

    if existing_questions:
        return Question.query.filter(Question.play_id == play.id).all()
    else:
        return None


def get_question_character(question, character):
    """Given a question and character, return or create a CharacterQuestion object."""

    existing_question_character = db.session.query(exists().where((CharacterQuestion.question_id == question.id) & (CharacterQuestion.character_id == character.id))).scalar()

    if existing_question_character:
        question_character = CharacterQuestion.query.filter((CharacterQuestion.question_id == question.id) & (CharacterQuestion.character_id == character.id)).first()
    else:
        question_character = add_question_character(question, character)

    return question_character


def get_question_scene(question, scene):
    """Given a question and scene, return or create a SceneQuestion object."""

    existing_question_scene = db.session.query(exists().where((SceneQuestion.question_id == question.id) & (SceneQuestion.scene_id == scene.id))).scalar()

    if existing_question_scene:
        question_scene = SceneQuestion.query.filter((SceneQuestion.question_id == question.id) & (SceneQuestion.scene_id == scene.id)).first()
    else:
        question_scene = add_question_scene(question, scene)

    return question_scene


def get_interpretation(question, film):
    """Given a question and film, return the related Interpretation object."""

    existing_interpretation = db.query.session(exists().where((Interpretation.question_id == question.id) & (Interpretation.film_id == film.id))).scalar()

    if existing_interpretation:
        return Interpretation.query.filter((Interpretation.question_id == question.id) & (Interpretation.film_id == film.id)).first()
    else:
        return None


def get_all_interpretations_by_play(play):
    """Given a play, return any existing related Interpretation objects in the database."""

    existing_interpretations = db.session.query(exists().where(Interpretation.play_id == play.id)).scalar()

    if existing_interpretations:
        return Interpretation.query.filter(Interpretation.play_id == play.id).all()
    else:
        return None


def get_character_interpretation(interpretation, character):
    """Given an interpretation and character, return or create an CharacterInterpretation object."""

    existing_character_interpretation = db.session.query(exists().where((CharacterInterpretation.interpretation_id == interpretation.id) & (CharacterInterpretation.character_id == character.id))).scalar()

    if existing_character_interpretation:
        character_interpretation = CharacterInterpretation.query.filter((CharacterInterpretation.interpretation_id == interpretation.id) & (CharacterInterpretation.character_id == character.id)).first()
    else:
        character_interpretation = add_character_interpretation(interpretation, character)

    return character_interpretation


def get_scene_interpretation(interpretation, scene):
    """Given an interpretation and scene, return or create an SceneInterpretation object."""

    existing_scene_interpretation = db.session.query(exists().where((SceneInterpretation.interpretation_id == interpretation.id) & (SceneInterpretation.scene_id == scene.id))).scalar()

    if existing_scene_interpretation:
        scene_interpretation = SceneInterpretation.query.filter((SceneInterpretation.interpretation_id == interpretation.id) & (Interpretation.scene_id == scene.id)).first()
    else:
        scene_interpretation = add_scene_interpretation(interpretation, scene)

    return scene_interpretation


def get_job_by_title(title):
    """Given a job title, return the Job object."""

    existing_job = db.session.query(exists().where(Job.title == title)).scalar()

    if existing_job:
        job = Job.query.filter(Job.title == title).first()
    else:
        job = add_job(title)
    
    return job


def get_person_job(person, film, job_title):
    """Given a person, film and job title, return (or create and return) a PersonJob object."""

    job = get_job_by_title(job_title)

    existing_person_job = db.session.query(exists().where((PersonJob.person_id == person.id) & (PersonJob.film_id == film.id) & (PersonJob.job_id == job.id))).scalar()
    
    if existing_person_job:
        person_job = PersonJob.query.filter((PersonJob.person_id == person.id) & (PersonJob.film_id == film.id) & (PersonJob.job_id == job.id)).first()
    else:
        person_job = add_person_job(film, job, person)
    
    return person_job


def get_film(play, moviedb_id, imdb_id, title, release_date, language, overview, length, poster_path):

    existing_film = db.session.query(exists().where(Film.moviedb_id == moviedb_id)).scalar()
    
    if existing_film:
        film = Film.query.filter(Film.moviedb_id == moviedb_id).first()
    else:
        film = add_film(play=play, moviedb_id=moviedb_id, imdb_id=imdb_id, title=title, release_date=release_date, 
                        language=language, length=length, overview=overview, poster_path=poster_path)
    
    return film


def get_film_by_moviedb_id(moviedb_id, play):
    """Given a film's MovieDB ID, return the Film object."""

    existing_film = db.session.query(exists().where(Film.moviedb_id == moviedb_id)).scalar()
    
    if existing_film:
        film = Film.query.filter(Film.moviedb_id == moviedb_id).first()
    else:
        film = parse_moviedb_film_details(moviedb_id, play)
    
    return film


def get_films_by_play(play):
    """Given a play, return the related Film objects."""

    existing_films = db.session.query(exists().where(Film.play_id == play.id)).scalar()
    
    if existing_films:
        return Film.query.filter(Film.play_id == play.id).all()
    else:
        return None


def get_person(moviedb_id, imdb_id, fname, lname, birthday, gender, photo_path):
    """Given a person's information, create (or return) a Person object."""

    existing_person = db.session.query(exists().where((Person.moviedb_id == moviedb_id) & (Person.fname == fname) & (Person.lname == lname))).scalar()

    if existing_person:
        person = Person.query.filter((Person.moviedb_id == moviedb_id) & (Person.fname == fname) & (Person.lname == lname)).first()
    else:
        person = add_person(moviedb_id=moviedb_id, imdb_id=imdb_id, fname=fname, lname=lname,
                    birthday=birthday, gender=gender, photo_path=photo_path)
    
    return person


def get_character_actor(person, character_name, film, img=None):
    """Given a person's information, create (or return) a Person object."""

    play = get_play_by_film(film)
    character = get_character(name=character_name, play=play)

    existing_character_actor = db.session.query(exists().where((CharacterActor.person_id == person.id) & (CharacterActor.character_id == character.id) & (CharacterActor.film_id == film.id))).scalar()

    if existing_character_actor:
        character_actor = CharacterActor.query.filter((CharacterActor.person_id == person.id) & (CharacterActor.character_id == character.id) & (CharacterActor.film_id == film.id)).first()
    else:
        character_actor = add_character_actor(person=person, character_name=character_name, film=film, img=img)
    
    return character_actor


def get_play_by_shortname(shortname):
    """Given a play's shortname, return the play."""

    from app.main.forms import play_titles

    existing_play = db.session.query(exists().where(Play.shortname == shortname)).scalar()

    if existing_play:
        play = Play.query.filter(Play.shortname == shortname).one()
        return play
    elif play_titles.get(shortname):
        play = add_play(play_titles[shortname], shortname)
        return play
    else:
        return None


def get_play_by_title(title):
    """Given a play's complete title, return the play."""

    existing_play = db.session.query(exists().where(Play.title == title)).scalar()

    if existing_play:
        play = Play.query.filter(Play.title == title).first()
    else:
        for shortname, play_title in play_titles.items():
            if title == play_title:
                play = add_play(shortname, play_title)
    
    return play


def get_play_by_film(film):
    """Given a film, return the associated play."""

    play_id = film.play_id
    play = Play.query.filter(Play.id == play_id).first()
    return play


def get_scene(act, scene, play, title=None, description=None, img=None):
    """Given an act, scene, and play, return the appropriate Scene object."""

    existing_scene = db.session.query(exists().where((Scene.act == act) & (Scene.scene == scene) & (Scene.play_id == play.id))).scalar()

    if existing_scene:
        scene = Scene.query.filter((Scene.act == act) & (Scene.scene == scene) & (Scene.play_id == play.id)).first()
        if title != scene.title or description != scene.description or img != scene.img:
            updated_scene = update_scene(scene, title, description, img)
            return updated_scene
        else:
            return scene
    else:
        new_scene = add_scene(act=act, scene=scene, play=play, title=title, description=description, img=img)
        return new_scene


def get_all_scenes_by_play(play):
    """Given a play, return any existing related Scene objects in the database in order of act/scene."""

    existing_scenes = db.session.query(exists().where(Scene.play_id == play.id)).scalar()
    print(f"****************** IN GET_ALL_SCENES, play {play.title} *******************")
    print(f"****************** EXISTING SCENES: {existing_scenes} *******************")

    if existing_scenes:
        scenes = Scene.query.filter(Scene.play_id == play.id).order_by(Scene.act, Scene.scene).all()
    else:
        add_all_scenes(play)
        scenes = Scene.query.filter(Scene.play_id == play.id).order_by(Scene.act, Scene.scene).all()

    return scenes

# ----- END: GET FUNCTIONS ----- #


# ----- BEGIN: UPDATE FUNCTIONS ----- #
# For updating existing database records

def update_character(character, name=None, gender=None, img=None):
    """Given a character, update the existing values."""

    db_character = Character.query.get(character.id)

    if name != None:
        db_character.name = name
    if gender != None:
        db_character.gender = gender
    if img != None:
        db_character.img = img
    
    db.session.merge(db_character)
    db.session.commit()
    return db_character


def update_question(question, title=None, description=None, img=None):
    """Given a question, update the existing values."""

    db_question = Question.query.get(question.id)

    if title != None:
        db_question.title = title
    if description != None:
        db_question.description = description
    if img != None:
        db_question.img = img
    
    db.session.merge(db_question)
    db.session.commit()
    return db_question


def update_interpretation(interpretation, play=None, film=None, title=None, description=None, time_start=None, time_end=None, img=None):
    """Given an interpretation, update the existing values."""

    db_interpretation = Interpretation.query.get(interpretation.id)

    if play != None:
        db_interpretation.play = play
    if title != None:
        db_interpretation.title = title
    if film!= None:
        db_interpretation.film_id = film.id
    if description != None:
        db_interpretation.description = description
    if time_start != None:
        db_interpretation.time_start = time_start
    if time_end != None:
        db_interpretation.time_end = time_end
    if img != None:
        db_interpretation.img = img
    
    db.session.merge(db_interpretation)
    db.session.commit()
    return db_interpretation


def update_scene(scene, title=None, description=None, img=None):
    """Given a scene, update the existing values."""

    db_scene = Scene.query.get(scene.id)

    if title != None:
        db_scene.title = title
    if description != None:
        db_scene.description = description
    if img != None:
        db_scene.img = img
    
    db.session.merge(db_scene)
    db.session.commit()
    return db_scene

# ----- END: UPDATE FUNCTIONS ----- #


# ----- BEGIN: RANDOM FUNCTIONS ----- #
# For returning randomly selected records

def random_scene(play=None):
    """Returns a random scene. Can  be limited by play"""

    if play:
        scenes = Scene.query.filter(Scene.play_id == play.id).all()
    else:
        scenes = Scene.query.all()

    return random.question(scenes)

# ----- BEGIN: RANDOM FUNCTIONS ----- #


# ----- BEGIN: MISC FUNCTIONS ----- #

def calculate_age_during_film(person, film):
    """Given a person and film, calculate the person's age when the film was released."""

    film_release = film.release_date
    birthday = person.birthday
    days_between = film_release - birthday
    age = int(days_between.days/365)

    return age


def seed_play(play):
    scenes = get_all_scenes_by_play(play)
    characters = get_all_characters_by_play(play)


def delete_object(object):
    db.session.add(object)
    db.session.delete(object)


def get_random_image(type):

    options = []
    if type is Film:
        type_has_img = db.session.query(exists().where((type.poster_path != None) & (type.poster_path != "None"))).scalar()
        if type_has_img: 
            options = type.query.filter((type.poster_path != None) & (type.poster_path != "None")).all()
        elif Film.query.all():
            options = random.choice(Film.query.all())
    elif type is Person:
        type_has_img = db.session.query(exists().where((type.photo_path != None) & (type.photo_path != "None"))).scalar()
        if type_has_img: 
            options = type.query.filter((type.photo_path != None) & (type.photo_path != "None")).all()
        elif Person.query.all():
            options = random.choice(Person.query.all())
    else:
        type_has_img = db.session.query(exists().where((type.img != None) & (type.img != "None"))).scalar()
        if type_has_img:
            options = type.query.filter((type.img != None) & (type.img != "None")).all()
        elif type.query.all():
            options = type.query.all()

    if options:
        return random.choice(options)
    else:
        return None

# ----- END: MISC FUNCTIONS ----- #
