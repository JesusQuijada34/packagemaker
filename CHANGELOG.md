# Changelog

All notable changes to this project will be documented in this file.

## [3.2.5-25.12-17.44] - 2025-12-17

### Added
- **Real-time Project Watcher**: The project manager list now updates automatically when files change in the directory.
- **UWP-style Focus**: Input fields now show a vertical accent bar when focused.
- **Icon Selection**: Added a file browser to select custom `.ico` files during project creation.
- **Autocomplete**: Added recursive, partial-match autocomplete for Publisher and Project Name fields in the Build tab.
- **Window Icon**: The application now sets a default window/taskbar icon (`app-icon.ico`).
- **Python Verification**: Added robust checks (including `shutil.which`) to find a valid Python interpreter before running scripts.

### Changed
- **Compilation Engine**: Replaced simple zipping with `FlangCompiler` class (PyInstaller based).
- **Updater Logic**: `updater.py` is now embedded directly into the script and written dynamically, removing the dependency on an external file.
- **UI Layout**: Optimized "Crear Proyecto" tab for better alignment and responsiveness. Inputs now stretch to the right edge.
- **GitHub Verification**: Removed avatar preview to cleaner verification logic. API call now only checks existence.
- **Folder List**: `get_package_list` now scans recursively (using `os.walk`) to find projects in subdirectories.

### Fixed
- **NameError**: Fixed `FocusIndicationFilter` scope issue.
- **Layout**: Fixed "Examinar" button spacing and alignment.
