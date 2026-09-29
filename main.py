"""
DataSense AI - Main Application Entry Point
AI-Powered Data Analyzer that runs completely offline
"""

import sys
import os
from pathlib import Path

# Set up environment for Windows high DPI
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "Round"

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor

# Import main window
from ui.main_window import MainWindow

# Application metadata
APP_NAME = "DataSense AI"
APP_VERSION = "1.0.0"
APP_AUTHOR = "DataSense AI Team"
APP_DESCRIPTION = "AI-Powered Data Analyzer - Offline & No API Required"


def setup_application_style(app: QApplication) -> None:
    """Configure application-wide styling"""
    app.setStyle("Fusion")
    
    # Color palette based on SPEC.md
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#F8FAFC"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#1A202C"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#F1F5F9"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#1A202C"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#1A202C"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#1A202C"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.Link, QColor("#2D5A87"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#00D4AA"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    
    app.setPalette(palette)
    
    # Set application metadata
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("DataSense AI")
    app.setDesktopFileName("datasense-ai")


def main():
    """Main entry point for the application"""
    # Create application instance
    app = QApplication(sys.argv)
    
    # Apply styling
    setup_application_style(app)
    
    # Set application icon (will use default if not found)
    icon_path = Path(__file__).parent / "assets" / "icon.ico"
    if icon_path.exists():
        from PyQt6.QtGui import QIcon
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Create and show main window
    try:
        window = MainWindow()
        window.show()
        
        # Execute application
        return_code = app.exec()
        
        # Clean exit
        sys.exit(return_code)
        
    except Exception as e:
        # Show error dialog if main window fails
        error_msg = f"Failed to start application:\n\n{str(e)}"
        QMessageBox.critical(None, "Startup Error", error_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()