import os
from flask import Flask, request
from config import Config, DeploymentConfig
from flask_login import current_user, logout_user
from dotenv import load_dotenv
from db import db, mail, migrate, login_manager

# Load environment variables
load_dotenv()

def create_app(config_class):
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Import models here to avoid circular imports
    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.before_request
    def logout_if_user_missing():
        if current_user.is_authenticated and db.session.get(User, current_user.id) is None:
            logout_user()

    @app.context_processor
    def inject_request():
        return dict(request=request)

    # Register blueprint
    from blueprints import main
    app.register_blueprint(main)
    
    return app

# Create the application instance
application = create_app(DeploymentConfig)

if __name__ == '__main__':
    application.run()
