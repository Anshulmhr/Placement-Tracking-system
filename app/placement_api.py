import os
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

# Import database configuration
from app.database import Base, engine, get_db, SessionLocal
from app.database_utls import (
    UserCreate, UserSchema, CompanyBase, CompanySchema,
    DriveBase, DriveSchema, ApplicationSchema,
    UserPreferenceSchema, AnalyticsRecordSchema,
    User, Company, Drive
)
from app.app_utls import (
    get_user_by_email, create_user, verify_password,
    get_drives_by_company_id, get_recommendations, update_user_preference
)


# --- Directory Setup for Static Files ---
# Define the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent
# Define the location of the HTML templates
TEMPLATES_DIR = BASE_DIR / "templates"


app = FastAPI(
    title="Placement Tracker API",
    description="Backend service for managing campus placements and providing analytics.",
    version="1.0.0"
)


# --- Dependency: Database Session ---
def get_db_session():
    """Provides a transactional database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- FRONTEND ROUTING (Serves HTML Pages) ---

# Helper function to serve specific HTML files
def serve_html(filename: str):
    file_path = TEMPLATES_DIR / filename
    if not file_path.exists():
        return HTMLResponse(content="<h1>404 Not Found: Page Missing</h1>", status_code=404)
    return FileResponse(file_path)

# Root route (index.html)
@app.get("/", response_class=FileResponse)
async def serve_index():
    return serve_html("index.html")

# Explicit routes for all other HTML files (MUST use the file name as the path)
@app.get("/login.html", response_class=FileResponse)
async def serve_login():
    return serve_html("login.html")

@app.get("/register.html", response_class=FileResponse)
async def serve_register():
    return serve_html("register.html")

@app.get("/dashboard.html", response_class=FileResponse)
async def serve_dashboard():
    return serve_html("dashboard.html")

@app.get("/profile.html", response_class=FileResponse)
async def serve_profile():
    return serve_html("profile.html")
    
@app.get("/job-drives.html", response_class=FileResponse)
async def serve_job_drives():
    return serve_html("job-drives.html")

@app.get("/schedules.html", response_class=FileResponse)
async def serve_schedules():
    return serve_html("schedules.html")

@app.get("/analytics.html", response_class=FileResponse)
async def serve_analytics():
    return serve_html("analytics.html")

@app.get("/documents.html", response_class=FileResponse)
async def serve_documents():
    return serve_html("documents.html")
    
@app.get("/interview-prep.html", response_class=FileResponse)
async def serve_interview_prep():
    return serve_html("interview-prep.html")


# --- API Endpoint 1: User Authentication and Registration ---

@app.post("/users/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db_session)):
    """Registers a new user (Student, TPO Admin, or Recruiter)."""
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return create_user(db, user)

@app.post("/users/login")
def login_user(user_data: UserSchema, db: Session = Depends(get_db_session)):
    """Logs in a user and returns successful login message (simulated token)."""
    
    # We expect user_data to contain email and password fields for validation
    db_user = get_user_by_email(db, email=user_data.email)
    
    # Check if user exists AND if password is correct
    if not db_user or not verify_password(user_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Note: The Pydantic model UserSchema requires email, password, and account_type for validation, 
    # but the API only needs email/password for input. We use a generic UserSchema here, 
    # but the client-side JavaScript sends only necessary fields.
    
    # In a real app, you would generate and return a JWT token here
    return {
        "message": "Login successful", 
        "user_id": db_user.id, 
        "account_type": db_user.account_type, 
        "token": "SIMULATED_TOKEN"
    }

# --- API Endpoint 2: Core Data (Drives) CRUD (Example) ---

@app.post("/drives/", response_model=DriveSchema)
def create_drive(drive: DriveBase, db: Session = Depends(get_db_session)):
    """Creates a new job drive (Admin/TPO function)."""
    
    # Simple validation: check if company exists
    company = db.query(Company).filter(Company.id == drive.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company ID not found.")

    # Create drive
    db_drive = Drive(**drive.model_dump())
    db.add(db_drive)
    db.commit()
    db.refresh(db_drive)

    return db.query(Drive).filter(Drive.id == db_drive.id).first()


@app.get("/drives/{company_id}", response_model=List[DriveSchema])
def get_drives_by_company(company_id: int, db: Session = Depends(get_db_session)):
    """Gets all job drives for a specific company."""
    # Placeholder implementation
    drives = db.query(Drive).filter(Drive.company_id == company_id).all()
    if not drives:
        raise HTTPException(status_code=404, detail="No drives found for this company.")
    return drives

# --- API Endpoint 3: MongoDB Interaction (User Preferences/Recommendations) ---

@app.get("/recommendations/{user_id}")
def get_user_recommendations(user_id: int):
    """Retrieves simulated job recommendations for a user."""
    # This calls the placeholder function using the MongoDB context
    recommendations = get_recommendations(user_id)
    return {"user_id": user_id, "recommendations": recommendations}

@app.put("/users/{user_id}/preferences", status_code=status.HTTP_200_OK)
def update_preferences(user_id: int, preference: UserPreferenceSchema):
    """Updates user preferences in the MongoDB collection."""
    # Ensure user_id in path and body match
    if user_id != preference.user_id:
        raise HTTPException(status_code=400, detail="User ID mismatch in path and body.")
    
    # This calls the placeholder function using the MongoDB context
    update_user_preference(user_id, preference.model_dump())
    return {"message": "User preferences updated (MongoDB simulated)", "data": preference.model_dump()}


# --- Initial Data Setup (For Testing Purposes) ---
@app.on_event("startup")
def startup_event():
    # 1. Create SQL database tables
    Base.metadata.create_all(bind=engine)

    # 2. Add initial dummy data
    db = SessionLocal()
    if not db.query(Company).first():
        print("Creating initial company and drive data...")
        c1 = Company(name="TechCorp Solutions", industry="IT", location="Pune")
        db.add(c1)
        db.commit()
        db.refresh(c1)

        d1 = Drive(company_id=c1.id, role="Software Intern", package_lpa=6.5, deadline=datetime.strptime('2025-11-01', '%Y-%m-%d'))
        db.add(d1)
        db.commit()
        print("Initial data created successfully.")
    db.close()
