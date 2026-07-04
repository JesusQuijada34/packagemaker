import os
import requests
import sys

def setup_webhook():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    # En Render, la URL suele ser la URL de la app
    webhook_url = os.getenv('WEBHOOK_URL') 
    
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN no configurado.")
        return
    
    if not webhook_url:
        print("Error: WEBHOOK_URL no configurado (debe ser la URL de tu app en Render + /api/telegram_webhook).")
        return

    full_url = f"{webhook_url.rstrip('/')}/api/telegram_webhook"
    api_url = f"https://api.telegram.org/bot{token}/setWebhook"
    
    print(f"Configurando webhook en: {full_url}")
    
    try:
        response = requests.post(api_url, json={'url': full_url})
        result = response.json()
        if result.get('ok'):
            print("✅ Webhook configurado correctamente.")
        else:
            print(f"❌ Error al configurar webhook: {result.get('description')}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    setup_webhook()
