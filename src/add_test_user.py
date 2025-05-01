from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import User, Base

# Connect to the SQLite database.
engine = create_engine("sqlite:///app.db", echo=True)

# Create a session.
with Session(engine) as session:
    # Create a new user.
    user = User(
        username="test1",
        email="test1@example.com",
        display_name="test1"
    )
    user.set_password("test1")

    # Add and commit.
    session.add(user)
    session.commit()

    print(f"User '{user.username}' added with ID {user.id}")
