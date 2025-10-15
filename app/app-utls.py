from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.database_utls import User, UserCreate, Company, Drive
from typing import List

# Setup for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str):
	"""Verifies a plain text password against a stored hash."""
	return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
	"""Hashes a plain text password for secure storage."""
	return pwd_context.hash(password)

def get_user_by_email(db: Session, email: str):
	"""Retrieves a user by email address."""
	return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
	"""Creates and persists a new User record."""
	hashed_password = get_password_hash(user.password)
	
	db_user = User(
		full_name=user.full_name,
		email=user.email,
		hashed_password=hashed_password,
		account_type=user.account_type
	)
	try:
		db.add(db_user)
		db.commit()
		# This refresh is crucial for getting the auto-generated ID back
		db.refresh(db_user) 
		return db_user
	except Exception as e:
		# If anything fails during add/commit/refresh, rollback and print to console
		db.rollback()
		print(f"Database error during user creation: {e}")
		# Re-raise the exception so FastAPI can catch it and send a 500 error
		# (Though a non-JSON error is currently what's happening, this is better practice)
		raise
		

def get_drives_by_company_id(db: Session, company_id: int) -> List[Drive]:
	"""Retrieves job drives by company ID."""
	return db.query(Drive).filter(Drive.company_id == company_id).all() 

def get_recommendations(user_id: int) -> List[dict]:
	"""Simulated function for MongoDB recommendation logic."""
	return [
		{"role": "Simulated Data Analyst", "match_score": 0.85},
		{"role": "Simulated Software Engineer", "match_score": 0.79}
	]

def update_user_preference(user_id: int, preference: dict) -> bool:
	"""Simulated function to update user preferences in MongoDB."""
	print(f"MongoDB Simulation: Updated preferences for user {user_id}")
	return True
