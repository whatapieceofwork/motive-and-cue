import os
from app import create_app, db
from app.models import User, Role

app = create_app(os.getenv('FLASK_CONFIG') or "default")

