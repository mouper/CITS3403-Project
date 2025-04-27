from flask_login import UserMixin
from app import login_manager
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password_hash = generate_password_hash(password)  # Auto-hashes passwords

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

# Temporary dev users - test1/test1 will work
users = {
    1: User(1, 'test1', 'test1'),  # Hashed version will be created
    2: User(2, 'admin', 'admin')   # Optional second test user
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))