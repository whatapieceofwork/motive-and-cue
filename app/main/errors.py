from flask import render_template
from . import main

@main.app_errorhandler(403)
def forbidden(e):
    """Returns 403 error if user lacks permissions."""

    return render_template("errors/403.html"), 403


@main.app_errorhandler(404)
def page_not_found(e):
    """Returns 404 error if page not found."""

    return render_template("errors/404.html"), 404


@main.app_errorhandler(500)
def internal_service_error(e):
    """Returns 500 error if internal service error."""
    
    return render_template("errors/500.html"), 500
