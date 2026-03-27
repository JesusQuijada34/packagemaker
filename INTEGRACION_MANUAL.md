# Guía de Integración Manual

Si prefieres integrar manualmente los componentes o personalizarlos, sigue esta guía.

## Métodos Agregados a PackageTodoGUI

Los siguientes métodos ya han sido agregados a la clase `PackageTodoGUI` en `packagemaker.py`:

```python
def set_project_path(self, path):
    """Establece la ruta del proyecto"""
    
def show_create_project_dialog(self, path):
    """Muestra diálogo para crear proyecto"""
    
def show_install_folder_dialog(self, path):
    """Muestra diálogo para instalar carpeta"""
    
def set_compile_path(self, path):
    """Establece ruta de compilación"""
    
def show_compile_dialog(self, path):
    """Muestra diálogo de compilación"""
    
def show_repair_dialog(self, path):
    """Muestra diálogo de MoonFix"""
    
def show_install_package_dialog(self, file_path):
    """Muestra diálogo para instalar .iflapp"""
    
def open_package_file(self, file_path):
    """Abre paquete en gestor"""
    
def show_install_mexf_dialog(self, file_path):
    """Muestra diálogo para instalar .mexf"""
    
def open_mexf_editor(self, file_path):
    """Abre editor de .mexf"""
    
def show_create_mexf_dialog(self, path):
    """Muestra diálogo para crear .mexf"""
```

## Personalización de Diálogos

Si quieres personalizar los diálogos, edita los métodos en `packagemaker.py`.

### Ejemplo: Diálogo Personalizado para Crear Proyecto

```python
def show_create_project_dialog(self, path):
    """Muestra un diálogo personalizado para crear proyecto"""
    try:
        from leviathan_ui import LeviathanDialog
        
        dialog = LeviathanDialog(self, title="Crear Proyecto Aquí")
        dialog.resize(600, 500)
        
        layout = QVBoxLayout()
        
        # Título
        lbl_title = QLabel(f"Crear proyecto en:\n{path}")
        lbl_title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(lbl_title)
        
        # Nombre del proyecto
        lbl_name = QLabel("Nombre del proyecto:")
        lbl_name.setStyleSheet("color: white;")
        layout.addWidget(lbl_name)
        
        txt_name = QLineEdit()
        txt_name.setText(os.path.basename(path))
        txt_name.setStyleSheet("""
            background-color: rgba(255,255,255,0.1);
            color: white;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 4px;
            padding: 8px;
        """)
        layout.addWidget(txt_name)
        
        # Versión
        lbl_version = QLabel("Versión:")
        lbl_version.setStyleSheet("color: white;")
        layout.addWidget(lbl_version)
        
        txt_version = QLineEdit("1.0")
        txt_version.setStyleSheet("""
            background-color: rgba(255,255,255,0.1);
            color: white;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 4px;
            padding: 8px;
        """)
        layout.addWidget(txt_version)
        
        # Autor
        lbl_author = QLabel("Autor:")
        lbl_author.setStyleSheet("color: white;")
        layout.addWidget(lbl_author)
        
        txt_author = QLineEdit()
        txt_author.setStyleSheet("""
            background-color: rgba(255,255,255,0.1);
            color: white;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 4px;
            padding: 8px;
        """)
        layout.addWidget(txt_author)
        
        layout.addStretch()
        
        # Botones
        btn_layout = QHBoxLayout()
        
        btn_create = QPushButton("Crear Proyecto")
        btn_create.setStyleSheet("""
            background-color: rgba(230,244,234,0.82);
            color: rgba(5,98,55,0.99);
            border-radius: 9px;
            padding: 10px 20px;
            font-weight: 600;
        """)
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet("""
            background-color: rgba(243,246,251,0.85);
            color: rgba(32,33,36,0.96);
            border-radius: 9px;
            padding: 10px 20px;
            font-weight: 600;
        """)
        
        btn_layout.addWidget(btn_create)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        dialog.set_content_layout(layout)
        
        # Conectar botones
        btn_cancel.clicked.connect(dialog.close)
        btn_create.clicked.connect(
            lambda: self._create_project_action(
                path,
                txt_name.text(),
                txt_version.text(),
                txt_author.text(),
                dialog
            )
        )
        
        dialog.exec_()
        
    except Exception as e:
        print(f"Error mostrando diálogo: {e}")

def _create_project_action(self, path, name, version, author, dialog):
    """Acción para crear el proyecto"""
    try:
        # Crear carpetas
        project_path = os.path.join(path, name)
        os.makedirs(project_path, exist_ok=True)
        
        folders = ["app", "assets", "config", "docs", "source", "lib"]
        for folder in folders:
            os.makedirs(os.path.join(project_path, folder), exist_ok=True)
        
        # Crear details.xml
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<package>
    <app>{name}</app>
    <version>{version}</version>
    <platform>Windows</platform>
    <author>{author}</author>
    <publisher>{author}</publisher>
    <description>Proyecto creado con Influent Package Maker</description>
</package>"""
        
        with open(os.path.join(project_path, "details.xml"), 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        # Crear archivo principal
        with open(os.path.join(project_path, f"{name}.py"), 'w', encoding='utf-8') as f:
            f.write(f'#!/usr/bin/env python\n# -*- coding: utf-8 -*-\n"""\n{name}\n"""\n\nif __name__ == "__main__":\n    print("Hello from {name}!")\n')
        
        QMessageBox.information(
            self,
            "Proyecto Creado",
            f"Proyecto '{name}' creado exitosamente en:\n{project_path}"
        )
        
        dialog.close()
        
    except Exception as e:
        QMessageBox.critical(self, "Error", f"Error creando proyecto: {e}")
```

