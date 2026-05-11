"""
Pydantic models for data validation and serialization.
Provides strongly-typed, validated data structures.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator
import re

from config.constants import STUDENT_FIELDS, EMPLOYEE_FIELDS
from config.exceptions import (
    InvalidEmailError,
    InvalidGPAError,
    InvalidRatingError,
    MissingRequiredFieldError,
)


class StudentModel(BaseModel):
    """Student data model with validation"""

    name: str = Field(..., min_length=1, max_length=100)
    id: str = Field(..., min_length=1, max_length=20)
    email: EmailStr
    course: str = Field(..., min_length=1, max_length=50)
    semester: int = Field(default=1, ge=1, le=8)
    gpa: float = Field(default=3.0, ge=0.0, le=4.0)
    attendance: int = Field(default=80, ge=0, le=100)
    midterm: float = Field(default=0, ge=0, le=100)
    final: float = Field(default=0, ge=0, le=100)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "id": "STU001",
                "email": "john@example.com",
                "course": "Computer Science",
                "semester": 4,
                "gpa": 3.8,
                "attendance": 95,
                "midterm": 92,
                "final": 90,
            }
        }

    @field_validator("gpa")
    @classmethod
    def validate_gpa(cls, v):
        if not (0.0 <= v <= 4.0):
            raise InvalidGPAError(v)
        return round(v, 2)

    @field_validator("attendance")
    @classmethod
    def validate_attendance(cls, v):
        if not (0 <= v <= 100):
            raise ValueError("Attendance must be between 0 and 100")
        return v

    def get_performance_level(self) -> str:
        """Get performance level based on GPA"""
        if self.gpa >= 3.8:
            return "Outstanding"
        elif self.gpa >= 3.5:
            return "Excellent"
        elif self.gpa >= 3.0:
            return "Good"
        elif self.gpa >= 2.5:
            return "Satisfactory"
        else:
            return "Needs Improvement"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.model_dump(exclude={"created_at", "updated_at"})


class EmployeeModel(BaseModel):
    """Employee data model with validation"""

    name: str = Field(..., min_length=1, max_length=100)
    id: str = Field(..., min_length=1, max_length=20)
    email: EmailStr
    department: str = Field(..., min_length=1, max_length=50)
    position: str = Field(..., min_length=1, max_length=50)
    salary: float = Field(default=50000, ge=0)
    performance_rating: float = Field(default=3.0, ge=0, le=5)
    years_employed: float = Field(default=0, ge=0)
    status: str = Field(default="Active", max_length=20)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "name": "Jane Smith",
                "id": "EMP001",
                "email": "jane@company.com",
                "department": "Engineering",
                "position": "Senior Engineer",
                "salary": 95000,
                "performance_rating": 4.5,
                "years_employed": 7,
                "status": "Active",
            }
        }

    @field_validator("performance_rating")
    @classmethod
    def validate_rating(cls, v):
        if not (0.0 <= v <= 5.0):
            raise InvalidRatingError(v)
        return round(v, 1)

    @field_validator("salary")
    @classmethod
    def validate_salary(cls, v):
        if v < 0:
            raise ValueError("Salary cannot be negative")
        return round(v, 2)

    def get_performance_level(self) -> str:
        """Get performance level based on rating"""
        if self.performance_rating >= 4.5:
            return "Exceptional"
        elif self.performance_rating >= 4.0:
            return "Exceeds Expectations"
        elif self.performance_rating >= 3.0:
            return "Meets Expectations"
        elif self.performance_rating >= 2.0:
            return "Developing"
        else:
            return "Needs Improvement"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.model_dump(exclude={"created_at", "updated_at"})


class BatchReportRequest(BaseModel):
    """Batch report generation request"""

    report_type: str = Field(..., description="Type of report")
    data: List[Dict[str, Any]] = Field(..., description="Data to process")
    output_format: str = Field(default="pdf", description="Output format")
    include_summary: bool = Field(default=True, description="Include summary page")
    password: Optional[str] = Field(default=None, description="PDF password")

    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "report_type": "student",
                "data": [
                    {
                        "name": "John Doe",
                        "id": "STU001",
                        "email": "john@example.com",
                        "course": "CS",
                        "gpa": 3.8,
                    }
                ],
                "output_format": "pdf",
                "include_summary": True,
            }
        }


class ReportMetadata(BaseModel):
    """Report metadata"""

    report_id: str
    report_type: str
    generated_at: datetime
    generated_by: str = Field(default="System")
    total_records: int
    file_path: str
    file_size_mb: float
    duration_seconds: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.model_dump()