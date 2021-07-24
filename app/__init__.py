from config import config
from flask import Flask, Blueprint
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_required, set_login_view
from flask_login.utils import login_user, current_user, logout_user, login_required
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.session import object_session
from sqlalchemy.sql import exists
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests

db = SQLAlchemy()
bootstrap = Bootstrap()
login_manager = LoginManager()
mail = Mail()
moment = Moment()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.url_map.strict_slashes = False

    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    login_manager.login_view = "login"

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app