## Agregar Nuevos Menús Contextuales

Para agregar un nuevo menú contextual, edita `shell_integration.py`:

```python
def _add_custom_menu(self):
    """Agrega un menú contextual personalizado"""
    key_path = r"Directory\shell\IPM_CustomAction"
    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path) as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "Mi Acción Personalizada")
        winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, self.icon_path)
    
    cmd_path = key_path + r"\command"
    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, cmd_path) as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'"{self.exe_path}" --custom-action "%1"')
```

Luego llama este método en `install_context_menus()`:

```python
def install_context_menus(self):
    try:
        self._add_folder_context_menu()
        self._add_iflapp_context_menu()
        self._add_background_context_menu()
        self._add_custom_menu()  # Agregar aquí
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
```

## Agregar Nuevos Comandos CLI

Para agregar un nuevo comando CLI, edita `cli_handler.py`:

```python
# En _setup_arguments():
self.parser.add_argument(
    '--custom-action',
    metavar='PATH',
    help='Ejecuta una acción personalizada'
)

# En get_action():
elif args.custom_action:
    return ('custom_action', args.custom_action)
```

Luego agrega el manejador en `handle_cli_action()`:

```python
elif action == 'custom_action':
    if data:
        window.show_custom_action_dialog(data)
```

Y finalmente agrega el método en `PackageTodoGUI`:

```python
def show_custom_action_dialog(self, path):
    """Muestra diálogo para acción personalizada"""
    QMessageBox.information(
        self,
        "Acción Personalizada",
        f"Ejecutando acción personalizada en:\n{path}"
    )
```

## Personalizar Archivos .mexf

Crea tu propio archivo .mexf personalizado:

```json
{
    "version": "1.0",
    "app_name": "Mi Aplicación Personalizada",
    "app_id": "com.miempresa.miapp",
    "extensions": [
        {
            "extension": ".miext",
            "description": "Mi Extensión Personalizada",
            "icon": "ruta/a/mi/icono.ico",
            "mime_type": "application/x-miext"
        }
    ],
    "context_menus": [
        {
            "target": "file",
            "extensions": [".miext"],
            "label": "Abrir con Mi App",
            "command": "miapp.exe \"%1\"",
            "icon": "ruta/a/mi/icono.ico"
        },
        {
            "target": "folder",
            "label": "Procesar con Mi App",
            "command": "miapp.exe --process \"%1\"",
            "icon": "ruta/a/mi/icono.ico"
        }
    ]
}
```

## Modificar Estilos de Botones

Los estilos están definidos en `gui_helpers.py`. Puedes modificarlos:

```python
BTN_STYLES = {
    "custom": "background-color: #your-color; color: white; border-radius: 9px; padding: 10px 20px;",
}
```

## Testing Personalizado

Agrega tus propios tests en `test_shell_integration.py`:

```python
class TestCustomFeature(unittest.TestCase):
    def test_custom_functionality(self):
        # Tu código de test aquí
        self.assertTrue(True)
```

## Conclusión

Todos los componentes son personalizables. Consulta los archivos fuente para más detalles.
