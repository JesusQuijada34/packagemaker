# Packagemaker UWP

Aplicación UWP nativa de Windows para crear paquetes .iflapp de Influent Package Maker.

## Requisitos

- Windows 10 versión 1809 (build 17763) o superior
- Visual Studio 2022 con la carga de trabajo de desarrollo para UWP
- Windows 10 SDK (versión 10.0.17763.0 o superior)

## Características

- Interfaz nativa de Windows con WinUI 3
- Creación de paquetes .iflapp con estructura completa
- Detección de conexión a Internet
- Validación de campos obligatorios
- Interfaz moderna con Fluent Design

## Estructura del Proyecto

```
PackagemakerUWP/
├── App.xaml                 # Recursos de la aplicación
├── App.xaml.cs              # Lógica de inicio de la aplicación
├── MainWindow.xaml          # Interfaz principal
├── MainWindow.xaml.cs       # Lógica de la ventana principal
├── Package.appxmanifest     # Manifiesto de la aplicación UWP
├── app.manifest             # Manifiesto de compatibilidad
└── Assets/                  # Recursos gráficos (iconos, splash, etc.)
```

## Compilación

1. Abre el proyecto en Visual Studio 2022
2. Selecciona la configuración deseada (Debug/Release)
3. Selecciona la plataforma (x86, x64 o ARM64)
4. Compila el proyecto (F6)
5. Ejecuta la aplicación (F5)

## Assets Requeridos

Necesitas crear los siguientes archivos de imagen en la carpeta `Assets/`:
- `SplashScreen.png` (620x300 píxeles)
- `StoreLogo.png` (50x50 píxeles)
- `Square150x150Logo.png` (150x150 píxeles)
- `Square44x44Logo.png` (44x44 píxeles)
- `Square44x44Logo.targetsize-24_altform-unplated.png` (24x24 píxeles)
- `Wide310x150Logo.png` (310x150 píxeles)

También necesitas las versiones scale-200 de estos assets:
- `SplashScreen.scale-200.png`
- `LockScreenLogo.scale-200.png`
- `Square150x150Logo.scale-200.png`
- `Square44x44Logo.scale-200.png`
- `Wide310x150Logo.scale-200.png`

Puedes crear estos assets usando herramientas de diseño como GIMP, Photoshop, o cualquier editor de imágenes.

## Empaquetado para Microsoft Store

El proyecto está configurado para generar un paquete MSIX que puede ser publicado en Microsoft Store.

Para crear el paquete:
1. Click derecho en el proyecto → Publicar → Crear paquetes de aplicación
2. Sigue el asistente de empaquetado
3. El paquete MSIX se generará en la carpeta `AppPackages`

## Funcionalidad

La aplicación permite:
- Ingresar metadatos del paquete (empresa, nombre lógico, nombre completo, versión)
- Crear la estructura completa de carpetas y archivos para un paquete .iflapp
- Generar archivos iniciales (script principal, README, requirements.txt, details.xml)
- Validar campos antes de crear el proyecto
- Confirmar sobrescritura si el proyecto ya existe

## Notas

- Los paquetes se crean en: `%USERPROFILE%\Documents\Influent Packages\`
- La aplicación requiere permisos de escritura en el sistema de archivos
- La conexión a Internet se verifica automáticamente al iniciar

