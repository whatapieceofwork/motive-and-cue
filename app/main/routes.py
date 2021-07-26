from app.main.crud import get_user_by_username
from app.main.errors import page_not_found
from bs4 import BeautifulSoup
from datetime import datetime
from flask import abort, flash, redirect, render_template, session, url_for, render_template_string
from . import main
from ..decorators import admin_required, permission_required
from .. import db
from ..models import User

@main.route("/")
@main.route("/index/")
def index():
    from motiveandcue import send_email
    # send_email("motiveandcue@gmail.com", "Test", "testemail")

    return render_template("index.html",
                            current_time=datetime.utcnow())
 

@main.route("/user/<username>")
def user(username):
    """Given a username in the URL, display user profile page or return 404."""

    user = get_user_by_username(username)
    if not user:
        abort(404)

    title = user.username
    return render_template("user.html", user=user, title=title)


@main.route("/about")
def about():
    """Display the About page."""

    title = "About"
    return render_template("about.html")


#  REMOVE BEFORE LAUNCH!!
@main.route("/reboot")
def test_reboot():
    """A wonderfully dangerous route to dump and rebuild the database for testing."""

    from app.main.seed import make_admin

    db.session.commit() # closes existing database connections to prevent issues when dropping tables
    db.drop_all()
    db.create_all()
    make_admin()
    
    flash("Good job, you successfully broke everything!", "success")

    return redirect("/index/")

#  REMOVE BEFORE LAUNCH!!
@main.route("/refresh")
def test_refresh():
    """A much less dangerous route to update tables."""

    db.create_all()
    flash("Tables re-created.", "success")

    return redirect("/index/")