
import os
from app import create_app, db, login_manager
from app.main.crud import get_user
from app.models import *
from flask import render_template
from flask_login import LoginManager, login_required, set_login_view
from flask_mail import Message
from threading import Thread

app = create_app(os.getenv('FLASK_CONFIG') or "default")
app.app_context().push()

# migrate = Migrate(app, db)

@current_app.login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(user_id)
    except:
        return None


def send_async_email(app, msg):
    """Sends a Flask-Mail message asynchronously."""

    from app import mail
    print("Async mail called")

    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    """Creates a Flask-Mail message and passes it to send_async_email."""

    print("Send mail called")
    msg = Message(app.config["MAIL_SUBJECT_PREFIX"] + subject, 
                sender=app.config["MAIL_SENDER"], recipients=[to])
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()

    return thr


@app.shell_context_processor
def make_shell_context():
    """Sets the Flask shell to automatically import database object models."""

    return dict(db=db, User=User, Role=Role, Character=Character, Question=Question, Film=Film, Interpretation=Interpretation, Job=Job, Person=Person, Play=Play, Scene=Scene, Topic=Topic, Quote=Quote, CharacterScene=CharacterScene, SceneQuestion=SceneQuestion, CharacterInterpretation=CharacterInterpretation, SceneInterpretation=SceneInterpretation, PersonJob=PersonJob, CharacterActor=CharacterActor, CharacterTopic=CharacterTopic, SceneTopic=SceneTopic)


@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover("app/tests")
    unittest.TextTestRunner(verbosity=2).run(tests)