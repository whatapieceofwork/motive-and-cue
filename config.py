import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    HEAD_ADMIN = os.environ.get("ADMIN_EMAIL")
    JSORT_SORT_KEYS = False
    PRESERVE_CONTEXT_ON_EXCEPTION = True
    SECRET_KEY = os.environ.get("FLASK_KEY")
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT")
    SQLALCHEMY_POOL_RECYCLE = 54000 #Recycle connection pool every 15 minutes
    SQLALCHEMY_POOL_SIZE = 10
    GOOGLE_SEARCH_API_KEY = os.environ.get("GOOGLE_SEARCH_API_KEY")

    CLOUDINARY_KEY = os.environ.get("CLOUDINARY_KEY")
    CLOUDINARY_KEY_SECRET = os.environ.get("CLOUDINARY_KEY_SECRET")
    CLOUD_NAME = os.environ.get("CLOUD_NAME")
    
    MAIL_DEBUG = True
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASS")
    MAIL_SUBJECT_PREFIX = os.environ.get("MAIL_SUBJECT_PREFIX")
    MAIL_SENDER = os.environ.get("MAIL_SENDER")
    MAIL_SUPPRESS_SEND = False

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL")
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATION = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    pass

config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}