from bs4 import BeautifulSoup
from datetime import datetime
from flask import redirect, render_template, session, url_for, render_template_string
from . import main


@main.route("/")
def index():
    # from motiveandcue import send_email, mail
    # send_email("motiveandcue@gmail.com", "Test", "testemail")

    return render_template("index.html",
                            current_time=datetime.utcnow())
