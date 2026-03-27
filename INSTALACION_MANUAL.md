# 📖 Instalación Manual de Integración Shell - IPM

## 🎯 Objetivo

Instalar manualmente la integración de IPM con el shell de Windows para tener acceso a los menús contextuales en el explorador de archivos.

---

## ⚠️ Requisitos Previos

1. **Permisos de Administrador** - Necesarios para modificar el registro de Windows
2. **Python instalado** - Para ejecutar los scripts
3. **IPM descargado** - En una ubicación permanente (no en carpetas temporales)

---

## 🚀 Método 1: Script de Instalación (Recomendado)

### Paso 1: Abrir Terminal como Administrador

1. Presiona `Win + X`
2. Selecciona "Windows PowerShell (Administrador)" o "Terminal (Administrador)"
3. Acepta el diálogo de permisos

### Paso 2: Navegar a la Carpeta de IPM

```bash
cd "C:\Users\TuUsuario\Documents\GitHub\packagemaker"
# Ajusta la ruta según donde tengas IPM
```

### Paso 3: Ejecutar Script de Instalación

```bash
python shell_integration.py --install
```

### Paso 4: Verificar Instalación

Deberías ver algo como:

```
[ShellIntegration] Ruta ejecutable: C:\...\packagemaker.py
[ShellIntegration] Ruta icono: C:\...\app\app-icon.ico
[ShellIntegration] Instalando menús contextuales...
  ✓ Registrado: 🆕 Crear Proyecto Aquí
  ✓ Registrado: 📦 Instalar como Fluthin Package
  ✓ Registrado: 🔨 Compilar Proyecto
  ✓ Registrado: 🌙 Reparar Proyecto (MoonFix)
  ✓ Registrado: 🆕 Nuevo Proyecto IPM
  ✓ Registrados menús para .iflapp
[ShellIntegration] Instalando soporte MEXF...
  ✓ Registrado soporte MEXF
[ShellIntegration] Notificando cambios al sistema...
  ✓ Sistema notificado de cambios
[ShellIntegration] ✓ Integración completada
```

### Paso 5: Probar en el Explorador

1. Abre el Explorador de Windows
2. Navega a cualquier carpeta
3. Click derecho → Deberías ver las opciones de IPM

---

## 🔧 Método 2: Script Batch (Más Fácil)

### Paso 1: Ejecutar TEST_INTEGRACION.bat

1. Navega a la carpeta `packagemaker`
2. Click derecho en `TEST_INTEGRACION.bat`
3. Selecciona "Ejecutar como administrador"
4. Sigue las instrucciones en pantalla

---

## 🗑️ Desinstalación

### Opción 1: Script

```bash
# Como administrador
cd packagemaker
python shell_integration.py --uninstall
```

### Opción 2: Manual

1. Abre el Editor del Registro (`Win + R` → `regedit`)
2. Navega a `HKEY_CLASSES_ROOT`
3. Elimina estas claves:
   - `Directory\shell\IPM_CreateProject`
   - `Directory\shell\IPM_InstallFolder`
   - `Directory\shell\IPM_CompileProject`
   - `Directory\shell\IPM_RepairProject`
   - `Directory\Background\shell\IPM_CreateProjectHere`
   - `Directory\Background\shell\IPM_CreateMEXF`
   - `.iflapp`
   - `InfluentPackage`
   - `.mexf`
   - `MarkedExtensionsFile`

---

## 🧪 Verificación de Funcionamiento

### 1. Verificar Menús Contextuales

**En Carpetas** (click derecho en una carpeta):
- ✅ 🆕 Crear Proyecto Aquí
- ✅ 📦 Instalar como Fluthin Package
- ✅ 🔨 Compilar Proyecto
- ✅ 🌙 Reparar Proyecto (MoonFix)

**En Fondo de Carpeta** (click derecho en espacio vacío):
- ✅ 🆕 Nuevo Proyecto IPM
- ✅ 📝 Crear Archivo MEXF

