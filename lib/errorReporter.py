import sys
import traceback
import requests
import json
import os
import platform
from datetime import datetime

class ErrorReporter:
    def __init__(self, api_url):
        self.api_url = api_url

    def report_exception(self, exc_type, exc_value, exc_traceback):
        """
        Captura y envía los detalles de una excepción a la API de Flask.
        """
        # Formatear el traceback
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        tb_text = "".join(tb_lines)

        # Recopilar datos básicos del entorno (sin violar la privacidad)
        payload = {
            "timestamp": datetime.now().isoformat(),
            "exception_type": str(exc_type.__name__),
            "exception_message": str(exc_value),
            "traceback": tb_text,
            "environment": {
                "os": platform.system(),
                "os_release": platform.release(),
                "python_version": sys.version.split()[0],
                "termux": "TERMUX_VERSION" in os.environ
            }
        }

        try:
            # Enviar la carga útil mediante una petición HTTP POST
            # Nota: En una aplicación GUI real, esto debería ser asíncrono.
            # Para este script, usamos requests de forma directa con un timeout.
            response = requests.post(
                self.api_url, 
                json=payload, 
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error al reportar telemetría: {e}")
            return False

def setup_global_reporter(api_url):
    """
    Configura el capturador global de excepciones.
    """
    reporter = ErrorReporter(api_url)

    def global_excepthook(exc_type, exc_value, exc_traceback):
        # Primero reportar el error
        reporter.report_exception(exc_type, exc_value, exc_traceback)
        # Luego llamar al excepthook original para que el programa maneje el error normalmente
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = global_excepthook
    return reporter
