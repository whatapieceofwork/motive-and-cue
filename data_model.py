"""Data model."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Film(db.Model):
    """A film adaptation."""

    __tablename__ = "films"

    film_id = db.Column(db.Integer,
                        autoincrement=True,
                        primary_key=True,
                        )
    film_moviedb_id = db.Column(db.Integer,
                        )
    title = db.Column(db.String(50),
                        nullable=False,
                        default="English",
                        )
    year = db.Column(db.Date,
                        nullable=False,
                        )
    language = db.Column(db.String(15),
                        nullable=False,
                        default="English",
                        )
    length = db.Column(db.Interval,
                        )
    director_fname = db.Column(db.String(30),
                        )
    director_lname = db.Column(db.String(30),
                        )

    def __repr__(self):
        return f"<FILM id={self.film_id} {self.year} {self.director_lname}>"


class Actor(db.Model):
    """A single actor. May be cast in multiple parts and multiple movies."""

    actor_id = db.Column(db.Integer,
                        autoincrement=True,
                        primary_key=True,
                        )
    actor_moviedb_id = db.Column(db.Integer,
                        )
    fname = db.Column(db.String(30),
                        )
    lname = db.Column(db.String(30),
                        )
    birthday = db.Column(db.Date
                        )
    gender = db.Column(db.string(10)
                        )

    def __repr__(self):
        return f"<ACTOR id={self.actor_id} {self.fname} {self.lname}>"


class Scene(db.Model):
    """A scene from the play."""

    scene_id = db.Column(db.Integer,
                    autoincrement=True,
                    primary_key=True,
                    )
    act_num = db.Column(db.Integer,
                    nullable=False,
                    )
    scene_num = db.Column(db.Integer,
                    nullable=False,
                    )

    def __repr__(self):
        return f"<SCENE id={self.scene_id} {self.act_num} {self.scene_num}}>"


class ChoicePoint(db.Model):
    """A point in the play where multiple interpretations could be made."""

    choicepoint_id = db.Column(db.Integer,
                        autoincrement=True,
                        primary_key=True,
                        )
    choicepoint_title = (db.String(50),
                        nullable=False,
                        )
    desc = db.Column(db.Text
            )
    # scene = # FOREIGN KEY

    def __repr__(self):
        return f"<CHOICEPOINT id={self.choicepoint_id} {self.choicepoint_title}>"


class Interpretation(db.Model):
    """A film's specific interpretation of a choice point."""

    interpretation_id = db.Column(db.Integer,
                        autoincrement=True,
                        primary_key=True,
                        )
    # film_id = # FOREIGN KEY

   def __repr__(self):
        return f"<INTERPRETATION id={self.interpretation_id} {self.interpretation_title} {#DIRECTORLNAME}}>"


class Character(db.Model):
    """A character from the play."""

    character_id = db.Column(db.Integer,
                    autoincrement=True,
                    primary_key=True,
                    )
    name = db.Column(db.String(25),
                    nullable=False,
                    )
    dies_in_play = db.Column(db.Boolean,
                    )

    def __repr__(self):
        return f"<CHARACTER id={self.character_id} {self.character_name}>"