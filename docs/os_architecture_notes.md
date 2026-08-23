# Influent OS: arquitectura de aplicaciones Linux y Android

## Alcance del prototipo

Influent OS es una distribución experimental **x86_64 basada en Ubuntu Noble**, con sesión GNOME sobre Wayland, aplicaciones Linux nativas y una capa Android separada del host. La primera entrega no intenta reemplazar el kernel ni reimplementar Android: integra componentes existentes de Ubuntu y AOSP mediante interfaces controladas.

## Decisión Android: sin Waydroid

**Waydroid queda excluido por decisión explícita del proyecto.** La estrategia inicial será ejecutar una imagen Android x86_64 basada en **AOSP/Cuttlefish** dentro de una máquina virtual acelerada por KVM. Cuttlefish está diseñado para ejecutar Android localmente en hosts Linux x86/x86_64 y proporciona un dispositivo virtual con el framework Android y ART, por lo que permite usar APKs sin convertir Waydroid en una dependencia del sistema.

Esta decisión implica una separación clara: Ubuntu ejecuta sus aplicaciones ELF nativas y el escritorio; la instancia Android ejecuta ART, el framework Android y las APKs. El intercambio de información se realizará a través de un servicio C++ con IPC local, ADB controlado y sincronización explícita. No se presentará como una traducción completa de APIs Android a Linux, porque esa alternativa requeriría reimplementar una gran parte de Android.

## Arquitectura por capas

| Capa | Tecnología | Responsabilidad |
|---|---|---|
| Arranque y sistema base | Kernel Linux, systemd, Ubuntu Noble | Arranque, dispositivos, red, actualizaciones y recuperación |
| Escritorio | GNOME, Mutter, Wayland, XWayland | Ventanas, entrada, composición y compatibilidad X11 |
| Aplicaciones Linux | ELF nativo, deb y futuras capas Flatpak/AppImage | Ejecutar aplicaciones Linux normales |
| Runtime Android | AOSP x86_64/Cuttlefish sobre KVM | Ejecutar Android, ART, servicios Android y APKs |
| Puente del host | C++17, socket Unix, systemd | Comprobar KVM, iniciar/detener el runtime, validar comandos y sincronizar estado |
| Lanzador Android | Java dentro de Android | Descubrir paquetes, publicar actividades lanzables e iniciar APKs con intents |
| Interfaz del host | Cliente de escritorio y entrada `.desktop` | Mostrar el catálogo Android junto a las apps Linux |
| Construcción | live-build con compatibilidad local GRUB2 | Generar una ISO reproducible para x86_64 |
| Gestión de paquetes | PackageMaker como herramienta complementaria | Crear o distribuir paquetes de aplicaciones, sin mezclarlo con el kernel |

## División entre Java y C++

El componente **Java** vivirá en el entorno Android. Usará `PackageManager` e intents explícitos para descubrir aplicaciones instaladas, registrar metadatos y lanzar actividades. El lanzador no debe ejecutar APKs directamente sobre Ubuntu: debe enviar una solicitud al servicio Android que controle el ciclo de vida dentro de Cuttlefish.

El componente **C++** será el soldador y orquestador del host. Su API aceptará un conjunto pequeño de operaciones como `status`, `start`, `stop`, `install` y `launch`; validará nombres de paquetes y actividades; y ejecutará solamente binarios Android permitidos mediante argumentos construidos internamente. Las futuras funciones de portapapeles, archivos, audio y ventanas se añadirán como módulos separados.

## Flujo de una aplicación Android

1. El usuario selecciona “Aplicaciones Android” desde el escritorio Ubuntu-like.
2. El cliente local contacta con el socket Unix del puente C++.
3. El puente verifica la configuración, el acceso a KVM y el estado de Cuttlefish.
4. Si el runtime no está activo, el puente lo inicia con una configuración conocida.
5. La aplicación Java consulta el `PackageManager` Android y devuelve el catálogo de actividades lanzables.
6. Una selección del usuario se transforma en un intent controlado dentro de Android.
7. El estado del runtime y del proceso se devuelve al escritorio mediante IPC.

## Limitaciones conocidas

La primera versión no garantiza Google Play, DRM, SafetyNet/Play Integrity, sensores físicos, cámaras, aceleración 3D perfecta ni aplicaciones que requieran binarios ARM-only. Cuttlefish requiere soporte KVM y no ofrece por sí solo integración transparente de cada ventana Android con el compositor Linux. La compatibilidad de APKs se validará progresivamente por familias de aplicaciones.

## Fuentes técnicas

[1] [Android Open Source Project: Cuttlefish](https://source.android.com/docs/devices/cuttlefish)

[2] [Android Open Source Project: introducción a Cuttlefish](https://source.android.com/docs/devices/cuttlefish/get-started)

[3] [Android Runtime (ART)](https://source.android.com/docs/core/runtime)

[4] [ART como módulo del sistema](https://source.android.com/docs/core/ota/modular-system/art)

[5] [Wayland](https://wayland.freedesktop.org/)

[6] [Repositorio PackageMaker seleccionado](https://github.com/JesusQuijada34/packagemaker)
