import os
from app import create_app, db, login_manager
from app.models import User, Role
from flask import render_template
from flask_login import LoginManager, login_required, set_login_view
from flask_mail import Message
from threading import Thread

app = create_app(os.getenv('FLASK_CONFIG') or "default")
app.app_context().push()
# migrate = Migrate(app, db)

def send_async_email(app, msg):
    from app import mail

    print("Async mail called")

    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):

    print("Send mail called")
    msg = Message(app.config["MAIL_SUBJECT_PREFIX"] + subject, 
                sender=app.config["MAIL_SENDER"], recipients=[to])
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()

    return thr


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover("app/tests")
    unittest.TextTestRunner(verbosity=2).run(tests)