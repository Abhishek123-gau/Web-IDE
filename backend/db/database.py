import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Create a local SQLite database file named app.db in the backend folder
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "app.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# check_same_thread=False is needed for SQLite in FastAPI since requests can come from different threads
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
