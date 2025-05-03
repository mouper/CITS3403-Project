from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from sqlalchemy.sql import func

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    display_name = db.Column(db.Text)
    password_hash = db.Column(db.Text, nullable=False)
    stats_visibility = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=func.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

class Friend(db.Model):
    __tablename__ = 'friends'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    status = db.Column(db.Text, nullable=False)

    __table_args__ = (
        db.CheckConstraint(status.in_(['pending', 'accepted']), name='status_check'),
    )

class Tournament(db.Model):
    __tablename__ = 'tournaments'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    game_type = db.Column(db.Text)
    format = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    is_draft = db.Column(db.Boolean, default=True)
    round_time_minutes = db.Column(db.Integer)
    total_rounds = db.Column(db.Integer)
    include_creator_as_player = db.Column(db.Boolean, default=False)
    start_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, server_default=func.now())

    __table_args__ = (
        db.CheckConstraint(format.in_(['round robin', 'swiss', 'single elimination']), name='format_check'),
    )
