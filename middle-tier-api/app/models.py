from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional, List


# User Models
class UserBase(BaseModel):
    """Base user model with required fields for creation"""
    id : int
    name: str
    email: EmailStr
    passwordHash: str


class UserCreate(UserBase):
    """Model for creating a new user"""
    pass


class User(UserBase):
    """Full user model with all fields including id and timestamps"""
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Syllabus Models
class SyllabusBase(BaseModel):
    """Base syllabus model with required fields for creation"""
    userId: int
    courseCode: str
    courseName: str
    term: str
    rawText: str


class SyllabusCreate(SyllabusBase):
    """Model for creating a new syllabus"""
    pass


class Syllabus(SyllabusBase):
    """Full syllabus model with all fields including id and timestamps"""
    id: Optional[str] = None
    uploadedAt: Optional[datetime] = None

    class Config:
        from_attributes = True


# Tasks Models
class TasksBase(BaseModel):
    """Base tasks model with required fields for creation"""
    syllabusId: int
    taskType: str
    taskName: str
    dueDate: date
    weight: Optional[str] = None
    notes: Optional[str] = None


class TasksCreate(TasksBase):
    """Model for creating a new task"""
    pass


class Tasks(TasksBase):
    """Full tasks model with all fields including id"""
    id: Optional[int] = None

    class Config:
        from_attributes = True

