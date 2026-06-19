#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Core Updater Module - PackageMaker Updater System

This module provides the core functionality for the PackageMaker updater system,
including GUI windows, workers, system tray integration, and installation logic.
"""

# Core utilities
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

# System tray
from .system_tray import (
    SystemTrayIcon,
    get_tray_icon,
    set_tray_icon,
    get_updater_window,
    set_updater_window,
)

# Workers
from .workers import (
    InstallerWorker,
    IFLAPPInstallerWorker,
    EXEInstallerWorker,
)

# Windows
from .windows import (
    ModernUpdaterWindow,
    IFLAPPInstallerWindow,
    LicenseTermsDialog,
    EXEInstallerWindow,
)

# Installer functions
from .installer import (
    install_iflapp,
    update_app,
    _update_from_exe,
    _update_from_iflapp,
)

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
]

__version__ = '2.1'
