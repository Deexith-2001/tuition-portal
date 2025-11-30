# backend/main.py
import os
import smtplib
from email.message import EmailMessage

from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, SessionLocal

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tuition Enrollment API")

# CORS (allow Netlify + Render)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict to Netlify domain later
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- DB dependency ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- EMAIL SENDER ----------
def send_enrollment_email(enrollment: models.Enrollment):
    """
    Sends an email notification for every new enrollment.
    Uses environment variables:
      SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, EMAIL_FROM, EMAIL_TO
    """

    host = os.getenv("SMTP_HOST")
    port = os.getenv("SMTP_PORT")
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    from_email = os.getenv("EMAIL_FROM") or user
    to_email = os.getenv("EMAIL_TO") or user

    # If anything missing → skip email safely
    if not host or not port or not user or not password or not to_email:
        print("Email not configured — skipping.")
        return

    try:
        port = int(port)
    except:
        port = 587  # default

    # Email body
    msg = EmailMessage()
    msg["Subject"] = f"New Tuition Enrollment — {enrollment.student_name}"
    msg["From"] = from_email
    msg["To"] = to_email

    body = f"""
You have a new tuition enrollment request:

Student Name : {enrollment.student_name}
Class        : {enrollment.student_class}
Board        : {enrollment.board}
Subjects     : {enrollment.subjects}
Area         : {enrollment.area}
Phone        : {enrollment.phone}
Preferred Time: {enrollment.preferred_time}

This email was sent by your Tuition Portal automatically.
"""

    msg.set_content(body)

    # Send email
    try:
        with smtplib.SMTP(host, port, timeout=15) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(msg)
            print("Email sent successfully!")
    except Exception as e:
        print("Email sending failed:", e)


# ---------- ROUTES ----------
@app.get("/")
def home():
    return {"message": "Tuition enrollment API is running"}


@app.post("/api/enroll", response_model=schemas.EnrollmentOut)
def create_enrollment(
    data: schemas.EnrollmentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
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

    # Send email without blocking
    # background_tasks.add_task(send_enrollment_email, enrollment)

    return enrollment


@app.get("/api/enrollments", response_model=list[schemas.EnrollmentOut])
def list_enrollments(db: Session = Depends(get_db)):
    return (
        db.query(models.Enrollment)
        .order_by(models.Enrollment.created_at.desc())
        .all()
    )
