# Runtime Python para PackageMaker Android

## Hallazgos

Chaquopy 17 se integra con el sistema de compilación Gradle de Android, busca por defecto el código Python en `app/src/main/python`, requiere llamar a `Python.start()` antes de ejecutar módulos Python y permite declarar dependencias mediante un bloque `pip`. La documentación indica que el plugin se incorpora en un único módulo Android y que las dependencias deben ser compatibles con Android/ABI.

PackageMaker contiene una interfaz de escritorio basada en PyQt/PySide y módulos de lógica que usan procesos externos, PyInstaller, rutas Windows/Linux, editores de escritorio y comandos de shell. Por ello, no se puede ejecutar la interfaz original tal cual dentro de Android. El port debe separar el núcleo de generación/validación de proyectos de la UI Qt y del compilador de escritorio.

## Decisión técnica provisional

Integrar Chaquopy en el módulo `android/app` para ejecutar un núcleo Python Android adaptado. Mantener la interfaz Android existente y conectar Kotlin con Python mediante la API Java de Chaquopy. Excluir del runtime local las partes que dependen de PyQt/PySide, PyInstaller, ejecutables `.exe`, shell de escritorio o toolchains no disponibles en Android. Esas partes seguirán mediante el flujo SSH remoto.

## Fuentes

1. https://chaquo.com/chaquopy/doc/current/android.html — Chaquopy 17.0, plugin Gradle, arranque de Python, source sets y dependencias pip.
2. https://docs.python.org/3/using/android.html — Python embebido en aplicaciones Android.
3. https://github.com/kivy/python-for-android — alternativa de empaquetado Python para Android.
