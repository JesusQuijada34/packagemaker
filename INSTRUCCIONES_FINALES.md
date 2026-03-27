# 📖 INSTRUCCIONES FINALES - Shell Integration IPM

## ✅ Estado Actual

El sistema está funcionando correctamente. Los scripts están listos y detectan las rutas correctamente.

---

## 🚀 INSTALACIÓN (IMPORTANTE)

### Paso 1: Ejecutar como Administrador

**Opción A - Usando el script batch (MÁS FÁCIL)**:
1. Busca el archivo `INSTALAR_SHELL.bat`
2. Click derecho → "Ejecutar como administrador"
3. Acepta el diálogo de permisos
4. Espera a que termine

**Opción B - Usando PowerShell**:
1. Click derecho en PowerShell → "Ejecutar como administrador"
2. Navega a la carpeta:
   ```powershell
   cd "C:\Users\Jesus Quijada\Documents\GitHub\packagemaker"
   ```
3. Ejecuta:
   ```powershell
   python shell_integration.py --install
   ```

### Paso 2: Verificar Instalación

Deberías ver:
```
[ShellIntegration] Instalando menús contextuales...
  ✓ Registrado: 🆕 Crear Proyecto Aquí
  ✓ Registrado: 📦 Instalar como Fluthin Package
  ✓ Registrado: 🔨 Compilar Proyecto
  ✓ Registrado: 🌙 Reparar Proyecto (MoonFix)
  ✓ Registrado: 🆕 Nuevo Proyecto IPM
  ✓ Registrados menús para .iflapp
[ShellIntegration] Instalando soporte MEXF...
  ✓ Registrado soporte MEXF
[ShellIntegration] ✓ Integración completada
```

**Si ves errores de "Acceso denegado"**: No estás ejecutando como administrador.

---

## 🧪 PRUEBA MANUAL

### Probar el Script Directamente

```bash
# Abrir terminal normal (no necesita admin)
cd packagemaker
python packagemaker-shell.py --create-project "C:\temp\test"
```

**Resultado esperado**: Se abre una ventana para crear proyecto

**Si no se abre nada**: Verifica que Python y PyQt5 estén instalados

---

## 🔍 VERIFICAR QUÉ SE REGISTRÓ

### Ver el Comando Registrado

```bash
python VER_COMANDO_REGISTRADO.py
```

Esto te mostrará exactamente qué comando se registró en el shell.

### Verificar en el Registro de Windows

1. Presiona `Win + R`
2. Escribe `regedit` y presiona Enter
3. Navega a: `HKEY_CLASSES_ROOT\Directory\shell\IPM_CreateProject\command`
4. Verifica que el valor sea algo como:
   ```
   "C:\Program Files\Python314\pythonw.exe" "C:\...\packagemaker-shell.py" --create-project "%1"
   ```

---

## 🎯 PROBAR EN EL EXPLORADOR

### Paso 1: Abrir Explorador de Windows

1. Presiona `Win + E`
2. Navega a cualquier carpeta

### Paso 2: Click Derecho

1. Click derecho en una carpeta
2. Deberías ver: "🆕 Crear Proyecto Aquí"

### Paso 3: Click en la Opción

1. Click en "Crear Proyecto Aquí"
2. **Debe abrirse**: Una ventana para crear proyecto
3. **La ventana debe mostrar**: La ruta de la carpeta seleccionada

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Problema 1: No aparecen los menús

**Causa**: No se instaló correctamente o no tienes permisos

**Solución**:
1. Ejecuta como administrador: `INSTALAR_SHELL.bat`
2. Reinicia el Explorador de Windows:
   ```bash
   taskkill /f /im explorer.exe
   start explorer.exe
   ```
3. Si persiste, reinicia Windows

### Problema 2: Los menús aparecen pero no pasa nada al hacer click

**Causa**: El comando en el registro está mal o Python no está en el PATH

