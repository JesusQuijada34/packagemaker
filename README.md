# Influent Package Maker

Influent Package Maker es una aplicación PyQt6 para crear, compilar, inspeccionar e instalar paquetes `.iflapp`. La interfaz usa una barra de título personalizada, tokens centralizados de diseño y Roboto como primera opción tipográfica.

## Estado actual

La aplicación incluye cinco áreas principales: Crear, Compilar, Configuración, MoonFix y Acerca de. La compilación ofrece backends Nuitka, PyInstaller, zipapp, cx_Freeze y PyOxidizer cuando están disponibles. El contenedor `.iflapp` v2 incorpora manifiesto, verificación y extracción segura.

La integración `.mexf`/`.asksome` está en migración: `example.mexf` se conserva como formato JSON legacy mientras se formaliza el nuevo contrato YAML versionado. No se ejecutan comandos heredados como shell sin validación.

## Desarrollo

```bash
python -m pip install -r requirements-dev.txt
QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q
python -m py_compile $(git ls-files '*.py')
python -m pyflakes $(git ls-files '*.py')
```

Para inspeccionar la interfaz sin hardware gráfico se puede regenerar el conjunto de capturas con:

```bash
QT_QPA_PLATFORM=offscreen python scripts/capture_screenshots.py
```

## Convenciones

- El trabajo se realiza directamente sobre `main`.
- `lib/design_tokens.py` es la fuente única de paleta, tipografía, radios y espaciados.
- Las ventanas y diálogos usan titlebar personalizada y botones SVG del proyecto.
- Las acciones de shell y compilación deben funcionar también en modo headless.
- Los cambios de interfaz deben incluir regresiones automatizadas y conservar fallback cuando PyQt6 o `leviathan_ui` no estén disponibles.
