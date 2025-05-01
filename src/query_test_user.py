from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models import User

# Connect to the SQLite database.
engine = create_engine("sqlite:///app.db", echo=True)

# Create a session.
with Session(engine) as session:
    # Query for the user by username.
    stmt = select(User).where(User.username == "test1")
    result = session.execute(stmt).scalar_one_or_none()

    if result:
        print(f"User found: {result}")
        # Test the password.
        if result.verify_password("test1"):
            print("Password is correct.")
        else:
            print("Password is incorrect.")
    else:
        print("User not found.")
