import os
from flask import Flask, request
from config import Config, DeploymentConfig
from flask_login import LoginManager, current_user, logout_user
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask extensions
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

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

    # Register blueprint
    from blueprints import main
    app.register_blueprint(main)

    @app.before_request
    def logout_if_user_missing():
        if current_user.is_authenticated and db.session.get(User, current_user.id) is None:
            logout_user()

    @app.context_processor
    def inject_request():
        return dict(request=request)
    
    return app

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return db.session.get(User, int(user_id))

# Create the application instance
application = create_app(DeploymentConfig)

if __name__ == '__main__':
    application.run()
