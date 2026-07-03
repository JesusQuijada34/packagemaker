#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Core Updater Module - PackageMaker Updater System

This module provides the core functionality for the PackageMaker updater system,
including GUI windows, workers, system tray integration, and installation logic.
"""

# Core utilities - these work without PyQt6
from .core import (
    log,
    _rXml,
    _rXml_r,
    _fR,
    _fR_exe,
    cache_get,
    cache_set,
    cache_clear,
    KillerLogic,
    XML_PATH,
    LOG_PATH,
    CHECK_INTERVAL,
    GITHUB_API,
)

# System tray - safe import with fallback
try:
    from .system_tray import (
        SystemTrayIcon,
        get_tray_icon,
        set_tray_icon,
        get_updater_window,
        set_updater_window,
    )
except ImportError:
    # PyQt6 not available - provide dummy classes
    SystemTrayIcon = object
    def get_tray_icon(): return None
    def set_tray_icon(*args): pass
    def get_updater_window(): return None
    def set_updater_window(*args): pass

# Workers - safe import with fallback
try:
    from .workers import (
        InstallerWorker,
        IFLAPPInstallerWorker,
        EXEInstallerWorker,
    )
except ImportError:
    # PyQt6 not available - provide dummy classes
    class InstallerWorker:
        finished = None
        progress = None
        status = None
        def __init__(self, *args, **kwargs): pass
        def run(self): pass
    IFLAPPInstallerWorker = InstallerWorker
    EXEInstallerWorker = InstallerWorker

# Windows - safe import with fallback
try:
    from .windows import (
        ModernUpdaterWindow,
        IFLAPPInstallerWindow,
        LicenseTermsDialog,
        EXEInstallerWindow,
    )
except ImportError:
    # PyQt6 not available - provide dummy classes
    ModernUpdaterWindow = object
    IFLAPPInstallerWindow = object
    LicenseTermsDialog = object
    EXEInstallerWindow = object

# Installer functions - safe import with fallback
try:
    from .installer import (
        install_iflapp,
        update_app,
        _update_from_exe,
        _update_from_iflapp,
        sync_templates_to_local,
        get_templates_source_dir,
        get_templates_target_dir,
    )
except ImportError:
    # Fallback functions when PyQt6 is not available
    def install_iflapp(*args, **kwargs):
        raise ImportError("PyQt6 is required for installation GUI")
    def update_app(*args, **kwargs):
        raise ImportError("PyQt6 is required for update functionality")
    def sync_templates_to_local():
        """Fallback: sincronizar plantillas (requiere coreUpdater)"""
        return False, "PyQt6 required for template sync", []
    def get_templates_source_dir(): return None
    def get_templates_target_dir(): return None
    _update_from_exe = None
    _update_from_iflapp = None

__all__ = [
    # Core
    'log',
    '_rXml',
    '_rXml_r',
    '_fR',
    '_fR_exe',
    'cache_get',
    'cache_set',
    'cache_clear',
    'KillerLogic',
    'XML_PATH',
    'LOG_PATH',
    'CHECK_INTERVAL',
    'GITHUB_API',
    # System tray
    'SystemTrayIcon',
    'get_tray_icon',
    'set_tray_icon',
    'get_updater_window',
    'set_updater_window',
    # Workers
    'InstallerWorker',
    'IFLAPPInstallerWorker',
    'EXEInstallerWorker',
    # Windows
    'ModernUpdaterWindow',
    'IFLAPPInstallerWindow',
    'LicenseTermsDialog',
    'EXEInstallerWindow',
    # Installer
    'install_iflapp',
    'update_app',
    '_update_from_exe',
    '_update_from_iflapp',
    'sync_templates_to_local',
    'get_templates_source_dir',
    'get_templates_target_dir',
]

__version__ = '2.2'
