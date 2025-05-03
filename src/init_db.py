from sqlalchemy import create_engine
from models import Base

# Create an SQLite database called 'app.db' in the current folder.
engine = create_engine("sqlite:///app.db")

# Create all tables defined in 'models.py'.
Base.metadata.create_all(engine)

print("Database and tables created successfully.")