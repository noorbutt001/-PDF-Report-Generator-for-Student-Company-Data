"""Application entry point"""

import sys
from pathlib import Path
from config.settings import get_settings
from config.logger_config import get_logger
from ui.cli_interface import CLIInterface

logger = get_logger(__name__)

def main():
    """Main entry point"""
    try:
        settings = get_settings()
        logger.info(f"Starting {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}")
        
        cli = CLIInterface()
        cli.run()
    
    except KeyboardInterrupt:
        print("\n\n👋 Application terminated by user")
        sys.exit(0)
    
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()  # <-- FIXED: Removed the pip install command from here