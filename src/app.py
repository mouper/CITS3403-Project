from flask import Flask, request, session
from flask_login import LoginManager

application = Flask(__name__)
application.config['SECRET_KEY'] = 'your-secret-key-here'  # For session security

login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'login'

@application.context_processor
def inject_request():
    return dict(request=request)

import routes