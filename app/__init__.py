from re import escape
from config import config
from flask import Flask, Blueprint
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_required, set_login_view
from flask_login.utils import login_user, current_user, logout_user, login_required
from flask_mail import Mail
from flask_moment import Moment
from flask_msearch import Search
from flask_sqlalchemy import SQLAlchemy
from flask_whooshee import Whooshee
from .models import db, AnonymousUser, whooshee
from sqlalchemy.sql import exists

bootstrap = Bootstrap()
msearch = Search()
login_manager = LoginManager()
mail = Mail()
moment = Moment()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.url_map.strict_slashes = False
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    login_manager.login_message_category = "primary"
    login_manager.login_view = "auth.login"
    login_manager.anonymous_user = AnonymousUser

    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    # msearch.init_app(app)
    whooshee.init_app(app)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix="/api")
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app