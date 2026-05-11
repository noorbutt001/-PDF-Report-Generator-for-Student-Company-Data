"""Professional student report generation"""

from typing import Dict, Any, List
from pathlib import Path
from core.pdf_engine import PDFEngine
from reports.abstract_report import AbstractReport
from config.constants import STUDENT_FIELDS, GPA_RATINGS
from config.logger_config import get_logger

logger = get_logger(__name__)

class StudentReportGenerator(AbstractReport):
    """Enterprise student report generator"""
    
    def __init__(self, output_dir: Path = None):
        super().__init__(
            report_name="Student Academic Report",
            report_type="student",
            output_dir=output_dir,
        )
    
    def get_required_fields(self) -> List[str]:
        return ["name", "id", "email", "course"]
    
    def _build_content(self, data: Dict[str, Any], engine: PDFEngine) -> None:
        """Build student report content"""
        engine.add_title("📚 STUDENT ACADEMIC REPORT")
        
        engine.add_paragraph(f"<b>Student:</b> {data.get('name')}<br/>"
                           f"<b>ID:</b> {data.get('id')}<br/>"
                           f"<b>Email:</b> {data.get('email')}<br/>"
                           f"<b>Course:</b> {data.get('course')}")
        
        engine.add_heading("Academic Performance", level=2)
        
        gpa = float(data.get('gpa', 0))
        performance = self._get_performance_badge(gpa)
        
        table_data = [
            ["Metric", "Value", "Status"],
            ["GPA", f"{gpa:.2f}/4.0", performance],
            ["Attendance", f"{data.get('attendance', 0)}%", ""],
            ["Midterm", f"{data.get('midterm', 0)}/100", ""],
            ["Final", f"{data.get('final', 0)}/100", ""],
        ]
        
        engine.add_table(table_data)
    
    @staticmethod
    def _get_performance_badge(gpa: float) -> str:
        """Get performance badge"""
        if gpa >= 3.8:
            return "🌟 Outstanding"
        elif gpa >= 3.5:
            return "✓ Excellent"
        elif gpa >= 3.0:
            return "✓ Good"
        return "→ Needs Improvement"