import os
import requests
import time
import json

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
# Usamos la URL local para reenviar los mensajes al webhook de Flask
WEBHOOK_LOCAL_URL = "http://127.0.0.1:5000/api/telegram_webhook"

def run_polling():
    if not TOKEN:
        print("TELEGRAM_BOT_TOKEN no configurado.")
        return

    print("Iniciando bot en modo polling (segundo plano)...")
    offset = 0
    
    # Eliminar webhook previo para permitir polling
    requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")

    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=30"
            resp = requests.get(url).json()
            
            if resp.get('ok'):
                for update in resp.get('result', []):
                    offset = update['update_id'] + 1
                    # Reenviar a la app Flask localmente
                    try:
                        requests.post(WEBHOOK_LOCAL_URL, json=update, timeout=5)
                    except Exception as e:
                        print(f"Error al reenviar al webhook local: {e}")
            
        except Exception as e:
            print(f"Error en polling: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_polling()
