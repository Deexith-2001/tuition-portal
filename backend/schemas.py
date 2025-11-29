from pydantic import BaseModel

class EnrollmentCreate(BaseModel):
    student_name: str
    student_class: str
    board: str | None = None
    subjects: str
    area: str
    phone: str
    preferred_time: str | None = None

class EnrollmentOut(EnrollmentCreate):
    id: int

    class Config:
        orm_mode = True
