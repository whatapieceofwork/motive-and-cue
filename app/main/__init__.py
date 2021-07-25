from flask import Blueprint
main = Blueprint("main", __name__)
from . import routes, errors
from ..models import Permission

@main.app_context_processor
def inject_permissions():
    """Makes the Permission class for roles available to all templates."""

    return dict(Permission=Permission)