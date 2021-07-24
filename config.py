import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    JSORT_SORT_KEYS = False
    PRESERVE_CONTEXT_ON_EXCEPTION = True
    SECRET_KEY = os.environ.get("FLASK_KEY")
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT")
    SQLALCHEMY_POOL_RECYCLE = 54000 #Recycle connection pool every 15 minutes
    SQLALCHEMY_POOL_SIZE = 10
    
    MAIL_DEBUG = True
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASS")
    MAIL_SUBJECT_PREFIX = "[Motive and Cue] "
    MAIL_SENDER = "Motive and Cue Admin <motiveandcue@gmail.com>"
    MAIL_SUPPRESS_SEND = False

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATION = True

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    pass

config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}