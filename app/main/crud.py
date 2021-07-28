from app import db
from ..models import User
from werkzeug.security import generate_password_hash

# ----- BEGIN USER AUTHENTICATION FUNCTIONS ----- #

def create_user(email, username, password=None, password_hash=None, name=None, about=None):
    """Create and return a new User object."""

    if password:
        password_hash = generate_password_hash(password)
    user = User(email=email, username=username, password_hash=password_hash, name=name, about=about)
    db.session.add(user)
    db.commit()

    return user


def get_user(id):
    """Given an ID, return the User object or None."""

    return User.query.get(id)


def get_user_by_email(email):
    """Given an email, return the User obejct or None."""

    return User.query.filter(User.email == email).first()


def get_user_by_username(username):
    """Given a username, return the User object or None."""

    user = User.query.filter(User.username == username).first()
    return user

# ----- END USER AUTHENTICATION FUNCTIONS ----- #

