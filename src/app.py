import os
from flask import Flask, request
from flask_login import LoginManager, current_user, logout_user
from flask_mail import Mail, Message
from models import User
from db import db, migrate
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

application = Flask(__name__)

application.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
application.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT", 587))
application.config['MAIL_USE_TLS'] = True
application.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")  # your email
application.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")  # app password or real pass
application.config['MAIL_DEFAULT_SENDER'] = application.config['MAIL_USERNAME']

mail = Mail(application)

application.config['SECRET_KEY'] = os.environ.get("SECRET_KEY") or "your-secret-key-here"

application.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL") or \
    "sqlite:///" + os.path.join(basedir, "app.db")

application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(application)
migrate.init_app(application, db)

@application.before_request
def logout_if_user_missing():
    if current_user.is_authenticated and db.session.get(User, current_user.id) is None:
        logout_user()

login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@application.context_processor
def inject_request():
    return dict(request=request)

import routes
