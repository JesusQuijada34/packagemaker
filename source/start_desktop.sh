#!/usr/bin/env bash
set -euo pipefail

# Script mínimo para arrancar un entorno gráfico XFCE en un contenedor
# - Lanza Xvfb en :1
# - Exporta DISPLAY
# - Arranca XFCE
# - Arranca x11vnc conectado a :1
# - Arranca noVNC (websockify) en el puerto 6080 para acceso por navegador

if [[ "$EUID" -ne 0 ]]; then
  echo "Este script requiere permisos de administrador (sudo). Ejecute: sudo $0"
  exit 1
fi

echo "Instalando paquetes necesarios (xfce4, xvfb, x11vnc, novnc, websockify)..."
apt-get update
apt-get install -y xfce4 xfce4-goodies xvfb x11vnc novnc websockify python3-websockify && echo "Instalación completada"

DISPLAY_NUMBER=1
RESOLUTION=1280x720x24

echo "Iniciando Xvfb :$DISPLAY_NUMBER ($RESOLUTION) ..."
Xvfb :$DISPLAY_NUMBER -screen 0 $RESOLUTION &
XVFB_PID=$!
export DISPLAY=:$DISPLAY_NUMBER

echo "Iniciando sesión XFCE (en segundo plano)..."
nohup startxfce4 >/tmp/xfce4.log 2>&1 &

sleep 2

echo "Iniciando x11vnc en display :$DISPLAY_NUMBER ..."
nohup x11vnc -display :$DISPLAY_NUMBER -forever -shared -nopw -rfbport 5901 >/tmp/x11vnc.log 2>&1 &

sleep 1

echo "Iniciando noVNC (websockify) en el puerto 6080 ..."
NOVNC_WEB=/usr/share/novnc
if [ ! -d "$NOVNC_WEB" ]; then
  # Fallback simple: use packaged location if present
  NOVNC_WEB="/usr/share/novnc"
fi
websockify --web $NOVNC_WEB 6080 localhost:5901 >/tmp/novnc.log 2>&1 &

echo "Entorno gráfico iniciado. Accede desde tu navegador en: http://localhost:6080/vnc.html"
echo "Si corres esto en Codespaces/Cloud, publica el puerto 6080 (o usa reenvío SSH/túnel)."

echo "PIDs: XVFB=$XVFB_PID"

exit 0
