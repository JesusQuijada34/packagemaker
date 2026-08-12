# Paquetes Debian de Influent Package Maker

Esta rama se llama `debían` y contiene el constructor reproducible de paquetes Debian. El script `debian/build_debs.py` genera variantes para `amd64`, `arm64`, `armhf` e `i386`, con nombres como `influent.packagemaker.v3.2.7-26.05-20.13-Danenone_amd64.deb`. `AlphaCube` queda reservado para paquetes que contengan únicamente código fuente o que se declaren explícitamente como multiplataforma; no se usa para archivos `.deb`.

El paquete instala el código Python/Qt en `/opt/influent-packagemaker`, añade el lanzador `/usr/bin/packagemaker` y registra una entrada `.desktop`. Los metadatos declaran las dependencias Debian de Python, PyQt6, Requests, Packaging y Pillow. Los directorios `.git`, `.github`, `.vscode`, las cachés y los artefactos temporales quedan excluidos del paquete.

La variante de arquitectura de Debian expresa la arquitectura objetivo para que el gestor de paquetes resuelva las dependencias correctas. Como el contenido de esta aplicación es código fuente Python, el payload es común; cualquier componente nativo generado posteriormente por Nuitka debe construirse en un runner nativo de la arquitectura correspondiente. En este entorno Linux x86_64 solo puede validarse de forma nativa `amd64`; las variantes `arm64`, `armhf` e `i386` se verifican estructuralmente y deben probarse en hardware o runners de esas arquitecturas antes de una distribución de producción.

Para construir todas las variantes disponibles:

```bash
python3 debian/build_debs.py --output debian-build
```

Para construir una sola variante:

```bash
python3 debian/build_debs.py --arch amd64 --output debian-build
```

La validación recomendada es comprobar el contenido con `dpkg-deb -I`, listar los archivos con `dpkg-deb -c` y probar el paquete `amd64` en una instalación Debian/Ubuntu limpia con sus dependencias disponibles.
