from dotenv import load_dotenv
from sqlalchemy import create_engine  
from sqlalchemy.orm import sessionmaker, declarative_base
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL,pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # define a session factory that will be used to create new sessions for interacting with the database. 
Base = declarative_base() # create a base class for declarative class definitions. All ORM models will inherit from this base class.

# Dependency function to get a database session. This function can be used in FastAPI routes to provide a session for database operations.
def get_db():
    db = SessionLocal()  # create a new session
    try:
        yield db  # yield the session to be used in the route
    finally:
        db.close()  # close the session after the request is done