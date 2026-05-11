"""
Advanced data management with support for multiple formats.
Handles loading, validation, caching, and persistence.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json
import csv
from io import StringIO
import threading
import hashlib
from datetime import datetime

import pandas as pd

from config.settings import get_settings
from config.constants import DataSourceType
from config.exceptions import (
    FileNotFoundError as FileNotFoundCustomError,
    InvalidFileFormatError,
    FileSizeExceededError,
    ValidationError,
)
from config.logger_config import get_logger
from data.validators import DataValidator
from data.models import StudentModel, EmployeeModel


logger = get_logger(__name__)


class DataManager:
    """
    Enterprise-grade data management system.
    Handles loading, validation, caching, and persistence.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize data manager.

        Args:
            data_dir: Data directory path
        """
        self.settings = get_settings()
        self.data_dir = Path(data_dir or self.settings.DATA_DIR)
        self.records: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self._cache: Dict[str, Tuple[List[Dict], datetime]] = {}
        self.validator = DataValidator()
        self.logger = get_logger(__name__)

    def load_csv(self, filepath: str, validate: bool = True) -> List[Dict[str, Any]]:
        """
        Load data from CSV file.

        Args:
            filepath: Path to CSV file
            validate: Whether to validate data

        Returns:
            List of records

        Raises:
            FileNotFoundError: If file not found
            InvalidFileFormatError: If format invalid
            ValidationError: If validation fails
        """
        try:
            filepath = Path(filepath)

            if not filepath.exists():
                raise FileNotFoundCustomError(str(filepath))

            # Check file size
            file_size_mb = filepath.stat().st_size / (1024 * 1024)
            if file_size_mb > self.settings.MAX_FILE_SIZE_MB:
                raise FileSizeExceededError(
                    str(filepath),
                    self.settings.MAX_FILE_SIZE_MB,
                    file_size_mb,
                )

            self.logger.info(f"Loading CSV file: {filepath}")

            df = pd.read_csv(filepath)
            records = df.to_dict("records")

            if validate:
                records = [self.validator.validate_record(r) for r in records]

            with self._lock:
                self.records = records
                self.metadata = {
                    "source": str(filepath),
                    "source_type": DataSourceType.CSV.value,
                    "loaded_at": datetime.now().isoformat(),
                    "record_count": len(records),
                }

            self.logger.info(f"Loaded {len(records)} records from {filepath}")
            return records

        except Exception as e:
            self.logger.error(f"Error loading CSV: {e}", exc_info=True)
            raise

    def load_json(self, filepath: str, validate: bool = True) -> List[Dict[str, Any]]:
        """
        Load data from JSON file.

        Args:
            filepath: Path to JSON file
            validate: Whether to validate data

        Returns:
            List of records

        Raises:
            FileNotFoundError: If file not found
            ValidationError: If validation fails
        """
        try:
            filepath = Path(filepath)

            if not filepath.exists():
                raise FileNotFoundCustomError(str(filepath))

            # Check file size
            file_size_mb = filepath.stat().st_size / (1024 * 1024)
            if file_size_mb > self.settings.MAX_FILE_SIZE_MB:
                raise FileSizeExceededError(
                    str(filepath),
                    self.settings.MAX_FILE_SIZE_MB,
                    file_size_mb,
                )

            self.logger.info(f"Loading JSON file: {filepath}")

            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            records = data if isinstance(data, list) else [data]

            if validate:
                records = [self.validator.validate_record(r) for r in records]

            with self._lock:
                self.records = records
                self.metadata = {
                    "source": str(filepath),
                    "source_type": DataSourceType.JSON.value,
                    "loaded_at": datetime.now().isoformat(),
                    "record_count": len(records),
                }

            self.logger.info(f"Loaded {len(records)} records from {filepath}")
            return records

        except Exception as e:
            self.logger.error(f"Error loading JSON: {e}", exc_info=True)
            raise

    def load_excel(self, filepath: str, sheet_name: str = 0, validate: bool = True) -> List[Dict[str, Any]]:
        """
        Load data from Excel file.

        Args:
            filepath: Path to Excel file
            sheet_name: Sheet name or index
            validate: Whether to validate data

        Returns:
            List of records
        """
        try:
            filepath = Path(filepath)

            if not filepath.exists():
                raise FileNotFoundCustomError(str(filepath))

            self.logger.info(f"Loading Excel file: {filepath}")

            df = pd.read_excel(filepath, sheet_name=sheet_name)
            records = df.to_dict("records")

            if validate:
                records = [self.validator.validate_record(r) for r in records]

            with self._lock:
                self.records = records
                self.metadata = {
                    "source": str(filepath),
                    "source_type": DataSourceType.XLSX.value,
                    "loaded_at": datetime.now().isoformat(),
                    "record_count": len(records),
                }

            self.logger.info(f"Loaded {len(records)} records from {filepath}")
            return records

        except Exception as e:
            self.logger.error(f"Error loading Excel: {e}", exc_info=True)
            raise

    def add_record(self, record: Dict[str, Any], validate: bool = True) -> bool:
        """
        Add single record.

        Args:
            record: Record dictionary
            validate: Whether to validate

        Returns:
            True if successful
        """
        try:
            if validate:
                record = self.validator.validate_record(record)

            with self._lock:
                self.records.append(record)

            self.logger.info(f"Added record: {record.get('id', 'unknown')}")
            return True

        except Exception as e:
            self.logger.error(f"Error adding record: {e}")
            return False

    def add_records(self, records: List[Dict[str, Any]], validate: bool = True) -> int:
        """
        Add multiple records.

        Args:
            records: List of records
            validate: Whether to validate

        Returns:
            Number of successfully added records
        """
        count = 0
        for record in records:
            if self.add_record(record, validate):
                count += 1
        return count

    def save_csv(self, filepath: str, overwrite: bool = False) -> bool:
        """
        Save data to CSV file.

        Args:
            filepath: Output file path
            overwrite: Whether to overwrite existing file

        Returns:
            True if successful
        """
        try:
            filepath = Path(filepath)

            if filepath.exists() and not overwrite:
                self.logger.warning(f"File exists: {filepath}")
                return False

            filepath.parent.mkdir(parents=True, exist_ok=True)

            df = pd.DataFrame(self.records)
            df.to_csv(filepath, index=False)

            self.logger.info(f"Saved {len(self.records)} records to {filepath}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving CSV: {e}", exc_info=True)
            return False

    def save_json(self, filepath: str, overwrite: bool = False, pretty: bool = True) -> bool:
        """
        Save data to JSON file.

        Args:
            filepath: Output file path
            overwrite: Whether to overwrite existing file
            pretty: Whether to format JSON

        Returns:
            True if successful
        """
        try:
            filepath = Path(filepath)

            if filepath.exists() and not overwrite:
                self.logger.warning(f"File exists: {filepath}")
                return False

            filepath.parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(
                    self.records,
                    f,
                    indent=2 if pretty else None,
                    default=str,
                )

            self.logger.info(f"Saved {len(self.records)} records to {filepath}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving JSON: {e}", exc_info=True)
            return False

    def get_records(self) -> List[Dict[str, Any]]:
        """
        Get all records.

        Returns:
            List of records
        """
        with self._lock:
            return self.records.copy()

    def get_record_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Get record by ID.

        Args:
            record_id: Record ID

        Returns:
            Record dictionary or None
        """
        with self._lock:
            for record in self.records:
                if record.get("id") == record_id:
                    return record.copy()
        return None

    def filter_records(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Filter records by field values.

        Args:
            **kwargs: Field filters

        Returns:
            Filtered records
        """
        with self._lock:
            filtered = []
            for record in self.records:
                if all(record.get(k) == v for k, v in kwargs.items()):
                    filtered.append(record.copy())
            return filtered

    def update_record(self, record_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update record by ID.

        Args:
            record_id: Record ID
            updates: Updates dictionary

        Returns:
            True if successful
        """
        with self._lock:
            for i, record in enumerate(self.records):
                if record.get("id") == record_id:
                    self.records[i].update(updates)
                    self.logger.info(f"Updated record: {record_id}")
                    return True
        return False

    def delete_record(self, record_id: str) -> bool:
        """
        Delete record by ID.

        Args:
            record_id: Record ID

        Returns:
            True if successful
        """
        with self._lock:
            for i, record in enumerate(self.records):
                if record.get("id") == record_id:
                    self.records.pop(i)
                    self.logger.info(f"Deleted record: {record_id}")
                    return True
        return False

    def clear_records(self) -> None:
        """Clear all records"""
        with self._lock:
            self.records.clear()
            self.logger.info("Records cleared")

    def get_summary(self) -> Dict[str, Any]:
        """
        Get data summary statistics.

        Returns:
            Summary dictionary
        """
        with self._lock:
            if not self.records:
                return {
                    "total_records": 0,
                    "fields": [],
                    "metadata": self.metadata,
                }

            return {
                "total_records": len(self.records),
                "fields": list(self.records[0].keys()),
                "metadata": self.metadata,
            }

    def get_duplicate_ids(self) -> List[str]:
        """
        Get IDs that appear multiple times.

        Returns:
            List of duplicate IDs
        """
        with self._lock:
            id_counts = {}
            for record in self.records:
                record_id = record.get("id")
                if record_id:
                    id_counts[record_id] = id_counts.get(record_id, 0) + 1

            return [id for id, count in id_counts.items() if count > 1]

    def get_statistics(self, field: str) -> Dict[str, Any]:
        """
        Get statistics for numeric field.

        Args:
            field: Field name

        Returns:
            Statistics dictionary
        """
        with self._lock:
            values = []
            for record in self.records:
                try:
                    val = float(record.get(field, 0))
                    values.append(val)
                except (ValueError, TypeError):
                    pass

            if not values:
                return {"count": 0}

            return {
                "count": len(values),
                "sum": sum(values),
                "mean": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
            }