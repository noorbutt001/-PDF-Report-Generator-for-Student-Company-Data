"""
Advanced data validation with configurable rules and error handling.
Provides comprehensive validation for student and employee records.
"""

from typing import Dict, Any, List, Optional
import re
from abc import ABC, abstractmethod

from config.constants import STUDENT_FIELDS, EMPLOYEE_FIELDS, ValidationLevel
from config.exceptions import (
    ValidationError,
    InvalidEmailError,
    InvalidGPAError,
    InvalidRatingError,
    MissingRequiredFieldError,
)
from config.logger_config import get_logger


logger = get_logger(__name__)


class FieldValidator(ABC):
    """Abstract base validator for specific field types"""

    @abstractmethod
    def validate(self, value: Any) -> Any:
        """Validate value and return cleaned value"""
        pass


class EmailValidator(FieldValidator):
    """Email field validator"""

    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    def validate(self, value: Any) -> str:
        """Validate email format"""
        if not isinstance(value, str):
            raise InvalidEmailError(str(value))

        if not re.match(self.EMAIL_PATTERN, value):
            raise InvalidEmailError(value)

        return value.lower()


class GPAValidator(FieldValidator):
    """GPA field validator"""

    def validate(self, value: Any) -> float:
        """Validate GPA is between 0.0 and 4.0"""
        try:
            gpa = float(value)
            if not (0.0 <= gpa <= 4.0):
                raise InvalidGPAError(gpa)
            return round(gpa, 2)
        except (ValueError, TypeError):
            raise InvalidGPAError(value)


class RatingValidator(FieldValidator):
    """Performance rating validator"""

    def __init__(self, max_value: float = 5.0):
        self.max_value = max_value

    def validate(self, value: Any) -> float:
        """Validate rating is within range"""
        try:
            rating = float(value)
            if not (0.0 <= rating <= self.max_value):
                raise InvalidRatingError(rating, self.max_value)
            return round(rating, 1)
        except (ValueError, TypeError):
            raise InvalidRatingError(value, self.max_value)


class PercentageValidator(FieldValidator):
    """Percentage field validator"""

    def validate(self, value: Any) -> int:
        """Validate percentage is between 0 and 100"""
        try:
            percentage = int(value)
            if not (0 <= percentage <= 100):
                raise ValueError(f"Percentage must be between 0 and 100, got {percentage}")
            return percentage
        except (ValueError, TypeError):
            raise ValueError(f"Invalid percentage value: {value}")


class StringValidator(FieldValidator):
    """String field validator"""

    def __init__(self, min_length: int = 1, max_length: int = None):
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value: Any) -> str:
        """Validate string length"""
        value = str(value).strip()

        if len(value) < self.min_length:
            raise ValidationError(
                f"String must be at least {self.min_length} characters",
                field="string",
            )

        if self.max_length and len(value) > self.max_length:
            raise ValidationError(
                f"String must not exceed {self.max_length} characters",
                field="string",
            )

        return value


class DataValidator:
    """
    Enterprise validator for complete record validation.
    Supports multiple validation levels and custom rules.
    """

    def __init__(self, level: ValidationLevel = ValidationLevel.STANDARD):
        """
        Initialize validator.

        Args:
            level: Validation level
        """
        self.level = level
        self.email_validator = EmailValidator()
        self.gpa_validator = GPAValidator()
        self.rating_validator = RatingValidator()
        self.percentage_validator = PercentageValidator()
        self.logger = get_logger(__name__)

    def validate_record(
        self,
        record: Dict[str, Any],
        record_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Validate complete record.

        Args:
            record: Record to validate
            record_type: Type of record (student/employee)

        Returns:
            Validated record

        Raises:
            ValidationError: If validation fails
        """
        if not record:
            raise ValidationError("Record is empty or None")

        validated = record.copy()

        # Determine record type if not provided
        if not record_type:
            record_type = self._determine_record_type(record)

        # Validate based on type
        if record_type == "student":
            return self._validate_student_record(validated)
        elif record_type == "employee":
            return self._validate_employee_record(validated)
        else:
            return self._validate_generic_record(validated)

    def _determine_record_type(self, record: Dict[str, Any]) -> str:
        """Determine record type based on fields"""
        if "gpa" in record or "semester" in record:
            return "student"
        elif "department" in record or "position" in record:
            return "employee"
        return "generic"

    def _validate_student_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate student record.

        Args:
            record: Student record

        Returns:
            Validated record
        """
        required_fields = ["name", "id", "email", "course"]

        if self.level == ValidationLevel.STRICT:
            required_fields.extend(["gpa", "attendance", "semester"])

        # Check required fields
        for field in required_fields:
            if not record.get(field):
                raise MissingRequiredFieldError(field)

        # Validate fields
        record["email"] = self.email_validator.validate(record.get("email"))
        record["name"] = StringValidator(max_length=100).validate(record.get("name"))
        record["id"] = StringValidator(max_length=20).validate(record.get("id"))
        record["course"] = StringValidator(max_length=50).validate(record.get("course"))

        if record.get("gpa") is not None:
            record["gpa"] = self.gpa_validator.validate(record["gpa"])

        if record.get("attendance") is not None:
            record["attendance"] = self.percentage_validator.validate(record["attendance"])

        if record.get("semester"):
            record["semester"] = int(record["semester"])

        return record

    def _validate_employee_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate employee record.

        Args:
            record: Employee record

        Returns:
            Validated record
        """
        required_fields = ["name", "id", "email", "department", "position"]

        if self.level == ValidationLevel.STRICT:
            required_fields.extend(["salary", "performance_rating"])

        # Check required fields
        for field in required_fields:
            if not record.get(field):
                raise MissingRequiredFieldError(field)

        # Validate fields
        record["email"] = self.email_validator.validate(record.get("email"))
        record["name"] = StringValidator(max_length=100).validate(record.get("name"))
        record["id"] = StringValidator(max_length=20).validate(record.get("id"))
        record["department"] = StringValidator(max_length=50).validate(record.get("department"))
        record["position"] = StringValidator(max_length=50).validate(record.get("position"))

        if record.get("salary") is not None:
            record["salary"] = float(record["salary"])

        if record.get("performance_rating") is not None:
            record["performance_rating"] = self.rating_validator.validate(
                record["performance_rating"]
            )

        if record.get("years_employed") is not None:
            record["years_employed"] = float(record["years_employed"])

        return record

    def _validate_generic_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate generic record.

        Args:
            record: Generic record

        Returns:
            Validated record
        """
        if self.level == ValidationLevel.STRICT and not record.get("id"):
            raise MissingRequiredFieldError("id")

        if record.get("email"):
            record["email"] = self.email_validator.validate(record["email"])

        return record

    def batch_validate(
        self,
        records: List[Dict[str, Any]],
        record_type: Optional[str] = None,
        skip_errors: bool = False,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Validate batch of records.

        Args:
            records: Records to validate
            record_type: Type of records
            skip_errors: Skip invalid records instead of raising

        Returns:
            Tuple of (valid_records, invalid_records)
        """
        valid = []
        invalid = []

        for i, record in enumerate(records):
            try:
                validated = self.validate_record(record, record_type)
                valid.append(validated)
            except ValidationError as e:
                error_dict = {
                    "index": i,
                    "record": record,
                    "error": str(e),
                }
                invalid.append(error_dict)

                if not skip_errors:
                    raise

                self.logger.warning(f"Skipped invalid record at index {i}: {e}")

        return valid, invalid