"""Professional employee report generation"""

from typing import Dict, Any, List
from pathlib import Path
from core.pdf_engine import PDFEngine
from reports.abstract_report import AbstractReport
from config.logger_config import get_logger

logger = get_logger(__name__)

class EmployeeReportGenerator(AbstractReport):
    """Enterprise employee report generator"""
    
    def __init__(self, output_dir: Path = None):
        super().__init__(
            report_name="Employee Performance Report",
            report_type="employee",
            output_dir=output_dir,
        )
    
    def get_required_fields(self) -> List[str]:
        return ["name", "id", "email", "department", "position"]
    
    def _build_content(self, data: Dict[str, Any], engine: PDFEngine) -> None:
        """Build employee report content"""
        engine.add_title("👔 EMPLOYEE PERFORMANCE REPORT")
        
        engine.add_paragraph(f"<b>Employee:</b> {data.get('name')}<br/>"
                           f"<b>ID:</b> {data.get('id')}<br/>"
                           f"<b>Department:</b> {data.get('department')}<br/>"
                           f"<b>Position:</b> {data.get('position')}")
        
        engine.add_heading("Performance Metrics", level=2)
        
        rating = float(data.get('performance_rating', 0))
        performance = self._get_rating_badge(rating)
        
        table_data = [
            ["Metric", "Value", "Assessment"],
            ["Performance Rating", f"{rating}/5.0", performance],
            ["Salary", f"${data.get('salary', 0):,.2f}", ""],
            ["Years Employed", f"{data.get('years_employed', 0)}", ""],
            ["Status", f"{data.get('status', 'Active')}", ""],
        ]
        
        engine.add_table(table_data)
    
    @staticmethod
    def _get_rating_badge(rating: float) -> str:
        """Get rating badge"""
        if rating >= 4.5:
            return "⭐⭐⭐⭐⭐ Exceptional"
        elif rating >= 4.0:
            return "⭐⭐⭐⭐ Exceeds"
        elif rating >= 3.0:
            return "⭐⭐⭐ Meets"
        return "⭐ Needs Improvement"