from flask import jsonify
from app import db
from app.api import api
from app.api.auth import basic_auth

@api.route("/tokens", methods=["POST"])
@basic_auth.login_required
def get_token():
    token = basic_auth.current_user().get_api_token()
    db.session.commit()
    return jsonify({"token": token})