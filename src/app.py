from flask import Flask, request, session
from flask_login import LoginManager
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import User

application = Flask(__name__)
application.config['SECRET_KEY'] = 'your-secret-key-here'  # For session security

login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'login'

# Set up SQLite engine.
engine = create_engine("sqlite:///app.db")

# Load the user from the database by ID.
@login_manager.user_loader
def load_user(user_id):
    with Session(engine) as session:
        return session.get(User, int(user_id))

@application.context_processor
def inject_request():
    return dict(request=request)

import routes