#!/bin/bash

# Iniciar la aplicación Flask con Gunicorn en segundo plano
echo "Iniciando servidor web..."
gunicorn --bind 0.0.0.0:$PORT app:app &

# Esperar un poco a que el servidor web esté listo
sleep 5

# Configurar Webhook si las variables están presentes
if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$WEBHOOK_URL" ]; then
    echo "Configurando Webhook de Telegram..."
    python3 setup_webhook.py
else
    # Si no hay Webhook configurado, intentar Polling como respaldo
    echo "TELEGRAM_BOT_TOKEN o WEBHOOK_URL no configurados. Iniciando bot en modo polling..."
    python3 bot_polling.py &
fi

# Mantener el script vivo
wait
