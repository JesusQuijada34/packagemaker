#!/bin/bash

# Función para limpiar procesos al salir
cleanup() {
    echo "Deteniendo procesos..."
    kill "$(jobs -p)"
    exit
}

trap cleanup SIGINT SIGTERM

echo "--- Iniciando Entorno Packagemaker ---"

# 1. Configurar Webhook primero (si aplica)
# Esto es rápido y no bloqueante, asegura que Telegram sepa a dónde enviar mensajes
if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$WEBHOOK_URL" ]; then
    echo "[Telegram] Configurando Webhook..."
    python3 setup_webhook.py
fi

# El bot ahora se gestiona principalmente vía Webhook en app.py.
# bot_polling.py queda como respaldo manual si se desea ejecutar localmente.

# 3. Iniciar el servidor Flask con Gunicorn
# IMPORTANTE: Gunicorn debe ser el proceso principal que mantenga vivo el contenedor/instancia en Render.
# Lo ejecutamos en PRIMER PLANO al final para que Render monitoree este proceso.
echo "[Web] Iniciando servidor Flask con Gunicorn en puerto ${PORT:-5000}..."
exec gunicorn --bind "0.0.0.0:${PORT:-5000}" --workers 2 --threads 4 --timeout 120 app:app
