# Diseño de acceso y vinculación de dispositivo

## Flujo web

1. Las rutas `/download` y `/linkdevice` comprueban la sesión web de GitHub.
2. Si no existe una sesión válida, redirigen a `/login?next=...`.
3. `/login` crea el estado OAuth y PKCE, y GitHub autentica al usuario directamente en el navegador.
4. El callback de GitHub vuelve a `/auth/github/callback`. Render consulta el perfil público, guarda una sesión temporal de 15 minutos y coloca solamente un identificador de sesión firmado en la cookie persistente del navegador.
5. El usuario vuelve al destino original (`/download` o `/linkdevice`).

## Vinculación de PackageMaker

Cuando el usuario visita `/linkdevice` con una sesión web válida, Render crea un código de ocho caracteres y un ticket opaco con caducidad de 15 minutos. La página muestra el código y espera a que PackageMaker haga ping a `POST /api/linkdevice/poll` cada dos segundos.

Cuando el código es válido, Render entrega el ticket opaco y el perfil mínimo de GitHub. PackageMaker guarda ese ticket y el perfil en `data/github.session` como archivo binario local privado. El token de GitHub nunca se envía a la aplicación de escritorio. Después de un consumo exitoso, la página cambia a **Vinculación exitosa** y el código no puede volver a utilizarse.

## Sesión web en caché

La tabla `github_sessions` mantiene temporalmente el token del servidor y el perfil mínimo durante 15 minutos. La cookie del navegador es HttpOnly, SameSite=Lax y persistente; no contiene el token de GitHub. Cuando la caché expira, `/login` vuelve a solicitar la autorización.

## Configuración de Render y GitHub

- `FLASK_ENV=production`
- `FLASK_SECRET_KEY`: secreto largo y aleatorio.
- `GITHUB_CLIENT_ID`: Client ID de la OAuth App.
- `GITHUB_CLIENT_SECRET`: secreto exclusivo de Render.
- `RENDER_AUTH_BASE_URL=https://packagemaker.onrender.com`

El callback registrado en GitHub debe ser exactamente:

```text
https://packagemaker.onrender.com/auth/github/callback
```

El servicio debe utilizar almacenamiento persistente o una base de datos compartida para que la caché no se pierda durante un reinicio o entre varias instancias.
