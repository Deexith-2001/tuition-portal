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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for now, allow all; you can restrict to Netlify domain later
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

# ---------- Email utility ----------
def send_enrollment_email(enrollment: models.Enrollment) -> None:
    """
    Send a simple email notification to you for each new enrollment.
    Uses environment variables:
      SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, EMAIL_FROM, EMAIL_TO
    """
    host = os.getenv("SMTP_HOST")
    port = os.getenv("SMTP_PORT")
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    from_email = os.getenv("EMAIL_FROM") or user
    to_email = os.getenv("EMAIL_TO") or user

    # If email is not configured, just skip silently
    if not host or not port or not user or not password or not to_email:
        return

    try:
        port = int(port)
    except ValueError:
        port = 587  # default

    msg = EmailMessage()
    msg["Subject"] = f"New tuition enrollment: {enrollment.student_name}"
    msg["From"] = from_email
    msg["To"] = to_email

    body_lines = [
        "You have a new tuition enrollment request:",
        "",
        f"Student Name : {enrollment.student_name}",
        f"Class        : {enrollment.student_class}",
        f"Board        : {enrollment.board or '-'}",
        f"Subjects     : {enrollment.subjects}",
        f"Area         : {enrollment.area}",
        f"Phone        : {enrollment.phone}",
        f"Preferred time: {enrollment.preferred_time or '-'}",
        "",
        "This message was sent automatically from your tuition portal.",
    ]
    msg.set_content("\n".join(body_lines))

    try:
        with smtplib.SMTP(host, port, timeout=15) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(msg)
    except Exception as e:
        # Don’t crash the API if email fails; just log it
        print("Error sending email:", e)


@app.get("/")
def read_root():
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

    # 🔔 Trigger email notification in the background
    background_tasks.add_task(send_enrollment_email, enrollment)

    return enrollment


@app.get("/api/enrollments", response_model=list[schemas.EnrollmentOut])
def list_enrollments(db: Session = Depends(get_db)):
    return (
        db.query(models.Enrollment)
        .order_by(models.Enrollment.created_at.desc())
        .all()
    )
