#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for OpenWithDialog improvements.
Tests the orange selection indicator and animations.
"""

import sys
from pathlib import Path

# Add lib directory to path
lib_path = Path(__file__).parent / "lib"
sys.path.insert(0, str(lib_path))

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from lib.openWithDialog import OpenWithDialog
    print("[OK] Successfully imported OpenWithDialog")
except ImportError as e:
    print(f"[ERROR] Error importing OpenWithDialog: {e}")
    sys.exit(1)

def test_dialog():
    """Test the OpenWithDialog with improved UI."""
    app = QApplication(sys.argv)
    
    # Create dialog with sample project info
    dialog = OpenWithDialog(
        parent=None,
        project_path="C:\\test\\project.exe",
        project_name="Test Project"
    )
    
    # Show dialog
    dialog.show()
    
    print("[OK] Dialog launched successfully")
    print("[INFO] Check for:")
    print("  - Orange selection indicator (#FF6B00) on left side")
    print("  - Smooth fade-in animation on dialog open")
    print("  - Smooth selection animation when clicking items")
    print("  - Orange hover states on items")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_dialog()
