# ❓ Preguntas Frecuentes - Packagemaker

## 🚀 Instalación

### ¿Qué necesito para usar Packagemaker?
**Requisitos mínimos:**
- Python 3.8 o superior
- PyQt6 6.5+
- 4GB RAM (8GB recomendado para proyectos grandes)
- Windows 10/11 (Linux/macOS con funcionalidad limitada)

**Instalación:**
```bash
git clone https://github.com/tuusuario/packagemaker.git
cd packagemaker
pip install -r requirements.txt
python packagemaker.py
```

### ¿Funciona en Linux o macOS?
Packagemaker está optimizado para Windows. Las funciones básicas funcionan en Linux/macOS, pero:
- La compilación a `.exe` no está disponible
- Algunos efectos visuales pueden no renderizar igual
- Se recomienda usar máquina virtual Windows para desarrollo multiplataforma

---

## 📦 Compilación y Empaquetado

### ¿Qué es un "script candidato"?
Es un archivo Python que Packagemaker detecta como punto de entrada principal. Debe contener:
```python
if __name__ == '__main__':
    # Código de entrada
    main()
```

### ¿Cómo funciona la extracción de clases?
Packagemaker analiza AST (Abstract Syntax Tree) del código y:
1. Detecta clases definidas en nivel superior
2. Mueve cada clase a archivo separado en `lib/_class/ScriptName/`
3. Actualiza el script original para importar desde nuevo path
4. Genera `lib/__init__.py` con imports consolidados

### ¿Cuál es la diferencia entre Simple Blind y Super Blind?

| Característica | Simple Blind | Super Blind |
|----------------|--------------|-------------|
| Estructura | Un archivo `.iflappb` | Múltiples carpetas organizadas |
| Seguridad | Estándar | Alta |
| Descompilación | Difícil | Muy difícil |
| Compatibilidad | Universal | Requiere instalador especial |
| Uso recomendado | Apps simples | Apps enterprise |

### ¿Por qué mi bundle no ejecuta?
Verifica:
1. **Clases extraídas**: Revisa que `lib/_class/` contiene los archivos
2. **Imports**: Confirma que `lib/__init__.py` tiene los imports correctos
3. **Dependencias**: Asegúrate que todas las librerías estén en `requirements.txt`
4. **Script principal**: El entry point debe estar bien definido en `manifest.yaml`

---

## 🎨 Interface y UX

### ¿Cómo cambio el tema/colores?
Edita `config/theme.json`:
```json
{
  "primary": "#ff5722",
  "background": "#121822",
  "accent": "#00d4aa"
}
```

### ¿Por qué la ventana muestra bordes azules?
Packagemaker hereda el estilo de Leviathan-UI. Para fondo oscuro uniforme:
```python
# En tu código (automático en v1.0.0)
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
Sí, pero requiere configuración adicional:
1. Instala Buildozer: `pip install buildozer`
2. Configura `buildozer.spec` en raíz del proyecto
3. Usa opción "Compilar para Android" en Packagemaker

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
**Causa**: La estructura de carpetas se rompió durante extracción
**Solución**: 
1. Verifica que `lib/_class/` existe
2. Revisa que `lib/__init__.py` tiene contenido
3. Recompila desde cero: `Build → Clean & Rebuild`

### "La compilación se congela"
**Causa**: Proyecto muy grande o dependencias circulares
**Solución**:
1. Divide tu proyecto en módulos más pequeños
2. Elimina imports circulares
3. Aumenta timeout en configuración

### "Errores de import tras compilar"
**Causa**: Imports relativos mal manejados
**Solución**: 
- Usa imports absolutos: `from lib.mi_modulo import X`
- Evita imports con `*` en clases extraídas

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
└── manifest.yaml         # Generado por Packagemaker
```

### Optimización de compilación
1. **Excluye archivos innecesarios**: Usa `.pmignore` (similar a `.gitignore`)
2. **Minifica assets**: Comprime imágenes antes de compilar
3. **Usa Simple Blind**: Para apps pequeñas (más rápido)
4. **Cache de análisis**: Habilita en configuración para recompilaciones rápidas

---

## 📞 Soporte

¿No encuentras tu respuesta?
- Abre un [Issue en GitHub](../../issues)
- Consulta la documentación en `docs/`
- Revisa ejemplos en `examples/`

---

**Última actualización**: 2026-04-09 | **Versión**: 1.0.0