**En Archivos .iflapp**:
- ✅ 📥 Instalar Paquete
- ✅ 📄 Abrir con IPM

**En Archivos .mexf**:
- ✅ 🔧 Instalar Extensiones
- ✅ ✏️ Editar con IPM

### 2. Verificar que se Abren Ventanas

1. Click derecho en una carpeta → "Crear Proyecto Aquí"
2. **Debe abrirse**: IPM con la ventana de crear proyecto
3. **La ventana debe mostrar**: La ruta de la carpeta seleccionada

---

## 🐛 Solución de Problemas

### Problema: No aparecen los menús

**Solución 1**: Reiniciar el Explorador
```bash
# Como administrador
taskkill /f /im explorer.exe
start explorer.exe
```

**Solución 2**: Reinstalar
```bash
python shell_integration.py --uninstall
python shell_integration.py --install
```

**Solución 3**: Reiniciar Windows

### Problema: Se abre IPM pero sin ventana

**Causa**: El comando en el registro está mal formado

**Solución**:
1. Abre el Editor del Registro (`regedit`)
2. Navega a: `HKEY_CLASSES_ROOT\Directory\shell\IPM_CreateProject\command`
3. Verifica que el valor sea algo como:
   ```
   "C:\Python\python.exe" "C:\...\packagemaker.py" --create-project "%1"
   ```
4. Si está mal, reinstala la integración

### Problema: Error "No se puede ejecutar esta aplicación"

**Causa**: La ruta en el registro no es correcta

**Solución**:
1. Verifica que `packagemaker.py` existe en la ruta registrada
2. Reinstala la integración desde la ubicación correcta
3. No muevas IPM después de instalar la integración

### Problema: Errores de explorer.exe

**Causa**: Comando mal formado en el registro

**Solución**:
1. Desinstala la integración
2. Verifica que no haya caracteres especiales en las rutas
3. Reinstala la integración

---

## 📝 Comandos Útiles

### Ver Rutas Detectadas
```bash
cd packagemaker
python shell_integration.py
```

### Instalar
```bash
python shell_integration.py --install
```

### Desinstalar
```bash
python shell_integration.py --uninstall
```

### Probar Comando Específico
```bash
python packagemaker.py --create-project "C:\temp\test"
```

---

## ✅ Checklist de Instalación

- [ ] Ejecutar terminal como administrador
- [ ] Navegar a carpeta de IPM
- [ ] Ejecutar `python shell_integration.py --install`
- [ ] Ver mensajes de éxito en consola
- [ ] Abrir Explorador de Windows
- [ ] Verificar que aparecen menús contextuales
- [ ] Probar una opción (ej: Crear Proyecto Aquí)
- [ ] Verificar que se abre IPM con ventana correcta

---

## 🎯 Resultado Esperado

Cuando todo funciona correctamente:

1. **Click derecho en carpeta** → "Crear Proyecto Aquí"
2. **Se abre IPM** con la ventana de crear proyecto
3. **La ventana muestra** la ruta de la carpeta seleccionada
4. **Puedes llenar** el formulario y crear el proyecto
5. **El proyecto se crea** en la carpeta seleccionada

---

## 📞 Notas Importantes

1. **No muevas IPM** después de instalar la integración
2. **Ejecuta siempre como administrador** para instalar/desinstalar
3. **Reinicia el explorador** si los menús no aparecen inmediatamente
4. **Verifica las rutas** en el registro si algo no funciona

---

## 🔗 Archivos Relacionados

- `shell_integration.py` - Script de integración
- `TEST_INTEGRACION.bat` - Script de prueba
- `SOLUCION_COMPLETA.md` - Guía completa de solución
- `RESUMEN_CORRECCION.md` - Resumen de cambios

---

**¡La integración manual es simple y funciona perfectamente!** 🎉
