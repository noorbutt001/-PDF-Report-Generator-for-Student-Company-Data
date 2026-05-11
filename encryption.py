"""PDF encryption and security utilities"""

from pathlib import Path
from cryptography.fernet import Fernet
from PyPDF2 import PdfReader, PdfWriter
from config.logger_config import get_logger

logger = get_logger(__name__)

class EncryptionManager:
    """Handles PDF encryption and file security"""
    
    def encrypt_pdf(self, pdf_path: str, password: str) -> None:
        """Encrypt PDF with password"""
        try:
            reader = PdfReader(pdf_path)
            writer = PdfWriter()
            
            for page in reader.pages:
                writer.add_page(page)
            
            writer.encrypt(password, algorithm="AES-256")
            
            with open(pdf_path, "wb") as f:
                writer.write(f)
            
            logger.info(f"PDF encrypted: {pdf_path}")
        
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise