import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Not relying on environment variables for the key for marking purposes, since we are not uploading the .env file to the public repository. 
    SECRET_KEY = os.environ.get("SECRET_KEY") or 'dev-key-please-change'

    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")  # your email
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")  # app password or real pass
    MAIL_DEFAULT_SENDER = MAIL_USERNAME

class DeploymentConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True