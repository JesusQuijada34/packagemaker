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

### Calidad
- Reparación de lint en todo el repositorio: imports sin usar, f-strings sin
  marcadores, `except` desnudos y variables sin uso.

## v3.2.7-26.05-20.13

- Identidad normalizada: publisher `influent` y author `JesusQuijada34`.
- Versión pública normalizada sin sufijo de plataforma.
- MoonFix aplicado con estructura PackageMaker 3.2.7.
- Documentación y archivos estructurales verificados.
