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
