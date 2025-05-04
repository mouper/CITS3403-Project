import os
from flask import Flask, request
from flask_login import LoginManager
from models import User
from db import db, migrate
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

application = Flask(__name__)

application.config['SECRET_KEY'] = os.environ.get("SECRET_KEY") or "your-secret-key-here"

application.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL") or \
    "sqlite:///" + os.path.join(basedir, "app.db")

application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(application)
migrate.init_app(application, db)

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
