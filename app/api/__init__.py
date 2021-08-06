from flask import Blueprint
api = Blueprint("api", __name__)
from . import routes
from app.api import errors, tokens