from bs4 import BeautifulSoup
from datetime import datetime
from flask import flash, redirect, render_template, session, url_for, render_template_string
from . import main
from ..decorators import admin_required, permission_required
from app import db

@main.route("/")
@main.route("/index/")
def index():
    from motiveandcue import send_email
    # send_email("motiveandcue@gmail.com", "Test", "testemail")

    return render_template("index.html",
                            current_time=datetime.utcnow())
 
#  REMOVE BEFORE LAUNCH!!
@main.route("/reboot")
# @admin_required
def test_reboot():
    """A wonderfully dangerous route to dump and rebuild the database for testing."""

    db.drop_all()
    db.create_all()
    flash("Good job, you successfully broke everything!", "success")

    return redirect("/index/")