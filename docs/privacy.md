# Privacidad y reporte de errores

Influent Package Maker funciona sin conexión. El reporte de errores es
**opcional y está desactivado por defecto**: no se envía nada hasta que el
usuario lo active y configure un endpoint.

## Qué se envía cuando está activado

Sólo si `telemetry_enabled` es verdadero **y** `telemetry_endpoint` no está
vacío (claves de `data/pm.data`):

- versión de la aplicación y de Python;
- sistema operativo (por ejemplo `Windows` o `Linux`);
- tipo y mensaje de la excepción;
- traza del error, saneada.

## Qué no se envía nunca

- variables de entorno ni credenciales;
- nombres de usuario;
- rutas absolutas: `sanitize()` sustituye la carpeta personal por `~` y
  cualquier ruta absoluta por `<path>`;
- valores con pinta de token, contraseña o clave de API, que se reemplazan por
  `<redacted>`.

## Cómo funciona

`lib/errorReporter.py` encadena el envío al `sys.excepthook` y lo ejecuta en un
hilo aparte con un tiempo límite de 5 s. Un servidor lento o caído nunca bloquea
la interfaz ni genera un error nuevo: cualquier fallo del envío se ignora.

## Cómo desactivarlo

Deje `telemetry_enabled` en `false` (valor por defecto) o vacíe
`telemetry_endpoint`. No es necesario reiniciar para que el cambio afecte al
siguiente error reportado.

## Reportes como issues de GitHub

Además del endpoint opcional anterior, la aplicación puede publicar el fallo
como un issue en el repositorio del proyecto. Esto usa la sesión de GitHub que
el usuario ya autenticó en la aplicación: no se piden credenciales nuevas y no
hay ningún servidor intermediario.

Qué se envía en ese caso:

- la descripción que escribe el usuario y los archivos que adjunte;
- el entorno del dispositivo: versión de PackageMaker, commit del repositorio
  (si se ejecuta desde el código fuente), versión de Python, sistema operativo y
  su versión, arquitectura, versión de Qt, distribución (congelada o fuente) y
  número de núcleos;
- la traza del error, saneada con las mismas reglas que el resto.

Qué no se envía nunca: rutas absolutas, la carpeta personal, el nombre de
usuario del sistema, el hostname, variables de entorno ni credenciales.

Los fallos automáticos se agrupan por huella (`fingerprint`): si el mismo fallo
ya tiene un issue abierto se añade un comentario en vez de abrir otro, para no
inundar el repositorio. Si no hay sesión de GitHub o no hay red, el reporte se
guarda en `data/report_queue.json` y se reintenta desde la página de Reportes.

Para desactivar el envío automático de fallos, desmarque la casilla de la
página de Reportes o ponga `auto_report_errors` en `false` en `data/pm.data`.
Con el envío automático apagado los fallos sólo se guardan en local.

## Tarjeta «Privacidad» de Configuración

Los dos interruptores anteriores también viven en **Configuración → Privacidad**,
junto al campo de la URL del servidor propio:

| Control | Clave en `data/pm.data` | Efecto |
|---|---|---|
| Enviar fallos automáticamente al repositorio | `auto_report_errors` | Publica el fallo como issue con la sesión de GitHub. Apagado, el fallo sólo se guarda en local. |
| Enviar fallos a un servidor propio | `telemetry_enabled` | Activa `lib/errorReporter.py`. Necesita además una URL. |
| Servidor propio (URL) | `telemetry_endpoint` | Destino del envío. Sin URL, `is_enabled()` devuelve `false`. |

Los dos envíos son independientes: se puede publicar en el repositorio sin
servidor propio, o al contrario. `telemetry_enabled` sigue desactivado por
defecto y `telemetry_endpoint` está vacío, así que la instalación recién hecha
no envía nada a ningún servidor externo.

## Asistente AIDE

AIDE no usa ningún servidor propio de PackageMaker. Habla con el proveedor que
el usuario elija:

- **GitHub Copilot**, con el SDK oficial y la sesión de GitHub ya autenticada;
- **cualquier endpoint compatible con OpenAI** (Azure OpenAI, Ollama, un
  servidor local), con la clave que el usuario aporte.

Qué se envía en cada consulta:

- el texto que escribe el usuario;
- el contexto del proyecto **sólo si marca la casilla**: hasta 12 ficheros de
  texto (`.py`, `.json`, `.xml`, `.yaml`, `.md`, `.txt`, `.qss`, `.js`), sin
  ficheros ocultos, recortados a 4 000 caracteres cada uno;
- la versión de la aplicación dentro del prompt de sistema.

Qué no se envía nunca: la clave de API se queda en la cabecera de la petición
(no forma parte del prompt), no se adjuntan binarios, rutas absolutas,
credenciales ni variables de entorno. El contexto pasa por
`lib.report_telemetry.sanitize()` antes de salir, así que la carpeta personal se
convierte en `~` y cualquier ruta absoluta en `<path>`.

La clave de API se guarda en `data/pm.data` (`aide_api_key`) en claro, igual que
el resto de preferencias; no se registra en logs ni se muestra en la interfaz
una vez escrita.
