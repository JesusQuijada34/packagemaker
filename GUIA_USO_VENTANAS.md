# 📖 Guía de Uso - Ventanas de Menú Contextual

## Introducción

Influent Package Maker (IPM) ahora incluye integración completa con el shell de Windows, permitiendo acceder a todas sus funcionalidades directamente desde el menú contextual del explorador de archivos.

---

## 🖱️ Opciones del Menú Contextual

### 1. 🆕 Crear Proyecto Aquí

**Ubicación**: Click derecho en una carpeta vacía o en el fondo del explorador

**Función**: Crea un nuevo proyecto Fluthin en la ubicación seleccionada

**Campos del formulario**:
- **Nombre del Proyecto**: Nombre identificador del proyecto
- **Versión**: Versión inicial (por defecto 1.0)
- **Autor**: Tu nombre o el del desarrollador
- **Publisher**: Nombre de la empresa o publicador
- **Descripción**: Descripción breve del proyecto

**Resultado**:
- Crea estructura de carpetas: `app/`, `assets/`, `config/`, `docs/`, `lib/`, `source/`
- Genera `details.xml` con la información del proyecto
- Crea archivo principal `.py` con plantilla básica
- Crea `requirements.txt` vacío en `lib/`

---

### 2. 📦 Instalar como Fluthin Package

**Ubicación**: Click derecho en una carpeta de proyecto

**Función**: Instala una carpeta como paquete Fluthin en el sistema

**Proceso**:
1. Verifica la estructura del proyecto
2. Crea `details.xml` si no existe
3. Copia todos los archivos a `Documentos/Fluthin Apps/`
4. Registra el paquete en el sistema

**Requisitos**:
- La carpeta debe contener un proyecto válido
- Si falta `details.xml`, se crea automáticamente

---

### 3. 🔨 Compilar Proyecto

**Ubicación**: Click derecho en una carpeta de proyecto

**Función**: Compila el proyecto para diferentes plataformas

**Opciones**:
- ✅ **Compilar para Windows**: Genera ejecutable .exe
- ✅ **Compilar para Knosthalij**: Genera paquete para Knosthalij
- ✅ **Optimizar código**: Aplica optimizaciones al código

**Resultado**:
- Ejecutables compilados en la carpeta del proyecto
- Log detallado del proceso de compilación

---

### 4. 🌙 Reparar Proyecto (MoonFix)

**Ubicación**: Click derecho en una carpeta de proyecto

**Función**: Analiza y repara automáticamente problemas del proyecto

**Verificaciones**:
- ✅ **Archivos faltantes**: Detecta y crea archivos requeridos (`details.xml`, `autorun`, etc.)
- ✅ **Configuraciones antiguas**: Actualiza configuraciones obsoletas
- ✅ **Estructura de carpetas**: Verifica y crea carpetas faltantes
- ✅ **Dependencias**: Verifica archivos de dependencias

**Resultado**:
- Reporte de problemas encontrados
- Reporte de problemas reparados
- Proyecto listo para usar

---

### 5. 📥 Instalar Paquete

**Ubicación**: Click derecho en un archivo `.iflapp`

**Función**: Instala un paquete Fluthin desde un archivo

**Proceso**:
1. Verifica el archivo .iflapp
2. Extrae el contenido del paquete
3. Copia archivos a Fluthin Apps
4. Registra el paquete en el sistema

**Resultado**:
- Paquete instalado y listo para usar
- Accesible desde el gestor de paquetes

---

### 6. 📝 Crear Archivo MEXF

**Ubicación**: Click derecho en una carpeta

**Función**: Crea un archivo de extensiones de shell (.mexf)

**Campos**:
- **Nombre**: Nombre del archivo (sin extensión)
- **Descripción**: Descripción de las extensiones

**Contenido generado**:
```json
{
    "name": "nombre",
    "version": "1.0",
    "description": "Descripción",
    "mimetypes": [...],
    "context_menus": [...],
    "shell_extensions": {...}
}
```

**Uso**: Permite crear integraciones personalizadas con el shell de Windows

---

### 7. 🔧 Instalar Extensiones MEXF

**Ubicación**: Click derecho en un archivo `.mexf`

