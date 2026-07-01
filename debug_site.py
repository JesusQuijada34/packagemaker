import sys
from app import app

def test_routes():
    print("Iniciando depuración de rutas...")
    client = app.test_client()
    
    routes = ['/', '/release-notes', '/faq']
    
    for route in routes:
        print(f"Probando ruta: {route}")
        response = client.get(route)
        if response.status_code == 200:
            print(f"  [OK] {route} cargada correctamente.")
        else:
            print(f"  [ERROR] {route} devolvió status {response.status_code}")
            return False
            
    print("Todas las rutas principales funcionan correctamente.")
    return True

if __name__ == "__main__":
    if test_routes():
        print("Depuración completada con éxito.")
        sys.exit(0)
    else:
        print("La depuración falló.")
        sys.exit(1)
