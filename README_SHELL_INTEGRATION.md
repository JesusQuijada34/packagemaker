# 🚀 Integración Shell para Influent Package Maker

> Sistema completo de integración con Windows Shell que permite acceder a todas las funcionalidades de IPM directamente desde el explorador de archivos.

## ✨ Características Principales

- 🖱️ **Menús Contextuales**: Acceso rápido desde el explorador de Windows
- 🔧 **MoonFix**: Sistema inteligente de reparación automática de proyectos
- 📦 **Gestión de Paquetes**: Instalación y gestión de paquetes .iflapp
- ⚙️ **Archivos .mexf**: Sistema de definición de extensiones personalizado
- 💻 **CLI Completa**: Todos los comandos disponibles desde terminal
- 🎨 **GUI Integrada**: Diálogos especializados con diseño moderno

## 📥 Instalación Rápida

### Método 1: Script Batch (Recomendado)
```bash
INSTALL_SHELL.bat
```

### Método 2: Python
```bash
python install_integration.py
```

### Método 3: Archivo de Registro
1. Edita `install_shell_integration.reg` con tus rutas
2. Doble clic en el archivo
3. Acepta el mensaje de confirmación

## 🎯 Uso Rápido

### Crear un Proyecto
```
Clic derecho en carpeta → "Crear Proyecto Aquí"
```

### Compilar un Proyecto
```
Clic derecho en carpeta → "Compilar Proyecto"
```

### Reparar un Proyecto
```
Clic derecho en carpeta → "Reparar Proyecto (MoonFix)"
```

### Instalar un Paquete
```
Clic derecho en archivo.iflapp → "Instalar Paquete"
```

## 💻 Comandos CLI

```bash
# Gestión de proyectos
packagemaker.exe --create-project "C:\Ruta"
packagemaker.exe --compile-project "C:\Ruta"
packagemaker.exe --repair-project "C:\Ruta"

# Gestión de paquetes
packagemaker.exe --install-package "archivo.iflapp"
packagemaker.exe --install-folder "C:\Carpeta"

# Gestión de extensiones
packagemaker.exe --install-mexf "archivo.mexf"
packagemaker.exe --create-mexf "C:\Destino"

# Gestión de integración
packagemaker.exe --install-shell
packagemaker.exe --uninstall-shell
```

## 🔧 MoonFix - Reparación Automática

MoonFix analiza y repara proyectos automáticamente:

- ✅ Verifica estructura de carpetas
- ✅ Crea archivos de configuración faltantes
- ✅ Valida dependencias
- ✅ Detecta archivos principales
- ✅ Actualiza configuraciones obsoletas

```
Clic derecho en proyecto → "Reparar Proyecto (MoonFix)"
```

## 📄 Archivos .mexf

Los archivos .mexf permiten definir extensiones personalizadas:

```json
{
    "version": "1.0",
    "app_name": "Mi App",
    "extensions": [...],
    "context_menus": [...],
    "file_associations": [...]
}
```

Ver `example.mexf` para un ejemplo completo.

## 📚 Documentación

- 📖 [QUICK_START.md](QUICK_START.md) - Guía de inicio rápido
- 📘 [SHELL_INTEGRATION.md](SHELL_INTEGRATION.md) - Documentación completa
- 🐛 [DEBUG_GUIDE.md](DEBUG_GUIDE.md) - Guía de debugging
- 📋 [IMPLEMENTACION_COMPLETA.md](IMPLEMENTACION_COMPLETA.md) - Detalles de implementación
- 🗂️ [ESTRUCTURA_PROYECTO.txt](ESTRUCTURA_PROYECTO.txt) - Estructura visual

## 🧪 Testing

```bash
python test_shell_integration.py
```

25 tests unitarios incluidos:
- ✅ ShellIntegration (8 tests)
- ✅ MEXFHandler (8 tests)
- ✅ CLIIntegration (9 tests)

## 🗑️ Desinstalación

### Método 1: Script Batch
```bash
UNINSTALL_SHELL.bat
```

### Método 2: Python
```bash
python uninstall_integration.py
```

### Método 3: Archivo de Registro
```bash
# Doble clic en:
uninstall_shell_integration.reg
```

## 🛠️ Solución de Problemas

### Los menús no aparecen
```bash
taskkill /f /im explorer.exe
start explorer.exe
```

### Error de permisos
Ejecuta como administrador:
```
Clic derecho en INSTALL_SHELL.bat → "Ejecutar como administrador"
```

### Más ayuda
Consulta [DEBUG_GUIDE.md](DEBUG_GUIDE.md) para soluciones detalladas.

## 📋 Requisitos

