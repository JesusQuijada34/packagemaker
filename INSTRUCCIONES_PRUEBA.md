# 🧪 Instrucciones de Prueba - Ventanas de IPM

## Objetivo
Verificar que todas las ventanas implementadas funcionan correctamente y sin errores.

---

## 📋 Pre-requisitos

1. **Python 3.6+** instalado
2. **PyQt5** instalado: `pip install PyQt5`
3. **leviathan-ui** instalado: `pip install leviathan-ui`
4. **Permisos de administrador** (para algunas operaciones)

---

## 🚀 Método 1: Prueba Individual de Ventanas

### Usando el Script de Prueba

1. Abre `test_ventanas.py`
2. Descomenta la línea de la ventana que quieres probar
3. Ajusta las rutas según tu sistema
4. Ejecuta:
   ```bash
   cd packagemaker
   python test_ventanas.py
   ```

### Ejemplo: Probar Crear Proyecto

```python
# En test_ventanas.py, descomenta:
window.showCreateProjectDialog(r"C:\Users\TuUsuario\Documents\test_project")
```

---

## 🧪 Método 2: Prueba desde Menú Contextual

### Instalación de Integración

1. Ejecuta IPM:
   ```bash
   cd packagemaker
   python packagemaker.py
   ```

2. Ve a la pestaña **Configuración**

3. Click en **Instalar Integración con Shell**

4. Espera a que se complete (puede requerir permisos de administrador)

### Prueba de Menús

1. **Crear Proyecto**:
   - Abre el explorador de Windows
   - Navega a una carpeta vacía
   - Click derecho → "Crear Proyecto Aquí"
   - Verifica que se abra la ventana

2. **Instalar Carpeta**:
   - Click derecho en la carpeta `packagemaker`
   - Selecciona "Instalar como Fluthin Package"
   - Verifica que se abra la ventana con log

3. **Compilar Proyecto**:
   - Click derecho en la carpeta `packagemaker`
   - Selecciona "Compilar Proyecto"
   - Verifica opciones de compilación

4. **Reparar Proyecto (MoonFix)**:
   - Click derecho en la carpeta `packagemaker`
   - Selecciona "Reparar Proyecto"
   - Verifica opciones de reparación

5. **Crear MEXF**:
   - Click derecho en cualquier carpeta
   - Selecciona "Crear Archivo MEXF"
   - Verifica formulario de creación

6. **Instalar MEXF**:
   - Click derecho en `example.mexf`
   - Selecciona "Instalar Extensiones MEXF"
   - Verifica que se lea el archivo correctamente

---

## 🧪 Método 3: Prueba desde Línea de Comandos

### Comandos de Prueba

```bash
# Navega a la carpeta packagemaker
cd packagemaker

# 1. Crear Proyecto
python packagemaker.py --create-project "C:\temp\test_project"

# 2. Instalar Carpeta
python packagemaker.py --install-folder "C:\temp\test_project"

# 3. Compilar Proyecto
python packagemaker.py --compile-project "C:\temp\test_project"

# 4. Reparar Proyecto
python packagemaker.py --repair-project "C:\temp\test_project"

# 5. Crear MEXF
python packagemaker.py --create-mexf "C:\temp"

# 6. Instalar MEXF
python packagemaker.py --install-mexf "C:\temp\example.mexf"
```

---

## ✅ Lista de Verificación

### Para Cada Ventana

- [ ] La ventana se abre sin errores
- [ ] El diseño es consistente con LeviathanUI
- [ ] Los efectos visuales (blur, transparencia) funcionan
- [ ] La barra de título personalizada funciona
- [ ] Los botones responden correctamente
- [ ] Los campos de texto aceptan entrada
- [ ] La validación de datos funciona
- [ ] La barra de progreso se anima correctamente
- [ ] El log muestra mensajes en tiempo real
- [ ] Los mensajes de éxito/error aparecen correctamente
- [ ] La ventana se puede cerrar sin problemas

### Ventanas Específicas

#### 1. Crear Proyecto
- [ ] Campos pre-llenados con valores por defecto
- [ ] Validación de nombre vacío funciona
- [ ] Se crea la estructura de carpetas
- [ ] Se genera `details.xml` correctamente
- [ ] Se crea el archivo `.py` principal
- [ ] Mensaje de éxito muestra ruta correcta

#### 2. Instalar Carpeta
- [ ] Verifica estructura del proyecto
- [ ] Crea `details.xml` si no existe
- [ ] Copia archivos a Fluthin Apps
- [ ] Barra de progreso avanza correctamente
- [ ] Log muestra todas las etapas
- [ ] Mensaje de éxito al finalizar

