# Diseño de vinculación de dispositivo

## Flujo

1. El usuario abre `https://packagemaker.onrender.com/linkdevice` y pulsa **Vincular con GitHub**.
2. Render crea una vinculación pendiente con un código corto, por ejemplo `AB7K-92QF`, y una caducidad de 15 minutos.
3. GitHub autentica al usuario en el navegador. El secreto de la OAuth App vive solo en Render.
4. Render guarda en caché durante 15 minutos la sesión mínima de GitHub y el perfil público asociado al código.
5. PackageMaker muestra al arrancar una pantalla de vinculación. El usuario escribe el código que aparece en `/linkdevice`.
6. PackageMaker hace ping a `POST /api/linkdevice/poll` cada dos segundos. Mientras GitHub no esté listo recibe `202 pending`; cuando la sesión esté disponible recibe `200 complete`.
7. Render devuelve un ticket opaco de sesión y el perfil mínimo. El ticket no es la contraseña ni el access token de GitHub.
8. PackageMaker guarda el ticket y el perfil en un archivo binario local con permisos restrictivos. El archivo se elimina o se ignora cuando la sesión expira.
9. El servidor marca el código como consumido y `/linkdevice` muestra que la vinculación fue exitosa.

## Seguridad

El código se genera con aleatoriedad criptográfica, se guarda en Render únicamente como hash y se invalida después de un uso o de 15 minutos. Todo el intercambio ocurre por HTTPS. El navegador recibe la contraseña directamente en GitHub; PackageMaker nunca ve credenciales. Render conserva el access token solo en memoria/almacén temporal del servidor durante la ventana de vinculación y no lo devuelve a la aplicación.

La sesión local es un ticket opaco con una fecha de expiración, no una copia de la contraseña ni del access token de GitHub. El archivo binario no debe utilizarse como mecanismo de autorización autónomo: para operaciones que requieran sesión, el servidor debe validar el ticket y su expiración.

## Variables de Render

- `FLASK_SECRET_KEY`: secreto largo y aleatorio para las cookies de Flask y la firma de tickets.
- `GITHUB_CLIENT_ID`: identificador público de la OAuth App.
- `GITHUB_CLIENT_SECRET`: secreto exclusivo del servicio Render.
- `RENDER_AUTH_BASE_URL`: `https://packagemaker.onrender.com`.

El alcance OAuth se mantiene mínimo. Para rellenar el autor basta con el usuario autenticado; no se solicitan repositorios ni permisos de escritura.