- Windows 7 o superior
- Python 3.7+
- PyQt5
- leviathan-ui
- Permisos de administrador (para instalación)

## 🗂️ Estructura de Archivos

```
packagemaker/
├── shell_integration.py          # Módulo principal
├── cli_handler.py                # Manejador CLI
├── install_integration.py        # Instalador
├── uninstall_integration.py      # Desinstalador
├── test_shell_integration.py     # Tests
├── example.mexf                  # Ejemplo MEXF
├── *.reg                         # Archivos de registro
├── *.bat                         # Scripts batch
└── *.md                          # Documentación
```

## 🎨 Capturas de Pantalla

### Menú Contextual
```
📁 Mi Proyecto
   ├── 🆕 Crear Proyecto Aquí
   ├── 📦 Instalar como Fluthin Package
   ├── 🔨 Compilar Proyecto
   └── 🔧 Reparar Proyecto (MoonFix)
```

### MoonFix en Acción
```
=== MoonFix - Sistema de Reparación Automática ===
[1/5] Verificando estructura de carpetas...
  ✓ Carpeta OK: app
  ✓ Carpeta OK: assets
  ⚠ Carpeta faltante: config - CREANDO...
  ✓ Carpeta creada: config
[2/5] Verificando archivos de configuración...
  ✓ Archivo OK: details.xml
[3/5] Verificando dependencias...
  ✓ Archivo OK: lib/requirements.txt
[4/5] Verificando archivos principales...
  ✓ Archivo principal encontrado: main.py
[5/5] Finalizando reparación...
=== Reparación Completada ===
```

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📝 Changelog

### v1.0.0 (Marzo 2026)
- ✨ Implementación inicial
- ✅ Menús contextuales completos
- ✅ Sistema MoonFix
- ✅ Soporte para archivos .mexf
- ✅ CLI completa
- ✅ Tests unitarios
- ✅ Documentación completa

## 👤 Autor

**Jesus Quijada**

## 📄 Licencia

GNU GPL v3 - Ver [LICENSE](LICENSE) para más detalles

## 🙏 Agradecimientos

- Comunidad de PyQt5
- Desarrolladores de leviathan-ui
- Usuarios beta testers

## 🔗 Enlaces

- [Repositorio](https://github.com/usuario/packagemaker)
- [Documentación](https://packagemaker.docs)
- [Issues](https://github.com/usuario/packagemaker/issues)
- [Releases](https://github.com/usuario/packagemaker/releases)

## ⭐ Características Destacadas

### 🎯 Integración Perfecta
Accede a todas las funcionalidades de IPM sin abrir la aplicación principal.

### 🔧 MoonFix Inteligente
Sistema de reparación que detecta y corrige problemas automáticamente.

### 📦 Gestión Simplificada
Instala, compila y gestiona paquetes con un solo clic.

### ⚙️ Extensible
Crea tus propias extensiones con archivos .mexf.

### 💻 CLI Poderosa
Automatiza tareas con comandos de terminal.

### 🎨 Diseño Moderno
Interfaz consistente con el diseño de IPM usando LeviathanUI.

## 🚀 Próximos Pasos

1. ✅ Instalar integración shell
2. ✅ Probar menús contextuales
3. ✅ Crear tu primer proyecto
4. ✅ Compilar un proyecto
5. ✅ Usar MoonFix para reparar
6. ✅ Crear un archivo .mexf personalizado

## 💡 Tips y Trucos

### Tip 1: Atajos de Teclado
Usa `Shift + Clic derecho` para ver más opciones en el menú contextual.

### Tip 2: Compilación Rápida
Arrastra una carpeta sobre `packagemaker.exe` para compilar directamente.

### Tip 3: MoonFix Preventivo
Ejecuta MoonFix regularmente para mantener tus proyectos en buen estado.

### Tip 4: Archivos .mexf
Comparte tus archivos .mexf con otros desarrolladores para estandarizar configuraciones.

### Tip 5: CLI en Scripts
Usa los comandos CLI en scripts batch para automatizar flujos de trabajo.

## 📊 Estadísticas

- 📁 10 archivos nuevos creados
- 🔧 1 archivo modificado
- 📝 11 comandos CLI
- 🧪 25 tests unitarios
- 📖 6 documentos
- ⏱️ Instalación en < 1 minuto
- 💾 Tamaño: ~50 MB

## 🎉 ¡Gracias por usar Influent Package Maker!

Si te gusta este proyecto, considera:
- ⭐ Dar una estrella en GitHub
- 🐛 Reportar bugs
- 💡 Sugerir mejoras
- 📢 Compartir con otros desarrolladores

---

**Hecho con ❤️ por Jesus Quijada**
