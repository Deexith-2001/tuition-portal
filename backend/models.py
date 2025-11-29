from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String, nullable=False)
    student_class = Column(String, nullable=False)
    board = Column(String, nullable=True)
    subjects = Column(String, nullable=False)
    area = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    preferred_time = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
