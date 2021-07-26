from flask import current_app
from .. import db
from ..models import User, Role
import os
from werkzeug.security import generate_password_hash

def make_admin():
    """Create admin account if it doesn't exist."""
    
    Role.insert_roles()

    email = os.environ.get("ADMIN_EMAIL")
    username = os.environ.get("ADMIN_USERNAME")
    password = os.environ.get("ADMIN_PASS")
    print(f"***************************** {password}")
    password_hash = generate_password_hash(password)
    name = os.environ.get("ADMIN_NAME")
    about = os.environ.get("ADMIN_ABOUT")

    admin = User.query.filter(User.email == email).first()

    if admin:
        return admin
    else:
        admin = User(username=username, email=email, password_hash=password_hash, name=name, about=about)
        db.session.add(admin)
        db.session.commit()
        return admin