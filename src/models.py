from flask_login import UserMixin
#from app import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, Text, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(UserMixin, Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True, nullable=False)
    email = Column(Text, unique=True, nullable=False)
    display_name = Column(Text)
    password_hash = Column(Text, nullable=False)
    stats_visibility = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

#    def __init__(self, id, username, password):
#        self.id = id
#        self.username = username
#        self.password_hash = generate_password_hash(password)  # Auto-hashes passwords
#
#    def verify_password(self, password):
#        return check_password_hash(self.password_hash, password)

# Temporary dev users - test1/test1 will work
#users = {
#    1: User(1, 'test1', 'test1'),  # Hashed version will be created
#    2: User(2, 'admin', 'admin')   # Optional second test user
#}

#@login_manager.user_loader
#def load_user(user_id):
#    return users.get(int(user_id))