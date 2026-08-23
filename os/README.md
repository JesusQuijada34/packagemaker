# Influent OS — prototipo Ubuntu x86_64

Influent OS es un prototipo de distribución basada en Ubuntu para ejecutar aplicaciones Linux nativas y ofrecer una capa Android separada, sin Waydroid. La primera versión prioriza una base reproducible, un escritorio Wayland sencillo y una integración Android basada en una imagen AOSP x86_64 ejecutada de forma virtualizada.

## Estado actual

Este directorio contiene la primera base de ingeniería: configuración de una imagen Ubuntu, tema visual, servicio de integración en C++, y un lanzador Java para Android. Todavía no es una ISO terminada ni una implementación completa de compatibilidad Android. La capa Android se conecta mediante una instancia virtual Android compatible con ADB; la integración avanzada de ventanas, audio, portapapeles y archivos se incorporará después de validar el ciclo de arranque.

## Arquitectura

| Área | Implementación inicial |
|---|---|
| Base | Ubuntu x86_64 con paquetes de escritorio seleccionados |
| Escritorio | Wayland con GNOME Shell y personalización visual mínima |
| Apps Linux | Paquetes APT, Flatpak y ejecutables ELF del sistema |
| Android | Imagen AOSP/Cuttlefish x86_64 separada; no se usa Waydroid |
| Puente | `influent-bridge`, daemon C++ sobre socket Unix |
| Lanzador APK | `InfluentLauncher`, aplicación Java instalada dentro del entorno Android |
| Empaquetado | Script de imagen reproducible; PackageMaker queda como componente de distribución opcional |

## Construcción

La construcción necesita una máquina Ubuntu/Debian x86_64 con privilegios para instalar `live-build`, `debootstrap`, `squashfs-tools`, `xorriso`, `qemu-kvm` y las dependencias de C++. El script no descarga ni ejecuta APKs de terceros. La imagen Android debe obtenerse de una fuente AOSP/Cuttlefish compatible y colocarse en el directorio indicado por la documentación del proyecto.

```bash
cd os
sudo ./build/build-iso.sh
```

Para una compilación local del puente C++ sin crear la ISO:

```bash
cmake -S host-bridge -B host-bridge/build
cmake --build host-bridge/build
ctest --test-dir host-bridge/build --output-on-failure
```

## Principios de seguridad

El puente solo escucha en un socket Unix con permisos restringidos. Las órdenes de instalación y lanzamiento reciben identificadores de paquetes, no comandos arbitrarios. La instancia Android se mantiene aislada del host y cualquier ampliación futura de carpetas compartidas deberá definir permisos explícitos.

## Próximos hitos

El siguiente hito consiste en compilar el daemon C++, empaquetar el servicio systemd, preparar una sesión de escritorio Ubuntu-like y validar el arranque de una imagen Android x86_64 en KVM. Después se conectará la aplicación Java con `PackageManager` y se añadirá el catálogo de aplicaciones al escritorio.

## Fuentes de diseño

- [Wayland](https://wayland.freedesktop.org/)
- [Android Open Source Project](https://source.android.com/docs)
- [Cuttlefish](https://source.android.com/docs/devices/cuttlefish)
- [Cuttlefish: requisitos y arranque](https://source.android.com/docs/devices/cuttlefish/get-started)
- [Android Runtime](https://source.android.com/docs/core/runtime)
