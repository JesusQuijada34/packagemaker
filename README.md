# Influent Package Maker

![IPM Banner](https://raw.githubusercontent.com/jesusquijada34/packagemaker/main/app/app-icon.ico)

## Suite Todo en Uno para Creación y Gestión de Paquetes (PyQt5 GUI)

**Influent Package Maker** es una herramienta gráfica moderna desarrollada en **Python 3** y **PyQt5**, pensada para crear, empaquetar, instalar y administrar proyectos tipo *Influent Flarm Apps* con extensión `.iflapp` en Windows y Linux, incluyendo soporte multiplataforma.

---

## 🚀 Características principales

- **Estructura automática de proyectos** con carpetas (`app`, `assets`, `config`, `docs`, `source`, `lib`)
- **Verificación online de usuario GitHub** para mayor autenticidad del autor
- **Empaquetado y construcción de archivos `.iflapp`** listos para distribución
- **Gestión visual de proyectos y apps instaladas**
- **Instalación/Desinstalación de apps en un clic**
- **Ejecución directa de scripts Python desde la GUI**
- **Protección SHA256**: cada proyecto tiene su propio hash único
- **Generación de accesos directos (solo Windows)**
- **Tema oscuro adaptable al sistema, con acentos naranjas**
- **Multiplataforma**: Windows, Linux y modo multiplataforma

---

## 🖥️ Estructura generada por defecto

```
.
├── app/
│   └── app-icon.ico
├── assets/
├── config/
├── docs/
├── source/
├── lib/
│   └── requirements.txt
├── LICENSE
├── autorun.bat              # Lanzador para Windows
├── autorun                  # Lanzador bash para Linux
├── details.xml              # Metadatos del paquete
├── manifest.res             # Manifest de Windows
├── version.res              # Recursos de versión
├── .storedetail             # Hash de protección único (SHA256)
├── README.md
└── <tu_aplicacion>.py
```

---

## 📦 Ejemplo de uso

Para ejecutar el script principal de un proyecto generado:

```bash
python3 <empresa>.<nombre>.v<version>/<nombre>.py
```

O, utilizando el lanzador según tu SO (debes tener Python 3 instalado):

- **Windows**:
    ```cmd
    cd <carpeta_del_proyecto>
    autorun.bat
    ```
- **Linux**:
    ```bash
    cd <carpeta_del_proyecto>
    ./autorun
    ```

---

## ⚙️ Requisitos técnicos

- **Python 3.7+**
- **PyQt5**
- (Opcional para integración de accesos directos Windows): `pywin32`
- Internet para validar usuario GitHub (opcional; permite skip si estás offline)

Dependencias necesarias para la app:

```bash
pip install PyQt5
```

---

## 🛠 ¿Cómo se instala IPM?

1. Clona este repositorio:
    ```bash
    git clone https://github.com/jesusquijada34/packagemaker.git
    cd packagemaker
    ```
2. Instala dependencias:
    ```bash
    pip install -r lib/requirements.txt
    # Si tu entorno no tiene requirements.txt, basta con: pip install PyQt5
    ```
3. Ejecuta el programa:
    ```bash
    python packagemaker.py/.exe/.elf
    ```
4. ¡Listo! Usa su interfaz amigable para crear, empaquetar y distribuir tus apps.

---

## 🔐 Licencia

Este proyecto está licenciado bajo la **GNU General Public License v3.0 (GPLv3)**.  
Consulta el archivo LICENSE para más información.

---

## 📢 Créditos y contacto

- **Principal:** [Jesus Quijada](https://t.me/JesusQuijada34) ([@JesusQuijada34](https://github.com/JesusQuijada34))
- **Colaborador:** [MkelCT](https://t.me/MkelCT)

**Telegram:** [@JesusQuijada34](https://t.me/JesusQuijada34)  
**Repo:** [github.com/jesusquijada34/packagemaker](https://github.com/jesusquijada34/packagemaker)

---

## 📝 Notas

- El sistema genera README y LICENSE automáticamente en cada proyecto.
- Cada paquete incluye su propio **details.xml** con metadatos para futuros stores.
- El gestor de proyectos permite instalar y desinstalar de manera segura.
- Cada proyecto/app puede contener scripts Python múltiples y su metadata asociada.


<div align="center" style="color:#888; margin-top:32px">
  <sub>Hecho con ❤️ usando PyQt5 • Influent OS • 2025.<br>
  Bajo licencia GPL v3.</sub>
</div>
