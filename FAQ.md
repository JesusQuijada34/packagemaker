# ❓ Preguntas Frecuentes - Packagemaker

## 🚀 Instalación

### ¿Qué necesito para usar Packagemaker?
**Requisitos mínimos:**
- Python 3.8 o superior
- PyQt6 6.5+
- 4GB RAM (8GB recomendado para proyectos grandes)
- Windows 10/11 para la interfaz completa
- Linux: compilación `.iflapp` verificada localmente para Danenone
- macOS: funciones básicas; no se verifica compilación cruzada desde macOS

**Instalación:**
```bash
git clone https://github.com/JesusQuijada34/packagemaker.git
cd packagemaker
pip install -r lib/requirements.txt
python packagemaker.py
```

### ¿Funciona en Linux o macOS?
Packagemaker puede ejecutar funciones básicas fuera de Windows. La compilación debe realizarse en un runner nativo de la plataforma objetivo: desde Linux se ha verificado la generación de `.iflapp` para Danenone, mientras que la compilación Windows requiere Windows y no se puede validar desde Linux. macOS no dispone en este repositorio de una ruta de compilación cruzada verificada.

---

## 📦 Compilación y Empaquetado

### ¿Qué es un "script candidato"?
Es un archivo Python que el analizador puede considerar como punto de entrada principal. La selección final debe coincidir con el `<app>` y el script principal definidos en `details.xml`; el bloque siguiente es una convención recomendada, no una garantía suficiente por sí sola:
```python
if __name__ == '__main__':
    main()
```

### ¿La extracción de clases forma parte del contrato actual?
Los términos de extracción automática a `lib/_class/` pertenecen a documentación histórica y no aparecen como una opción activa del CLI v3.2.7. El flujo actual debe validarse mediante `details.xml`, el script principal, la estructura del proyecto y el `.iflapp` resultante; no se debe asumir que una clase será movida automáticamente.

### ¿Cuál es el formato de entrega actual?
La salida validada del flujo actual es un archivo `.iflapp`, que se inspecciona como ZIP y debe contener sus metadatos, binarios y recursos esperados. `Simple Blind`, `Super Blind` y `.iflappb` no son opciones expuestas por el CLI actual y no deben usarse como instrucciones de compilación v3.2.7.

### ¿Por qué mi bundle no ejecuta?
Verifica:
1. **Metadatos**: Confirma que `details.xml` es válido y que `<app>` coincide con el script principal
2. **Estructura**: Comprueba que las carpetas y marcadores requeridos están presentes
3. **Dependencias**: Asegúrate de que las librerías necesarias estén declaradas en `lib/requirements.txt`
4. **Artefacto**: Valida que el `.iflapp` sea un ZIP válido con `details.xml`, binarios y recursos

---

## 🎨 Interface y UX

### ¿Cómo cambio el tema/colores?
El archivo `config/theme.json` no forma parte del repositorio actual. Los estilos se definen en los módulos de interfaz y las preferencias persistentes se almacenan en `data/pm.data`; utiliza las opciones de preferencias disponibles en la aplicación y no crees ese archivo esperando que sea cargado automáticamente.

### ¿Por qué la ventana muestra bordes azules?
Packagemaker hereda el estilo de Leviathan-UI. Para fondo oscuro uniforme:
```python
# Ejemplo para una aplicación Qt propia; no modifica el tema global de PackageMaker
widget.setStyleSheet("background-color: #121822; border: none;")
```

### ¿Cómo personalizo la barra de título?
La barra de título usa `CustomTitleBar` de Leviathan-UI:
```python
self.titlebar = CustomTitleBar(
    self,
    title="Mi App",
    icon="path/to/icon.ico"
)
```

---

## 🤝 Integraciones

### ¿Puedo usar Packagemaker con proyectos existentes?
Sí. Packagemaker detecta automáticamente proyectos Python. Solo:
1. Abre la carpeta del proyecto
2. El IDE escaneará archivos
3. Configura opciones de compilación
4. Compila

### ¿Funciona con virtualenv/conda?
Sí. Packagemaker detecta automáticamente entornos virtuales en el proyecto. Al compilar, incluye las dependencias del entorno activo.

### ¿Puedo compilar para Android?
El repositorio contiene un proyecto Android separado en `android/`, pero el CLI de PackageMaker no expone una opción `Buildozer` ni un comando "Compilar para Android". La compilación Android debe ejecutarse desde ese proyecto con sus herramientas nativas y no se considera una compilación `.iflapp` de PackageMaker.

---

## 🔧 Solución de Problemas

### "No se detectan scripts candidatos"
**Causa**: Tus scripts no tienen el bloque `if __name__ == '__main__'`
**Solución**: Agrega al final de tu script principal:
```python
if __name__ == '__main__':
    main()
```

### "Error: 'lib' no encontrado al ejecutar"
**Causa**: La estructura del proyecto o los metadatos no coinciden con el contrato esperado
**Solución**: 
1. Verifica que `details.xml` y el script principal existen
2. Comprueba las carpetas y marcadores requeridos por el proyecto
3. Recompila desde cero con `python packagemaker.py --buildthis /ruta/al/proyecto`

### "La compilación se congela"
**Causa**: Proyecto muy grande o dependencias circulares
**Solución**:
1. Divide tu proyecto en módulos más pequeños
2. Elimina imports circulares
3. Aumenta timeout en configuración

### "Errores de import tras compilar"
**Causa**: La estructura de imports o las dependencias no se resolvieron al compilar
**Solución**: 
- Usa imports absolutos cuando el proyecto los requiera: `from lib.mi_modulo import X`
- Revisa el log de compilación y declara las dependencias en `lib/requirements.txt`

---

## 💡 Mejores Prácticas

### Estructura recomendada de proyecto
```
mi-proyecto/
├── app/
│   ├── __init__.py
│   └── main.py           # Script candidato
├── lib/                  # Código de soporte (no scripts candidatos)
│   └── utils.py
├── assets/
│   └── icon.ico
├── requirements.txt
├── details.xml           # Metadatos del proyecto
└── manifest.res          # Manifiesto Windows opcional
```

### Optimización de compilación
1. **Excluye archivos innecesarios**: Mantén un `.gitignore` correcto; el compilador aplica sus patrones declarados
2. **Optimiza assets**: Comprime imágenes antes de compilar sin eliminar recursos requeridos
3. **Valida el artefacto**: Comprueba el ZIP, `details.xml`, binarios y recursos antes de distribuir
4. **Conserva las fuentes**: El proyecto fuente no debe eliminarse como efecto secundario de la compilación

---

## 📞 Soporte

¿No encuentras tu respuesta?
- Abre un [Issue en GitHub](https://github.com/JesusQuijada34/packagemaker/issues)
- Consulta el índice disponible en `docs/index.html`
- Revisa `README.md`, `CHANGELOG.md` y `RELEASE_NOTES.md`

---

**Última actualización**: 2026-08-19 | **Versión**: v3.2.7-26.05-20.13
