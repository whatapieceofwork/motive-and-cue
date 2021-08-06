from flask import render_template, request
from app import db
from app.api import api
from app.api.errors import api_error_response
from . import main

def wants_json_response():
    """Returns True if the requesting client is set to prefer JSON over HTML."""

    return request.accept_mimetypes["application/json"] >= request.accept_mimetypes["text/html"]

@api.app_errorhandler(403)
@main.app_errorhandler(403)
def forbidden(e):
    """Returns 403 error if user lacks permissions."""

    if wants_json_response():
        return api_error_response(403)

    title = "Forbidden"
    return render_template("errors/403.html", title=title), 403

@api.app_errorhandler(404)
@main.app_errorhandler(404)
def page_not_found(e):
    """Returns 404 error if page not found."""

    if wants_json_response():
        return api_error_response(404)

    title = "Page Not Found"
    return render_template("errors/404.html", title=title), 404


@api.app_errorhandler(500)
@main.app_errorhandler(500)
def internal_service_error(e):
    """Returns 500 error if internal service error."""

    db.session.rollback()
    if wants_json_response():
        return api_error_response(500)

    title = "Internal Service Error"
    return render_template("errors/500.html", title=title), 500
