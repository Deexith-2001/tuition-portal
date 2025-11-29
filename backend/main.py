from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, SessionLocal

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tuition Enrollment API")

# -------------- CORS (Fixes your issue) -----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         # allow all for development
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --------------------------------------------------------

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Tuition enrollment API is running"}

@app.post("/api/enroll", response_model=schemas.EnrollmentOut)
def create_enrollment(data: schemas.EnrollmentCreate, db: Session = Depends(get_db)):
    enrollment = models.Enrollment(
        student_name=data.student_name,
        student_class=data.student_class,
        board=data.board,
        subjects=data.subjects,
        area=data.area,
        phone=data.phone,
        preferred_time=data.preferred_time,
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment

@app.get("/api/enrollments", response_model=list[schemas.EnrollmentOut])
def list_enrollments(db: Session = Depends(get_db)):
    return db.query(models.Enrollment).order_by(models.Enrollment.created_at.desc()).all()
