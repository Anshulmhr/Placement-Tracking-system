import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# --- MySQL (SQLAlchemy) Configuration ---
# Using an in-memory SQLite database to simulate core MySQL functionality for development/testing.
# Replace with your actual MySQL URL for production: 
# DATABASE_URL = "mysql+mysqlconnector://user:password@host/dbname"
DATABASE_URL = "sqlite:///./placement.db" 	

# Set connect_args for SQLite only
engine = create_engine(
	DATABASE_URL, connect_args={"check_same_thread": False}, echo=False
)

# Base class for SQLAlchemy declarative models
Base = declarative_base()

# Session Local: Each session instance is a database connection
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# --- MongoDB Configuration (Placeholders) ---
# These are placeholder URLs and database names.
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
MONGO_DB_NAME = "placement_tracker_mongo"
MONGO_COLLECTIONS = {
	"preferences": "user_preferences",
	"analytics": "placement_analytics",
}

# Dependency for FastAPI to get a database session
def get_db():
	"""Provides a transactional database session."""
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

print("Database engine initialized (SQLite simulating MySQL).")
