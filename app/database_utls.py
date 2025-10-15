from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr
from app.database import Base # Ensure this import is correct

# --- SQLAlchemy ORM Models (MySQL / SQLite) ---

class User(Base):
	__tablename__ = "users"
	
	# CRITICAL FIX: Explicit autoincrement=True for SQLite/MySQL compatibility
	id = Column(Integer, primary_key=True, index=True, autoincrement=True) 
	full_name = Column(String, index=True, nullable=False)
	email = Column(String, unique=True, index=True, nullable=False)
	hashed_password = Column(String, nullable=False)
	account_type = Column(String, default="student", nullable=False) # student, tpo-admin, recruiter
	is_active = Column(Boolean, default=True)

	# Relationships
	applications = relationship("Application", back_populates="user")

class Company(Base):
	__tablename__ = "companies"
	
	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, unique=True, index=True)
	industry = Column(String)
	location = Column(String)
	
	drives = relationship("Drive", back_populates="company")

class Drive(Base):
	__tablename__ = "drives"
	
	id = Column(Integer, primary_key=True, index=True)
	company_id = Column(Integer, ForeignKey("companies.id"))
	role = Column(String)
	package_lpa = Column(Float)
	deadline = Column(DateTime)
	
	company = relationship("Company", back_populates="drives")
	applications = relationship("Application", back_populates="drive")

class Application(Base):
	__tablename__ = "applications"
	
	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey("users.id"))
	drive_id = Column(Integer, ForeignKey("drives.id"))
	status = Column(String, default="pending")
	applied_date = Column(DateTime, default=datetime.utcnow)
	
	user = relationship("User", back_populates="applications")
	drive = relationship("Drive", back_populates="applications")


# --- Pydantic Schemas (Input/Output Validation) ---

class UserCreate(BaseModel):
	full_name: str
	email: EmailStr
	password: str
	account_type: str
	
class UserSchema(BaseModel):
	id: int
	full_name: str
	email: EmailStr
	account_type: str

	class Config:
		from_attributes = True

class CompanyBase(BaseModel):
	name: str
	industry: str
	location: str

class CompanySchema(CompanyBase):
	id: int
	
	class Config:
		from_attributes = True

class DriveBase(BaseModel):
	company_id: int
	role: str
	package_lpa: float
	deadline: datetime

class DriveSchema(DriveBase):
	id: int
	
	class Config:
		from_attributes = True

class ApplicationSchema(BaseModel):
	id: int
	user_id: int
	drive_id: int
	status: str
	applied_date: datetime
	
	class Config:
		from_attributes = True

class UserPreferenceSchema(BaseModel):
	user_id: int
	theme: str = "light"

class AnalyticsRecordSchema(BaseModel):
	metric_name: str
	value: float
	timestamp: datetime