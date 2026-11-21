import logging
import traceback
import sys
from datetime import datetime

class LeviathanDebugger:
    """
    Herramienta de depuración robusta para Leviathan.
    Captura errores inesperados y los muestra de forma legible.
    """
    @staticmethod
    def setup_logging(log_file="debug.log"):
        try:
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                handlers=[
                    logging.FileHandler(log_file, encoding='utf-8'),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        except Exception as e:
            print(f"⚠️ No se pudo iniciar el logging: {e}")

    @staticmethod
    def parse_error(e):
        """Devuelve un resumen formateado del error para la terminal."""
        ts = datetime.now().strftime("%H:%M:%S")
        error_type = type(e).__name__
        msg = str(e)
        tb = traceback.format_exc()
        return f"\n{'='*50}\n[{ts}] ❌ ERROR ({error_type}): {msg}\n--- TRACEBACK ---\n{tb}{'='*50}\n"

def _handle_exception(exc_type, exc_value, exc_traceback):
    """Manejador global de excepciones no capturadas."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    error_msg = LeviathanDebugger.parse_error(exc_value)
    logging.critical("Excepción no capturada:", exc_info=(exc_type, exc_value, exc_traceback))
    print(error_msg, file=sys.stderr)

def install_debugger(log_file="debug.log"):
    """
    Instala el sistema de depuración global. 
    Llama a esto al principio de tu archivo principal.
    """
    sys.excepthook = _handle_exception
    LeviathanDebugger.setup_logging(log_file)
    print("🚀 Depurador Leviathan Activado")
