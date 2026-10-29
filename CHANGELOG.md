# Changelog

## Sin publicar

### Formato `.iflapp` v2
- Nuevo contenedor binario propio (`lib/iflapp_format.py`) que reemplaza al ZIP
  histórico: cabecera JSON indexada con icono, `details.xml` y manifiesto,
  payload TAR comprimido (LZMA) y cifrado opcional (HMAC-SHA256-CTR o
  AES-256-GCM cuando `cryptography` está disponible).
- Cabecera firmada con HMAC-SHA256 y cola redundante para tolerancia a daño
  parcial del encabezado.
- Handler de lectura por cabecera (`lib/iflapp_reader.py`) que muestra icono y
  detalles sin descifrar ni descomprimir el payload.
- Comandos CLI `--inspect`, `--inspect-json` y `--inspect-extract`.

### Compiladores
- Capa de backends intercambiables (`lib/compilers.py`): **Nuitka** (por
  defecto), PyInstaller, cx_Freeze y PyOxidizer, con detección de
  disponibilidad e instalación automática vía pip.
- Comando CLI `--list-compilers` y selector de compilador en la GUI.

### Sandbox
- Sandbox de virtualización a nivel de hardware/CPU (`lib/hardware_sandbox.py`)
  con selección jerárquica: `qemu-kvm` → `systemd-nspawn` → `docker`/`podman` →
  `bwrap`/`firejail`/`unshare` → `local`, con límites de CPU y memoria.
- Verificación del `.iflapp` delegada al sandbox antes de publicarlo.

### Droppers y blindaje
- Generador de droppers autoextraíbles (`lib/dropper.py`) con stub autónomo,
  extracción segura y compatibilidad con ZIP histórico.
- Módulo de blindaje (`lib/hardening.py`): `strip`, `upx`, `checksum`,
  `anti-debug`, `obfuscate` y `resource`.
- Comandos CLI `--dropper`, `--harden` y `--list-hardening`.

### Fuentes de la interfaz
- Gestor de fuentes (`lib/font_manager.py`): descarga Roboto, Inter, Noto Sans,
  Open Sans y JetBrains Mono desde Google Fonts, verifica cada archivo por
  SHA-256 y lo registra en Qt con `QFontDatabase.addApplicationFont`.
- Varios espejos por fuente (raw.githubusercontent y CDN jsDelivr) con
  tolerancia a fallos y arranque sin red usando la caché en `data/fonts/`.
- Resolución de familia versátil: las fuentes descargadas tienen prioridad
  sobre las del sistema, de modo que la interfaz se ve igual en cualquier
  máquina; si no hay ninguna, se usa el fallback del sistema.
- La fuente monoespaciada preferida (JetBrains Mono) se aplica al editor de
  código, al visor de diferencias y a la terminal de salida.
- Comandos CLI `--list-fonts`, `--download-fonts [KEYS]` y `--force-fonts`, y
  sección de fuentes con botón de descarga en la pestaña de configuración.
- Corrección del arranque: la fuente de UI ya no se resuelve antes de crear
  `QApplication`, lo que eliminaba el aviso
  `QFontDatabase: Must construct a QGuiApplication before accessing QFontDatabase`.

### Calidad
- Reparación de lint en todo el repositorio: imports sin usar, f-strings sin
  marcadores, `except` desnudos y variables sin uso.

## v3.2.7-26.05-20.13

- Identidad normalizada: publisher `influent` y author `JesusQuijada34`.
- Versión pública normalizada sin sufijo de plataforma.
- MoonFix aplicado con estructura PackageMaker 3.2.7.
- Documentación y archivos estructurales verificados.
