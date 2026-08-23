# Influent OS — estado de la primera entrega

## Alcance

Influent OS es una primera imagen experimental para **x86_64**, basada en Ubuntu Noble y ensamblada con `live-build`. Incluye una sesión GNOME sobre Wayland, tema Yaru, fondo visual propio, aplicaciones Linux de escritorio, herramientas C++ y QEMU/ADB para preparar la futura capa Android propia.

La imagen **no utiliza Waydroid**. La estrategia Android queda separada del escritorio Linux: el objetivo siguiente es ejecutar una instancia AOSP/Cuttlefish mediante virtualización y exponer únicamente operaciones controladas a través del puente C++.

## Componentes implementados

| Componente | Estado |
|---|---|
| ISO Ubuntu x86_64 | Generada y validada |
| Escritorio GNOME/Wayland con apariencia Ubuntu-like | Incluido |
| Tema Yaru, fondo y ajustes visuales de Influent | Incluido |
| Servicio puente C++ | Implementado y probado |
| Controlador C++ de runtime Android | Interfaz y backend inicial implementados; requiere imagen Cuttlefish para ejecución real |
| Lanzador Java de APKs | Esqueleto Android Java incluido; pendiente de compilar con Android SDK/Gradle |
| Waydroid | Excluido por decisión de arquitectura |
| Compatibilidad completa con APKs | No disponible todavía; requiere integrar AOSP/ART/Cuttlefish y validar gráficos, audio, red y entrada |

## Artefacto generado

El archivo se encuentra en `os/dist/influent-os-noble-amd64.iso`. Tiene formato ISO 9660 arrancable, volumen `INFLUENT_OS` y un tamaño aproximado de 4,98 GB. Su suma SHA-256 está en `os/dist/influent-os-noble-amd64.iso.sha256`.

La imagen está orientada a **pruebas en máquinas virtuales y arranque UEFI**. La primera entrega no usa `isohybrid` porque la versión de `live-build` disponible intenta combinar su backend antiguo de syslinux con GRUB2; se dejó un parche local versionado para GRUB2 y archivos squashfs grandes.

## Compilación

Desde la raíz del repositorio:

```bash
sudo apt-get update
sudo apt-get install -y live-build debootstrap squashfs-tools xorriso syslinux-utils cmake ninja-build g++
sudo WORK_DIR="$PWD/os/.live-build" \
  OUTPUT_DIR="$PWD/os/dist" \
  ./os/build/build-iso.sh
```

El script usa una copia local de compatibilidad en `os/build/live-build/` y mantiene los artefactos grandes fuera de Git mediante `.gitignore`.

## Validaciones realizadas

El archivo ISO fue reconocido como `ISO 9660 CD-ROM filesystem data (bootable)` y la comprobación `sha256sum -c` terminó correctamente. El puente C++ compiló con CMake/Ninja y su prueba `bridge_smoke_test` pasó con `100% tests passed`.

## Próximos pasos

La siguiente fase debe añadir la imagen AOSP/Cuttlefish, comprobar aceleración KVM y conectar el controlador C++ con un runtime Android real. Después se debe compilar el módulo Java con un Android SDK fijado, implementar instalación segura de APKs, descubrir actividades lanzables y añadir pruebas de integración desde el escritorio Linux.
