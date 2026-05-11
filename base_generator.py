"""
Base abstract class for all PDF report generators.
Implements common functionality and enforces interface contracts.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import threading
from enum import Enum

from reportlab.lib.pagesizes import letter, A4, legal
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib import colors

from config.settings import get_settings
from config.constants import ReportStatus, OutputFormat
from config.logger_config import get_logger
from config.exceptions import PDFGenerationError, InvalidOperationError


logger = get_logger(__name__)


class PageSize(Enum):
    """PDF page size enumeration"""
    LETTER = letter
    A4 = A4
    LEGAL = legal


class BaseReportGenerator(ABC):
    """
    Abstract base class for all report generators.
    Provides common functionality and enforces implementation contracts.
    """

    def __init__(
        self,
        report_name: str,
        output_dir: Optional[Path] = None,
        password: Optional[str] = None,
        compress: bool = True,
    ):
        """
        Initialize report generator.

        Args:
            report_name: Name of the report
            output_dir: Output directory for reports
            password: Optional PDF password protection
            compress: Whether to compress PDF
        """
        self.settings = get_settings()
        self.report_name = report_name
        self.output_dir = Path(output_dir or self.settings.REPORTS_DIR)
        self.password = password
        self.compress = compress
        self.status = ReportStatus.PENDING
        self.created_at = datetime.now()
        self._lock = threading.RLock()

        self.logger = get_logger(self.__class__.__name__)
        self.logger.debug(f"Initialized {self.__class__.__name__}")

    @abstractmethod
    def generate(self, data: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """
        Generate report from data.

        Args:
            data: Report data dictionary
            output_file: Optional output file path

        Returns:
            Path to generated PDF file

        Raises:
            PDFGenerationError: If generation fails
        """
        pass

    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data.

        Args:
            data: Data to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        pass

    @abstractmethod
    def get_required_fields(self) -> List[str]:
        """
        Get list of required fields for this report type.

        Returns:
            List of required field names
        """
        pass

    def _ensure_output_directory(self) -> None:
        """Ensure output directory exists"""
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Output directory ensured: {self.output_dir}")
        except Exception as e:
            self.logger.error(f"Failed to create output directory: {e}")
            raise

    def _generate_output_filename(self, prefix: str = None, extension: str = "pdf") -> str:
        """
        Generate unique output filename.

        Args:
            prefix: Optional filename prefix
            extension: File extension

        Returns:
            Generated filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        filename_prefix = prefix or self.report_name.lower().replace(" ", "_")
        return f"{filename_prefix}_{timestamp}.{extension}"

    def _validate_status(self, expected: ReportStatus) -> bool:
        """
        Validate current status.

        Args:
            expected: Expected status

        Returns:
            True if status matches
        """
        return self.status == expected

    def _set_status(self, status: ReportStatus) -> None:
        """
        Set report generation status.

        Args:
            status: New status
        """
        with self._lock:
            old_status = self.status
            self.status = status
            self.logger.debug(f"Status changed: {old_status} -> {status}")

    def get_page_size(self) -> tuple:
        """
        Get PDF page size based on settings.

        Returns:
            ReportLab page size tuple
        """
        page_size_map = {
            "letter": PageSize.LETTER.value,
            "a4": PageSize.A4.value,
            "legal": PageSize.LEGAL.value,
        }
        return page_size_map.get(
            self.settings.PDF_PAGE_SIZE.value,
            PageSize.LETTER.value
        )

    def get_margins(self) -> Dict[str, float]:
        """
        Get PDF margins in points.

        Returns:
            Dictionary with margin values
        """
        inch = 72  # 1 inch = 72 points
        return {
            "top": self.settings.PDF_MARGIN_TOP * inch,
            "bottom": self.settings.PDF_MARGIN_BOTTOM * inch,
            "left": self.settings.PDF_MARGIN_LEFT * inch,
            "right": self.settings.PDF_MARGIN_RIGHT * inch,
        }

    def get_color(self, color_key: str) -> colors.Color:
        """
        Get color by key from settings.

        Args:
            color_key: Color key

        Returns:
            ReportLab Color object
        """
        color_hex = self.settings.color_map.get(color_key, "#000000")
        return colors.HexColor(color_hex)

    def thread_safe_operation(self, operation, *args, **kwargs) -> Any:
        """
        Execute operation in thread-safe manner.

        Args:
            operation: Callable to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Operation result
        """
        with self._lock:
            return operation(*args, **kwargs)

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get report metadata.

        Returns:
            Dictionary with metadata
        """
        return {
            "report_name": self.report_name,
            "generated_at": self.created_at.isoformat(),
            "status": self.status.value,
            "output_directory": str(self.output_dir),
            "password_protected": bool(self.password),
            "compressed": self.compress,
        }

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"{self.__class__.__name__}("
            f"name={self.report_name}, "
            f"status={self.status.value}, "
            f"output_dir={self.output_dir})"
        )