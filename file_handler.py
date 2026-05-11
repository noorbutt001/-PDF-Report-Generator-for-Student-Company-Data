"""File handling utilities"""

from pathlib import Path
from typing import List
import shutil
from config.logger_config import get_logger

logger = get_logger(__name__)

class FileHandler:
    """Handles file operations"""
    
    @staticmethod
    def create_directory(path: Path) -> None:
        """Create directory if not exists"""
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Directory ensured: {path}")
    
    @staticmethod
    def delete_file(path: Path) -> bool:
        """Delete file safely"""
        try:
            if path.exists():
                path.unlink()
                logger.info(f"File deleted: {path}")
            return True
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False
    
    @staticmethod
    def get_file_size_mb(path: Path) -> float:
        """Get file size in MB"""
        return path.stat().st_size / (1024 * 1024)