**Función**: Instala extensiones de shell desde un archivo MEXF

**Proceso**:
1. Lee el archivo .mexf
2. Registra mimetypes personalizados
3. Instala menús contextuales
4. Configura extensiones de shell

**Resultado**:
- Nuevos tipos de archivo reconocidos por Windows
- Menús contextuales personalizados
- Integración completa con el explorador

---

### 8. 📄 Abrir con IPM

**Ubicación**: Click derecho en un archivo `.iflapp`

**Función**: Abre el paquete en el gestor de IPM

**Resultado**:
- IPM se abre en la pestaña de gestor
- Paquete cargado y listo para gestionar

---

### 9. ✏️ Editar MEXF

**Ubicación**: Click derecho en un archivo `.mexf`

**Función**: Abre el editor de archivos MEXF

**Resultado**:
- Editor de MEXF abierto
- Permite modificar configuraciones de extensiones

---

## 🎨 Características de las Ventanas

### Diseño Consistente
Todas las ventanas siguen el diseño de LeviathanUI:
- Fondo semi-transparente con efecto blur
- Bordes redondeados
- Barra de título personalizada
- Animaciones suaves

### Feedback Visual
- **Barras de progreso**: Muestran el avance de operaciones largas
- **Logs en tiempo real**: Estilo terminal con colores
- **Mensajes modales**: Éxito, error, advertencia, información

### Controles Intuitivos
- Botones grandes y fáciles de clickear
- Campos de texto con validación
- Checkboxes para opciones
- Tooltips informativos

---

## 🚀 Uso desde Línea de Comandos

También puedes invocar estas funciones desde la línea de comandos:

```bash
# Crear proyecto
packagemaker.exe --create-project "C:\ruta\proyecto"

# Instalar carpeta
packagemaker.exe --install-folder "C:\ruta\carpeta"

# Compilar proyecto
packagemaker.exe --compile-project "C:\ruta\proyecto"

# Reparar proyecto
packagemaker.exe --repair-project "C:\ruta\proyecto"

# Instalar paquete
packagemaker.exe --install-package "C:\ruta\archivo.iflapp"

# Crear MEXF
packagemaker.exe --create-mexf "C:\ruta\carpeta"

# Instalar MEXF
packagemaker.exe --install-mexf "C:\ruta\archivo.mexf"

# Editar MEXF
packagemaker.exe --edit-mexf "C:\ruta\archivo.mexf"
```

---

## 🔧 Instalación de la Integración

### Automática (Recomendado)
La integración se instala automáticamente al abrir IPM por primera vez.

### Manual
1. Abre IPM
2. Ve a la pestaña **Configuración**
3. Click en **Instalar Integración con Shell**
4. Espera a que se complete la instalación
5. ¡Listo! Los menús contextuales están disponibles

### Desinstalación
1. Abre IPM
2. Ve a la pestaña **Configuración**
3. Click en **Desinstalar Integración con Shell**
4. Los menús contextuales se eliminarán del sistema

---

## 📋 Requisitos

- Windows 7 o superior
- Python 3.6+ (si se ejecuta desde script)
- PyQt5
- leviathan-ui
- Permisos de administrador (para instalación de integración)

---

## 🐛 Solución de Problemas

### Los menús no aparecen
1. Verifica que la integración esté instalada
2. Reinicia el explorador de Windows (o reinicia el PC)
3. Ejecuta IPM como administrador y reinstala la integración

### Error de permisos
- Ejecuta IPM como administrador
- Verifica que tengas permisos de escritura en el registro

### Ventanas no se abren
- Verifica que todos los archivos estén en su lugar
- Revisa el log de errores en la consola
- Asegúrate de tener todas las dependencias instaladas

---

## 💡 Consejos

1. **Usa MoonFix regularmente**: Mantiene tus proyectos en buen estado
2. **Crea archivos MEXF**: Personaliza la integración con el shell
3. **Compila para múltiples plataformas**: Llega a más usuarios
4. **Documenta tus proyectos**: Usa el campo de descripción

---

## 📞 Soporte

Si encuentras algún problema o tienes sugerencias, por favor reporta en el repositorio del proyecto.

---

**¡Disfruta de Influent Package Maker con integración completa de shell!** 🎉