#### 3. Compilar Proyecto
- [ ] Checkboxes funcionan correctamente
- [ ] Opciones de plataforma se pueden seleccionar
- [ ] Log muestra proceso de compilación
- [ ] Barra de progreso avanza por etapas
- [ ] Mensaje de éxito al finalizar

#### 4. Reparar Proyecto (MoonFix)
- [ ] Checkboxes de opciones funcionan
- [ ] Detecta archivos faltantes
- [ ] Crea archivos necesarios
- [ ] Detecta carpetas faltantes
- [ ] Crea carpetas necesarias
- [ ] Reporte de problemas es correcto
- [ ] Log con color cyan funciona

#### 5. Instalar Paquete
- [ ] Verifica existencia del archivo
- [ ] Extrae información del paquete
- [ ] Copia a Fluthin Apps
- [ ] Barra de progreso funciona
- [ ] Mensaje de éxito al finalizar

#### 6. Crear MEXF
- [ ] Campo de nombre acepta texto
- [ ] Campo de descripción acepta texto
- [ ] Validación de nombre vacío funciona
- [ ] Genera archivo .mexf válido
- [ ] JSON tiene estructura correcta
- [ ] Confirmación de sobrescritura funciona

#### 7. Instalar MEXF
- [ ] Lee archivo .mexf correctamente
- [ ] Muestra información del paquete
- [ ] Cuenta mimetypes correctamente
- [ ] Cuenta menús contextuales correctamente
- [ ] Log muestra proceso de instalación
- [ ] Mensaje de éxito al finalizar

---

## 🐛 Errores Comunes y Soluciones

### Error: "No module named 'leviathan_ui'"
**Solución**: Instala leviathan-ui
```bash
pip install leviathan-ui
```

### Error: "No module named 'PyQt5'"
**Solución**: Instala PyQt5
```bash
pip install PyQt5
```

### Error: "Access Denied" al instalar integración
**Solución**: Ejecuta como administrador
```bash
# Click derecho en cmd/powershell → "Ejecutar como administrador"
cd packagemaker
python packagemaker.py
```

### Error: Ventana no se abre
**Solución**: Verifica que todos los archivos estén presentes
```bash
# Verifica que existan:
packagemaker.py
cli_handler.py
shell_integration.py
platform_detector.py
```

### Error: "LeviathanDialog missing argument"
**Solución**: Este error ya fue corregido. Si persiste, verifica que estés usando la versión actualizada de `packagemaker.py`

---

## 📊 Reporte de Pruebas

### Plantilla de Reporte

```
FECHA: ___________
PROBADOR: ___________
SISTEMA: Windows ___ / macOS / Linux

VENTANAS PROBADAS:
[ ] 1. Crear Proyecto
[ ] 2. Instalar Carpeta
[ ] 3. Compilar Proyecto
[ ] 4. Reparar Proyecto (MoonFix)
[ ] 5. Instalar Paquete
[ ] 6. Crear MEXF
[ ] 7. Instalar MEXF
[ ] 8. Abrir Paquete
[ ] 9. Editor MEXF

ERRORES ENCONTRADOS:
1. ___________________________________________
2. ___________________________________________
3. ___________________________________________

SUGERENCIAS:
1. ___________________________________________
2. ___________________________________________
3. ___________________________________________

CALIFICACIÓN GENERAL: ___/10
```

---

## 🎯 Criterios de Éxito

Una ventana pasa la prueba si:

1. ✅ Se abre sin errores de Python
2. ✅ El diseño es visualmente correcto
3. ✅ Todos los controles funcionan
4. ✅ La funcionalidad principal se ejecuta
5. ✅ Los mensajes de feedback son claros
6. ✅ Se puede cerrar sin problemas

---

## 📝 Notas Adicionales

### Rendimiento
- Las ventanas deben abrirse en menos de 1 segundo
- Las operaciones deben completarse sin cuelgues
- La barra de progreso debe animarse suavemente

### Diseño
- Todos los elementos deben ser legibles
- Los colores deben ser consistentes
- Los efectos visuales deben funcionar en todos los sistemas

### Funcionalidad
- Todas las operaciones deben completarse correctamente
- Los errores deben manejarse gracefully
- Los mensajes deben ser informativos

---

## 🚀 Siguiente Paso

Una vez completadas las pruebas:

1. Documenta cualquier error encontrado
2. Reporta sugerencias de mejora
3. Si todo funciona correctamente, ¡el proyecto está listo para producción!

---

**¡Buena suerte con las pruebas!** 🎉
