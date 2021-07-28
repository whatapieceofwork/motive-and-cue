from flask import render_template
from . import main

@main.app_errorhandler(403)
def forbidden(e):
    """Returns 403 error if user lacks permissions."""

    title = "Forbidden"
    return render_template("errors/403.html", title=title), 403


@main.app_errorhandler(404)
def page_not_found(e):
    """Returns 404 error if page not found."""

    title = "Page Not Found"
    return render_template("errors/404.html", title=title), 404


@main.app_errorhandler(500)
def internal_service_error(e):
    """Returns 500 error if internal service error."""

    title = "Internal Service Error"
    return render_template("errors/500.html", title=title), 500
