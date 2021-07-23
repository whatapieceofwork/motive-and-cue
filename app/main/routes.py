from bs4 import BeautifulSoup
from datetime import datetime
from flask import redirect, render_template, session, url_for, render_template_string
from . import main
from .. import db
from ..models import User

@main.route("/")
def index():
    return render_template("index.html")
