from flask import current_app
from .. import db
from .crud import create_user, get_user_by_email
from ..models import User, Role
import os
from werkzeug.security import generate_password_hash

def make_admin():
    """Create admin account if it doesn't exist."""
    
    # Update (or create) roles list to be sure it's up to date
    Role.insert_roles()

    email = os.environ.get("ADMIN_EMAIL")
    username = os.environ.get("ADMIN_USERNAME")
    password = os.environ.get("ADMIN_PASS")
    password_hash = generate_password_hash(password)
    name = os.environ.get("ADMIN_NAME")
    about = os.environ.get("ADMIN_ABOUT")

    admin = get_user_by_email(email)

    if admin:
        return admin
    else:
        admin = create_user(username=username, email=email, password_hash=password_hash, name=name, about=about)
        admin.confirmed = True
        db.session.add(admin)
        db.session.commit()
        return admin