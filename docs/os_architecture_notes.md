# Proyecto de sistema operativo Linux con aplicaciones Android y Linux

## Hallazgos iniciales

La opción técnicamente más viable para un primer prototipo no es reimplementar Android desde cero, sino usar una distribución Linux existente y añadir una capa Android basada en Waydroid. Waydroid arranca un sistema Android completo dentro de un contenedor Linux usando namespaces y LXC, con integración de hardware mediante binder y soporte de escritorio orientado a Wayland. La documentación pública de Waydroid describe integración de aplicaciones Android en el menú de aplicaciones Linux y modos de ventana múltiple y pantalla completa.

AOSP es una pila de software Android de código abierto y documenta la compilación, personalización, seguridad y compatibilidad. Para una primera versión conviene consumir una imagen Android compatible y reservar la compilación de una imagen personalizada basada en AOSP/LineageOS para una segunda fase.

Wayland será la base gráfica preferida porque es la arquitectura de escritorio recomendada por Waydroid y permite convivir con aplicaciones Linux nativas. XWayland puede cubrir aplicaciones Linux X11 que aún no sean Wayland-native.

## Arquitectura propuesta

| Capa | Tecnología propuesta | Responsabilidad |
|---|---|---|
| Arranque y sistema base | Linux kernel + systemd + una base Debian/Ubuntu | Arranque, servicios, dispositivos, actualizaciones y recuperación |
| Escritorio | Wayland + compositor wlroots o KDE/GNOME | Ventanas, entrada, portapapeles y composición |
| Apps Linux | ELF nativo, Flatpak/AppImage/deb | Ejecución normal de aplicaciones Linux |
| Apps Android | Waydroid + LXC + imagen Android/LineageOS | ART, framework Android, APKs y servicios Android |
| Integración | Servicio propio en C++ | Detectar, iniciar, detener, registrar y exponer apps Android |
| Gestión de paquetes | PackageMaker existente, adaptado gradualmente | Crear y distribuir paquetes de aplicaciones, sin mezclarlo con el kernel |
| API Java | Java dentro de Android; JNI/IPC con C++ | Código Java Android y puente con servicios nativos |
| Instalador | ISO reproducible con Calamares o live-build | Instalación del sistema y configuración inicial |

## Decisiones importantes

1. Android se ejecutará inicialmente en un contenedor, no como emulación completa de CPU. Esto ofrece mejor rendimiento en equipos con la misma arquitectura que la aplicación Android y reduce el alcance del proyecto.
2. El prototipo debe enfocarse primero en x86_64, GPU Intel/AMD y sesión Wayland. ARM64, NVIDIA, máquinas virtuales y compatibilidad avanzada se tratarán después.
3. El servicio C++ no debe reimplementar ART ni el framework Android. Su función será orquestación, integración de ventanas, descubrimiento de APKs, ciclo de vida y comunicación segura.
4. Java se usará para componentes Android o una aplicación de configuración Android; los servicios del host Linux permanecerán en C++ y se comunicarán mediante D-Bus, sockets Unix o una API local definida.
5. El repositorio PackageMaker es un IDE/compilador de paquetes Python/PyQt6 con plataforma AlphaCube. Puede reutilizarse como gestor de empaquetado de aplicaciones, pero no constituye por sí mismo la base del sistema operativo.

## Riesgos y límites

El soporte de Google Play y aplicaciones que dependen de certificación, DRM, SafetyNet/Play Integrity, ARM-only binaries o drivers específicos no puede darse por garantizado. También habrá diferencias de compatibilidad entre GPUs, kernels y aplicaciones Android.

## Fuentes

[1] Waydroid, sitio oficial: https://waydro.id/
[2] Waydroid, documentación: https://docs.waydro.id/
[3] Android Open Source Project, documentación: https://source.android.com/docs
[4] Wayland, sitio oficial: https://wayland.freedesktop.org/
[5] PackageMaker, repositorio revisado: https://github.com/JesusQuijada34/packagemaker

## Cambio solicitado: sin Waydroid

Waydroid queda excluido. La alternativa viable para el prototipo será ejecutar una imagen AOSP x86_64 mediante una máquina virtual acelerada por KVM, tomando Cuttlefish como referencia de dispositivo virtual. Cuttlefish está diseñado para ejecutar Android localmente en hosts Linux x86 y x86_64 y mantiene alta fidelidad con el framework Android; requiere virtualización disponible en el host. La primera versión usará esta vía para obtener un entorno Android real con ART y compatibilidad APK, sin depender de Waydroid ni de su contenedor.

El servicio C++ del host actuará como orquestador: comprobará KVM, preparará la instancia, iniciará y detendrá el dispositivo Android, expondrá una API local segura, sincronizará archivos y recibirá eventos. No reemplazará ART ni fingirá traducir cada API de Android. Una traducción completa de Android a Linux sería un proyecto de años y no es realista para un primer prototipo.

El componente Java será una aplicación/servicio Android dentro de la imagen AOSP. Su responsabilidad será registrar APKs instalados, publicar metadatos de lanzamiento, iniciar actividades mediante intents y devolver estados al puente C++. El host podrá incluir un pequeño cliente C++/GTK o una interfaz de escritorio para mostrar esos lanzadores junto con las aplicaciones Linux.

### Arquitectura revisada

| Componente | Primera implementación | Evolución posterior |
|---|---|---|
| Android | AOSP x86_64 + Cuttlefish/KVM, separado del host Ubuntu | Imagen AOSP personalizada y backend de virtualización optimizado |
| Lanzador APK | Servicio Java en Android que usa PackageManager/Intents | Catálogo de apps, permisos y actualización integrada |
| Soldador/traductor | Daemon C++ con IPC local, control de VM y sincronización | Integración avanzada de ventanas, portapapeles, audio y archivos |
| Escritorio | Wayland Ubuntu-like en el host | Shell propio y compositor personalizado si se justifica |

### Limitaciones explícitas

La primera versión no garantizará Google Play, DRM, SafetyNet/Play Integrity, sensores físicos, cámaras, aceleración 3D perfecta ni aplicaciones que requieran binarios ARM-only. Cuttlefish documenta su dependencia de KVM y su uso como dispositivo virtual de alta fidelidad, no como una capa transparente nativa de ventanas Linux.

### Fuentes nuevas

[6] AOSP Cuttlefish: https://source.android.com/docs/devices/cuttlefish
[7] Inicio de Cuttlefish y requisito KVM: https://source.android.com/docs/devices/cuttlefish/get-started
[8] Android Runtime (ART): https://source.android.com/docs/core/runtime
[9] ART como módulo del sistema: https://source.android.com/docs/core/ota/modular-system/art