**Solución**:
1. Ejecuta: `python VER_COMANDO_REGISTRADO.py`
2. Copia el comando que muestra
3. Pégalo en una terminal y prueba si funciona
4. Si no funciona, verifica que Python esté instalado correctamente

### Problema 3: Se abre una consola negra

**Causa**: Está usando `python.exe` en lugar de `pythonw.exe`

**Solución**: Ya está corregido en `shell_integration.py`, reinstala:
```bash
python shell_integration.py --uninstall
python shell_integration.py --install
```

### Problema 4: Error "pythonw.exe no encontrado"

**Causa**: Python no está instalado correctamente

**Solución**:
1. Verifica que Python esté instalado
2. Verifica que `pythonw.exe` existe en la carpeta de Python
3. Si no existe, reinstala Python

---

## 📝 COMANDOS ÚTILES

### Ver Información de Detección
```bash
python VER_COMANDO_REGISTRADO.py
```

### Instalar Integración
```bash
# Como administrador
python shell_integration.py --install
```

### Desinstalar Integración
```bash
# Como administrador
python shell_integration.py --uninstall
```

### Probar Script Directamente
```bash
python packagemaker-shell.py --create-project "C:\temp\test"
python packagemaker-shell.py --create-mexf "C:\temp"
```

---

## ✅ CHECKLIST DE VERIFICACIÓN

- [ ] Python instalado y en el PATH
- [ ] PyQt5 instalado (`pip install PyQt5`)
- [ ] Ejecutado `INSTALAR_SHELL.bat` como administrador
- [ ] Visto mensajes de éxito (✓) en la instalación
- [ ] Reiniciado el Explorador de Windows
- [ ] Verificado que aparecen los menús al hacer click derecho
- [ ] Probado hacer click en una opción
- [ ] Se abre la ventana correctamente

---

## 🎯 RESULTADO ESPERADO

### Cuando Todo Funciona

1. **Click derecho en carpeta** → Aparece "🆕 Crear Proyecto Aquí"
2. **Click en la opción** → Se abre ventana (sin consola negra)
3. **Ventana muestra** la ruta correcta de la carpeta
4. **Puedes llenar** el formulario (nombre, versión, autor, etc.)
5. **Click en "Crear Proyecto"** → Proyecto se crea
6. **Mensaje de éxito** → "Proyecto creado en: ..."
7. **Ventana se cierra** → Puedes ver el proyecto creado

---

## 📞 SI NADA FUNCIONA

### Opción 1: Reinstalar Todo

```bash
# Como administrador
python shell_integration.py --uninstall
python shell_integration.py --install
```

### Opción 2: Verificar Manualmente

1. Ejecuta: `python VER_COMANDO_REGISTRADO.py`
2. Copia el comando que muestra
3. Pégalo en una terminal (reemplaza `%1` por una ruta real)
4. Si funciona manualmente pero no desde el explorador, el problema está en el registro

### Opción 3: Verificar Registro

1. Abre `regedit`
2. Busca `IPM_CreateProject`
3. Verifica que el comando sea correcto
4. Si está mal, desinstala y reinstala

---

## 📊 INFORMACIÓN TÉCNICA

### Comando Registrado

El comando que se registra en el shell es:
```
"C:\Program Files\Python314\pythonw.exe" "C:\...\packagemaker-shell.py" --create-project "%1"
```

Donde:
- `pythonw.exe` = Python sin consola
- `packagemaker-shell.py` = Script que maneja las ventanas
- `--create-project` = Argumento que indica qué hacer
- `"%1"` = Ruta de la carpeta seleccionada

### Archivos Importantes

- `packagemaker-shell.py` - Maneja las ventanas
- `shell_integration.py` - Instala/desinstala la integración
- `VER_COMANDO_REGISTRADO.py` - Muestra qué se registrará
- `INSTALAR_SHELL.bat` - Instala como administrador
- `TEST_SHELL.bat` - Prueba el script directamente

---

**¡Sigue estas instrucciones y todo funcionará!** 🎉

**Fecha**: 2026-03-08
**Estado**: ✅ LISTO PARA USAR
