#!/bin/bash

# Iniciar la aplicación Flask con Gunicorn en segundo plano
echo "Iniciando servidor web..."
gunicorn --bind 0.0.0.0:$PORT app:app &

# Esperar un poco a que el servidor web esté listo
sleep 5

# Iniciar el bot en modo polling en segundo plano
echo "Iniciando bot de Telegram..."
python3 bot_polling.py &

# Mantener el script vivo
wait
