# Packagemaker (Influent Package Maker - IPM) v3.2.5-25.12-17.44

**Packagemaker** is a comprehensive suite for creating, packaging, managing, and distributing Python applications within the **Influent/Fluthin** ecosystem. It streamlines the lifecycle of your apps, from initial project structure creation to final `.iflapp` packaging and distribution.

## ✨ Key Features

### 🚀 Project Creation
- **Automated Structuring**: Generates complete project skeletons with `app`, `assets`, `config`, `docs`, `source`, and `lib` directories.
- **GitHub Verification**: Validates authorship by verifying GitHub usernames (API integration).
- **Icon Customization**: Select custom `.ico` files for your project application.
- **Smart Metadata**: Automatically generates `details.xml` with correlation IDs (SHA256) and version tracking.

### 📦 Compilation & Packaging
- **PyInstaller Integration**: robustly compiles scripts into standalone executables (Windowed/Console).
- **.iflapp Format**: Packages everything into a standardized, compressed `.iflapp` format ready for distribution.
- **Cross-Platform**: Supports Windows and Linux compilation targets.

### 🛠️ Project Management
- **Real-time Explorer**: Watches your project directories for changes instantly.
- **Global Registry**: Lists both local projects and installed apps.
- **One-Click Actions**: Install, Uninstall, Run Scripts, and Build packages directly from the UI.
- **Autocomplete**: Smart suggestions for Publisher and Project Name based on your existing workspace.

### 🎨 Modern UI/UX
- **Fluent Design**: UWP-style input highlighting and modern aesthetics.
- **Responsive Layouts**: clean, organized forms.
- **Taskbar Integration**: Proper window icon management.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- PyQt5
- Requests
- PyInstaller

```bash
pip install PyQt5 requests pyinstaller
```

### Usage
Run the main script:
```bash
python packagemaker.py
```

### Workflow
1. **Create**: Go to the "Crear Proyecto" tab. Enter your company name, app name, version, and GitHub username. Select an icon. Click Create.
2. **Develop**: Navigate to `Documents/Packagemaker Projects/<YourProject>`. Write your code in the generated `.py` script.
3. **Build**: Go to "Construir Paquete". Select your project (autocomplete helps here) and platform. Click Build.
4. **Distribute**: Share the generated `.iflapp` file found in the project directory.

## 📝 License
GNU General Public License v3.
Copyright © 2025 Jesus Quijada.
