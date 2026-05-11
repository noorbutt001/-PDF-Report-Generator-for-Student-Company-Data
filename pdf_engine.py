"""
Core PDF rendering engine using ReportLab.
Handles all PDF generation, styling, and encryption.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

import reportlab
from reportlab.lib.pagesizes import letter, A4, legal
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import reportlab.platypus
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
import io

from config.settings import get_settings
from config.exceptions import PDFGenerationError
from config.logger_config import get_logger
from utils.encryption import EncryptionManager


logger = get_logger(__name__)


class PDFEngine:
    """
    Professional PDF rendering engine.
    Handles document creation, styling, and encryption.
    """

    def __init__(
        self,
        filename: str,
        title: str = "Report",
        author: str = "PDF Report Generator",
        subject: str = "Professional Report",
    ):
        """
        Initialize PDF engine.

        Args:
            filename: Output PDF filename
            title: Document title
            author: Document author
            subject: Document subject
        """
        self.settings = get_settings()
        self.filename = filename
        self.title = title
        self.author = author
        self.subject = subject
        self.elements: List[reportlab.platypus.Flowable] = []
        self.styles = self._create_styles()
        self.logger = get_logger(__name__)

    def _create_styles(self) -> Dict[str, ParagraphStyle]:
        """
        Create custom paragraph styles.

        Returns:
            Dictionary of style objects
        """
        styles = getSampleStyleSheet()

        custom_styles = {
            "title": ParagraphStyle(
                name="CustomTitle",
                parent=styles["Heading1"],
                fontSize=self.settings.FONT_TITLE_SIZE,
                textColor=self.settings.get_color("header"),
                spaceAfter=12,
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
            ),
            "heading": ParagraphStyle(
                name="CustomHeading",
                parent=styles["Heading2"],
                fontSize=self.settings.FONT_HEADING_SIZE,
                textColor=self.settings.get_color("text"),
                spaceAfter=8,
                spaceBefore=8,
                fontName="Helvetica-Bold",
            ),
            "subheading": ParagraphStyle(
                name="CustomSubheading",
                parent=styles["Heading3"],
                fontSize=11,
                textColor=self.settings.get_color("text"),
                spaceAfter=6,
                spaceBefore=6,
                fontName="Helvetica-Bold",
            ),
            "body": ParagraphStyle(
                name="CustomBody",
                parent=styles["BodyText"],
                fontSize=self.settings.FONT_BODY_SIZE,
                textColor=self.settings.get_color("text"),
                spaceAfter=6,
                leading=14,
                alignment=TA_JUSTIFY,
            ),
            "footer": ParagraphStyle(
                name="CustomFooter",
                fontSize=self.settings.FONT_FOOTER_SIZE,
                textColor=colors.HexColor("#7f8c8d"),
                alignment=TA_CENTER,
            ),
        }

        return custom_styles

    def add_title(self, title: str) -> None:
        """
        Add document title.

        Args:
            title: Title text
        """
        para = reportlab.platypus.Paragraph(title, self.styles["title"])
        self.elements.append(para)
        self.elements.append(reportlab.platypus.Spacer(1, 0.3 * reportlab.lib.units.inch))

    def add_heading(self, text: str, level: int = 1) -> None:
        """
        Add section heading.

        Args:
            text: Heading text
            level: Heading level (1-3)
        """
        style_key = {
            1: "heading",
            2: "subheading",
            3: "body",
        }.get(level, "heading")

        para = reportlab.platypus.Paragraph(text, self.styles[style_key])
        self.elements.append(para)
        self.elements.append(reportlab.platypus.Spacer(1, 0.15 * reportlab.lib.units.inch))

    def add_paragraph(self, text: str, style_key: str = "body") -> None:
        """
        Add paragraph text.

        Args:
            text: Paragraph text
            style_key: Style key to use
        """
        para = reportlab.platypus.Paragraph(text, self.styles.get(style_key, self.styles["body"]))
        self.elements.append(para)
        self.elements.append(reportlab.platypus.Spacer(1, 0.1 * reportlab.lib.units.inch))

    def add_table(
        self,
        data: List[List[str]],
        col_widths: Optional[List[float]] = None,
        header_style: bool = True,
    ) -> None:
        """
        Add formatted table.

        Args:
            data: Table data (2D list)
            col_widths: Optional column widths
            header_style: Apply header styling
        """
        if not data:
            self.logger.warning("Empty data provided for table")
            return

        # Create table
        table = reportlab.platypus.Table(data, colWidths=col_widths)

        # Create style commands
        style_commands = [
            # Header style
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor(self.settings.TABLE_HEADER_BG),
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.HexColor(self.settings.TABLE_HEADER_TEXT),
            ),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 11),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            # Body style
            (
                "BACKGROUND",
                (0, 1),
                (-1, -1),
                colors.HexColor(self.settings.TABLE_ROW_BG),
            ),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                colors.HexColor(self.settings.TABLE_ROW_BG),
                colors.HexColor(self.settings.TABLE_ROW_ALT_BG),
            ]),
            # Borders
            (
                "GRID",
                (0, 0),
                (-1, -1),
                self.settings.TABLE_BORDER_WIDTH,
                colors.HexColor(self.settings.TABLE_BORDER_COLOR),
            ),
            ("PADDING", (0, 0), (-1, -1), 8),
        ]

        table.setStyle(reportlab.platypus.TableStyle(style_commands))
        self.elements.append(table)
        self.elements.append(reportlab.platypus.Spacer(1, 0.2 * reportlab.lib.units.inch))

    def add_spacer(self, height: float = 0.2) -> None:
        """
        Add vertical spacing.

        Args:
            height: Height in inches
        """
        self.elements.append(reportlab.platypus.Spacer(1, height * reportlab.lib.units.inch))

    def add_page_break(self) -> None:
        """Add page break"""
        self.elements.append(reportlab.platypus.PageBreak())

    def add_image(
        self,
        image_path: str,
        width: float = 1.5,
        height: Optional[float] = None,
        alignment: str = "center",
    ) -> None:
        """
        Add image to document.

        Args:
            image_path: Path to image file
            width: Image width in inches
            height: Optional image height in inches
            alignment: Image alignment
        """
        try:
            if not Path(image_path).exists():
                self.logger.warning(f"Image file not found: {image_path}")
                return

            img = reportlab.platypus.Image(
                image_path,
                width=width * reportlab.lib.units.inch,
                height=height * reportlab.lib.units.inch if height else None,
            )
            self.elements.append(img)
            self.elements.append(reportlab.platypus.Spacer(1, 0.15 * reportlab.lib.units.inch))

        except Exception as e:
            self.logger.error(f"Failed to add image: {e}")

    def add_footer(
        self,
        left_text: str = "",
        center_text: str = "",
        right_text: str = "",
    ) -> None:
        """
        Add footer with three columns.

        Args:
            left_text: Left-aligned footer text
            center_text: Center-aligned footer text
            right_text: Right-aligned footer text
        """
        self.elements.append(reportlab.platypus.Spacer(1, 0.3 * reportlab.lib.units.inch))

        footer_data = [
            [
                reportlab.platypus.Paragraph(left_text, self.styles["footer"]),
                reportlab.platypus.Paragraph(center_text, self.styles["footer"]),
                reportlab.platypus.Paragraph(right_text, self.styles["footer"]),
            ]
        ]

        footer_table = reportlab.platypus.Table(
            footer_data,
            colWidths=[2 * reportlab.lib.units.inch, 2 * reportlab.lib.units.inch, 2 * reportlab.lib.units.inch],
        )

        footer_table.setStyle(reportlab.platypus.TableStyle([
            ("ALIGN", (0, 0), (0, 0), "LEFT"),
            ("ALIGN", (1, 0), (1, 0), "CENTER"),
            ("ALIGN", (2, 0), (2, 0), "RIGHT"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#7f8c8d")),
        ]))

        self.elements.append(footer_table)

    def generate(
        self,
        output_path: str,
        password: Optional[str] = None,
    ) -> str:
        """
        Generate PDF file.

        Args:
            output_path: Output file path
            password: Optional PDF password

        Returns:
            Path to generated PDF

        Raises:
            PDFGenerationError: If generation fails
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Create PDF document
            doc = reportlab.platypus.SimpleDocTemplate(
                str(output_path),
                pagesize=letter,
                rightMargin=self.settings.PDF_MARGIN_RIGHT * 72,
                leftMargin=self.settings.PDF_MARGIN_LEFT * 72,
                topMargin=self.settings.PDF_MARGIN_TOP * 72,
                bottomMargin=self.settings.PDF_MARGIN_BOTTOM * 72,
                title=self.title,
                author=self.author,
                subject=self.subject,
            )

            # Build PDF
            doc.build(self.elements)

            # Encrypt if password provided
            if password:
                self._encrypt_pdf(output_path, password)

            self.logger.info(f"PDF generated successfully: {output_path}")
            return str(output_path)

        except Exception as e:
            self.logger.error(f"PDF generation failed: {e}", exc_info=True)
            raise PDFGenerationError(f"Failed to generate PDF: {str(e)}", cause=e)

    def _encrypt_pdf(self, pdf_path: Path, password: str) -> None:
        """
        Encrypt PDF with password.

        Args:
            pdf_path: Path to PDF file
            password: Encryption password

        Raises:
            PDFGenerationError: If encryption fails
        """
        try:
            encryption_manager = EncryptionManager()
            encryption_manager.encrypt_pdf(str(pdf_path), password)
            self.logger.info(f"PDF encrypted successfully")

        except Exception as e:
            self.logger.error(f"PDF encryption failed: {e}")
            raise PDFGenerationError(f"Failed to encrypt PDF: {str(e)}", cause=e)

    def clear_elements(self) -> None:
        """Clear all document elements"""
        self.elements.clear()
        self.logger.debug("Document elements cleared")

    def get_element_count(self) -> int:
        """
        Get number of elements in document.

        Returns:
            Element count
        """
        return len(self.elements)