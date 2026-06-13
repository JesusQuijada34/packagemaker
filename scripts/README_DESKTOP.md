Este conjunto de scripts permite levantar un entorno gráfico XFCE dentro del contenedor/espacio de trabajo y accederlo por navegador usando noVNC.

Requisitos y notas:
- Este script instala paquetes con `apt` y por tanto requiere permisos de administrador.
- En entornos remotos (Codespaces/Docker) debes exponer el puerto `6080` para acceder al VNC vía navegador.

Pasos básicos:
1. Haz ejecutable el script:

   chmod +x scripts/start_desktop.sh

2. Ejecuta con sudo:

   sudo scripts/start_desktop.sh

3. Abre en tu navegador: http://localhost:6080/vnc.html

Consejos:
- Si usas Codespaces/Cloud, añade la publicación del puerto 6080 en la configuración de puertos o crea un túnel SSH.
- Alternativa ligera desde tu máquina local: usa `ssh -X` o `ssh -Y` hacia el host con un servidor X11 local (no incluido aquí).

Limitaciones:
- No configura autenticación VNC por defecto (se ejecuta con `-nopw`). Para producción añade opciones de contraseña en `x11vnc`.
- Dependiendo de la imagen base, algunos paquetes pueden tener nombres distintos o requerir repositorios adicionales.
