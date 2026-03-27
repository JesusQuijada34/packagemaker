# 🧪 PRUEBA COMPLETA - Diagnóstico de Shell Integration

## 📋 Pasos para Diagnosticar el Problema

### Paso 1: Reinstalar la Integración

```bash
# Como ADMINISTRADOR
cd packagemaker
python shell_integration.py --uninstall
python shell_integration.py --install
```

**Verifica que veas**:
```
✓ Registrado: 🆕 Crear Proyecto Aquí
✓ Registrado: 📦 Instalar como Fluthin Package
...
✓ Integración completada
```

### Paso 2: Probar Manualmente

```bash
# Terminal normal (no admin)
cd packagemaker
python packagemaker-shell.py --create-project "C:\temp\test"
```

**Debe abrirse una ventana**. Si no se abre, hay un problema con PyQt5.

### Paso 3: Probar desde el Explorador

1. Abre el Explorador de Windows
2. Navega a cualquier carpeta
3. Click derecho en una carpeta
4. Click en "🆕 Crear Proyecto Aquí"

### Paso 4: Ver el Log de Debug

```bash
# Ejecuta este script
VER_LOG.bat
```

Esto te mostrará exactamente qué está pasando cuando haces click en el menú.

---

## 🔍 Qué Buscar en el Log

### Si el Log está Vacío

**Problema**: El comando no se está ejecutando

**Causas posibles**:
1. No se instaló correctamente (no ejecutaste como admin)
2. El comando en el registro está mal
3. Python no está en el PATH

**Solución**:
1. Reinstala como administrador
2. Verifica el registro: `regedit` → `HKEY_CLASSES_ROOT\Directory\shell\IPM_CreateProject\command`

### Si el Log Muestra Errores de Importación

**Problema**: PyQt5 no está instalado o no se encuentra

**Solución**:
```bash
pip install PyQt5
```

### Si el Log Muestra "Diálogo creado" pero no se ve

**Problema**: La ventana se está creando pero no se muestra

**Solución**: Puede ser un problema de foco. Intenta:
1. Presiona `Alt+Tab` para ver si la ventana está oculta
2. Verifica que no haya otra ventana bloqueándola

---

## 🐛 Diagnóstico Paso a Paso

### Test 1: Verificar Python

```bash
python --version
```

Debe mostrar Python 3.x

### Test 2: Verificar PyQt5

```bash
python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')"
```

Debe mostrar "PyQt5 OK"

### Test 3: Verificar Script

```bash
python packagemaker-shell.py --create-project "%CD%"
```

Debe abrir una ventana

### Test 4: Verificar Comando Registrado

```bash
python VER_COMANDO_REGISTRADO.py
```

Copia el comando y ejecútalo manualmente

### Test 5: Verificar Registro de Windows

1. `Win + R` → `regedit`
2. Navega a: `HKEY_CLASSES_ROOT\Directory\shell\IPM_CreateProject\command`
3. Verifica que el valor sea correcto

---

## 📊 Tabla de Diagnóstico

| Síntoma | Causa Probable | Solución |
|---------|----------------|----------|
| No aparecen menús | No instalado como admin | Ejecutar `INSTALAR_SHELL.bat` como admin |
| Menús aparecen pero no pasa nada | Comando mal registrado | Reinstalar integración |
| Error de PyQt5 | PyQt5 no instalado | `pip install PyQt5` |
| Log vacío | Comando no se ejecuta | Verificar registro de Windows |
| Ventana no se ve | Problema de foco | Presionar `Alt+Tab` |

---

## ✅ Checklist de Verificación

- [ ] Python instalado y funciona
- [ ] PyQt5 instalado (`pip install PyQt5`)
- [ ] Script funciona manualmente
- [ ] Integración instalada como administrador
- [ ] Menús aparecen en el explorador
- [ ] Log se crea al hacer click
- [ ] Log no muestra errores

---

## 📞 Si Todo Falla

### Opción 1: Usar python.exe en lugar de pythonw.exe

Edita `shell_integration.py` y cambia:
```python
pythonExe = sys.executable.replace("python.exe", "pythonw.exe")
```

Por:
```python
pythonExe = sys.executable  # Usar python.exe para ver errores
```

Reinstala y verás una consola con errores.

### Opción 2: Verificar Permisos

Asegúrate de que:
1. Tienes permisos de administrador
2. El antivirus no está bloqueando
3. Windows Defender no está bloqueando

### Opción 3: Reinstalar Python

Si nada funciona, puede ser que Python esté mal instalado.

---

## 🎯 Resultado Esperado

Cuando todo funciona:

1. **Click derecho** → Aparecen opciones de IPM
2. **Click en opción** → Se ejecuta el script
3. **Log se crea** → Muestra "INICIO DE EJECUCIÓN"
4. **Ventana se abre** → Puedes ver el formulario
5. **Sin errores** → Todo funciona perfectamente

---

**¡Sigue estos pasos y encontraremos el problema!** 🔍
