"""
Abstract report class implementing enterprise patterns.
Provides base functionality for all report types.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from config.settings import get_settings
from config.logger_config import get_logger
from config.constants import ReportStatus  # <-- FIXED: Added this missing import
from core.base_generator import BaseReportGenerator
from core.pdf_engine import PDFEngine
from data.validators import DataValidator


logger = get_logger(__name__)


class AbstractReport(BaseReportGenerator, ABC):
    """
    Abstract base class for all report generators.
    Implements common report generation workflow.
    """

    def __init__(
        self,
        report_name: str,
        report_type: str,
        output_dir: Optional[Path] = None,
        password: Optional[str] = None,
    ):
        """
        Initialize abstract report.

        Args:
            report_name: Report name
            report_type: Type of report
            output_dir: Output directory
            password: Optional PDF password
        """
        super().__init__(
            report_name=report_name,
            output_dir=output_dir,
            password=password,
        )
        self.report_type = report_type
        self.validator = DataValidator()

    @abstractmethod
    def _build_content(self, data: Dict[str, Any], engine: PDFEngine) -> None:
        """
        Build report content.

        Args:
            data: Report data
            engine: PDF engine instance
        """
        pass

    def generate(
        self,
        data: Dict[str, Any],
        output_file: Optional[str] = None,
    ) -> str:
        """
        Generate report.

        Args:
            data: Report data
            output_file: Optional output file path

        Returns:
            Path to generated PDF

        Raises:
            PDFGenerationError: If generation fails
        """
        try:
            self._set_status(ReportStatus.IN_PROGRESS)
            start_time = datetime.now()

            # Validate data
            self.validate_data(data)

            # Ensure output directory
            self._ensure_output_directory()

            # Generate filename
            output_file = output_file or self._generate_output_filename()
            output_path = self.output_dir / output_file

            # Create PDF engine
            engine = PDFEngine(
                filename=str(output_path),
                title=self.report_name,
            )

            # Build content
            self._build_content(data, engine)

            # Generate PDF
            engine.generate(
                output_path=str(output_path),
                password=self.password,
            )

            # Update status
            duration = (datetime.now() - start_time).total_seconds()
            self._set_status(ReportStatus.COMPLETED)

            # Log metadata
            self._save_metadata(output_path, data, duration)

            self.logger.info(f"Report generated: {output_path}")
            return str(output_path)

        except Exception as e:
            self._set_status(ReportStatus.FAILED)
            self.logger.error(f"Report generation failed: {e}", exc_info=True)
            raise

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate report data.

        Args:
            data: Data to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        if not data:
            raise ValueError("Data cannot be empty")

        required = self.get_required_fields()
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        return True

    def _save_metadata(
        self,
        output_path: Path,
        data: Dict[str, Any],
        duration: float,
    ) -> None:
        """
        Save report metadata.

        Args:
            output_path: Output file path
            data: Report data
            duration: Generation duration in seconds
        """
        try:
            file_size_mb = output_path.stat().st_size / (1024 * 1024)

            metadata = {
                "report_id": self.report_name,
                "report_type": self.report_type,
                "generated_at": datetime.now().isoformat(),
                "file_path": str(output_path),
                "file_size_mb": round(file_size_mb, 2),
                "duration_seconds": round(duration, 2),
                "total_records": 1,
            }

            metadata_file = output_path.parent / f"{output_path.stem}_metadata.json"
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

            self.logger.debug(f"Metadata saved: {metadata_file}")

        except Exception as e:
            self.logger.warning(f"Failed to save metadata: {e}")

    def generate_batch(
        self,
        records: List[Dict[str, Any]],
        output_dir: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Generate batch of reports.

        Args:
            records: Records to generate reports for
            output_dir: Output directory

        Returns:
            Batch results dictionary
        """
        output_dir = Path(output_dir or self.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        results = {
            "total": len(records),
            "successful": 0,
            "failed": 0,
            "files": [],
            "errors": [],
            "outputs_dir": str(output_dir) # Added so CLI interface receives this key
        }

        for i, record in enumerate(records, 1):
            try:
                self.logger.info(f"Generating report {i}/{len(records)}")
                file_path = self.generate(record, output_dir)
                results["successful"] += 1
                results["files"].append(file_path)

            except Exception as e:
                self.logger.error(f"Failed to generate report {i}: {e}")
                results["failed"] += 1
                results["errors"].append({
                    "index": i,
                    "record_id": record.get("id"),
                    "error": str(e),
                })

        self.logger.info(
            f"Batch generation completed: "
            f"{results['successful']} successful, "
            f"{results['failed']} failed"
        )

        return results