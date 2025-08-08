#!/usr/bin/env/python
# -*- coding: utf-8 -*-
import sys
import os
import time
import hashlib
import shutil
import zipfile
import xml.etree.ElementTree as ET
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QListWidget, QListWidgetItem, QFileDialog, QDialog, QStyle, QSizePolicy, QSplitter, QGroupBox
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# ----------- CONFIGURABLE VARIABLES -----------
APP_FONT = QFont('Arial', 11)
TAB_FONT = QFont('Arial', 12, QFont.Bold)
BUTTON_FONT = QFont('Arial', 11, QFont.Bold)
TAB_ICONS = {
    "crear": "app/package_add.ico",
    "construir": "app/package_build.ico",
    "gestor": "app/package_fm.ico",
    "about": "app/package_about.ico",
    "instalar": "app/package_install.ico",
    "desinstalar": "app/package_uninstall.ico",
}
BTN_STYLES = {
    "default": "background-color: #29b6f6;color: #000000;border-radius:5px;padding:10px 18px;font-weight:bold;border: 1px solid #45addc;",
    "success": "background-color: #43a047;color: #000000;border-radius:5px;padding:10px 18px;font-weight:bold;border: 1px solid #22863a;",
    "danger":  "background-color: #c62828;color: #000000;border-radius:5px;padding:10px 18px;font-weight:bold;border: 1px solid #B52222;",
    "warning": "background-color: #ffd54f;color: #212121;border-radius:5px;padding:10px 18px;font-weight:bold;border: 1px solid #E6BD3A;",
    "info":    "background-color: #5c6bc0;color: #000000;border-radius:5px;padding:10px 18px;font-weight:bold;border: 1px solid #3A4DB9;",
}
plataforma_platform = sys.platform
plataforma_name = os.name
if plataforma_platform.startswith("win"):
    BASE_DIR = os.path.join(os.environ["USERPROFILE"], "My Documents", "Influent Packages")
    FLATR_APPS = os.path.join(os.environ["USERPROFILE"], "My Documents", "Flatr Apps")
elif plataforma_platform.startswith("linux"):
    BASE_DIR = os.path.expanduser("~/Documentos/Influent Packages")
    FLATR_APPS = os.path.expanduser("~/Documentos/Flatr Apps")
else:
    BASE_DIR = "Influent Packages/"
    FLATR_APPS = "Flatr Apps/"

IPM_ICON_PATH = "app/app-icon.ico"
DEFAULT_FOLDERS = "app,assets,config,docs,source,lib"

plataforma = plataforma_platform.capitalize()
nombre = plataforma_name.capitalize()
plataforma = f"{plataforma} in {nombre}"

LGDR_MAKE_MESSAGES = {
    "_LGDR_PUBLISHER_E" : "Nombre del fabricante de creación. En blanco, Influent",
    "_LGDR_NAME_E" : "Nombre acortado del proyecto. Se permiten guiones y pisos, no espacios. En blanco, mycoolapp",
    "_LGDR_VERSION_E" :"Versión del proyecto, como 1 o 1.0, no es permitido guiones ni espacios. En blanco, 1",
    "_LGDR_TITLE_E" : "Título del proyecto, formato libre. En blanco, My Cool App",
    "_LGDR_MAKE_BTN" : "Crear proyecto y firmar"
}
LGDR_BUILD_MESSAGES = {
    "_LGDR_PUBLISHER_E" : "Nombre del publicador quien hizo el proyecto",
    "_LGDR_NAME_E" : "Nombre corto del proyecto a construir",
    "_LGDR_VERSION_E" : "Versión del proyecto a detectar",
    "_LGDR_TYPE_DDL" : "Packaged (Programa multiplataforma sin código)\nBundled (Script Python con dependencias necesarias",
    "_LGDR_BUILD_BTN" : "Construir a partir de RAW (Flatr Packaged/Bundled)"
}

LGDR_NAUFRAGIO_MESSAGES = {
    "_LGDR_LOCAL_LV" : "Proyectos locales encontrados en la carpeta predeterminada",
    "_LGDR_INSTALLED_LV" : "Paquetes instalados desde la RAW (Flatr Packaged/Bundled)",
    "_LGDR_REFRESH_BTN" : "Refresca proyectos locales y paquetes instalados",
    "_LGDR_INSTALL_BTN" : "Instala un paquete Flatr desde ruta",
    "_LGDR_UNINSTALL_BTN" : "Desinstala un paquete Flatr instalado en el directorio de la tienda",
    "_LGDR_RUNPY_BTN" : "Ejecuta o depura el bundle/py seleccionado",
    "_LGDR_INSTALLPROJ_BTN" : "Instala la carpeta del proyecto si se encuentra compilado",
    "_LGDR_UNINSTALLPROJ_BTN" : "Elimina definitivamente el proyecto desde el alamacenamiento",
    "_LGDR_RUNPYAPP_BTN" : "Ejecuta el bundle instalado",
    "_LGDR_UNINSTALLAPP_BTN" : "Desinstala definitivamente el Flatr Seleccionado",
}
AGE_RATINGS = {
    "adult" or "sex" or "sexual": "ADULTS ONLY",
    "social" or "violence" or "horror" or "obscene" or "boyfriend" or "girlfriend" or "teen" or "shoot" or "shooter" or "minecraft" or "drift" or "car" or "craft" or "dating" or "porn" or "pornhub" or "onlyfans" or "xnxx" or "porno" or "porngraphic" or "restricted" or "simulator": "TEENS ALL 18+",
    "kids" or "kid" or "learn" or "learner" or "gameto" or "abc" or "animated" or "makeup" or "girls" or "boys" or "puzzle": "FOR KIDS",
    "camera" or "calculator" or "game" or "games" or "public": "EVERYONE",
    "music" or "video" or "photo" or "document": "PERSONAL USE",
    "facebook" or "tiktok" or "whatsapp" or "telegram" or "snapchat" or "pinterest" or "x" or "twitter" or "youtube" or "likee" or "netflix" or "primevideo" or "cinema" or "ytmusic" or "browser" or "ads" or "discord" or "github" or "drive" or "mega" or "mediafire" or "yandex" or "opera" or "operamini" or "brave" or "chrome" or "googlechorme" or "chromebrowser" or "mozilla" or "firefox" or "tor" or "torbrowser" or "lightbrowser" or "edge" or "edgebrowser" or "internet" or "internetexplorer" or "ie" or "ie7" or "ie8" or "ie9" or "bing" or "duckduckgo" or "instagram" or "flickr" or "social" : "PUBLIC CONTENT",
    "ai" or "ia" or "chatgpt" or "copilot" or "deepseek" or "claude" or "gemini" or "mistral" or "leo" or "gabo" or "zapia" or "sonnet" or "plikaai" or "plika" or "klingai" or "kling" : "PUBLIC ALL",
    
}

def getversion():
    newversion = time.strftime("%y.%m-%H.%M")
    return f"{newversion}"

class BuildThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    def __init__(self, empresa, nombre, version, tipo, parent=None):
        super().__init__(parent)
        self.empresa = empresa
        self.nombre = nombre
        self.version = version
        self.tipo = tipo
    def run(self):
        folder = f"{self.empresa}.{self.nombre}.v{self.version}"
        path = os.path.join(BASE_DIR, folder)
        ext = ".iflapp" if self.tipo == "1" else ".iflappb"
        output_file = os.path.join(BASE_DIR, folder + ext)
        zip_path = output_file.replace(ext, "") + ".zip"
        if not os.path.exists(path):
            self.error.emit("No se encontró la carpeta del paquete.")
            return
        try:
            file_list = []
            for root, _, files in os.walk(path):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, path)
                    file_list.append((full_path, arcname))
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for i, (full_path, arcname) in enumerate(file_list):
                    zipf.write(full_path, arcname)
                    self.progress.emit(f"Empaquetando archivo {i+1}/{len(file_list)}: {arcname}")
            os.rename(zip_path, output_file)
            self.finished.emit(f"Paquete construido: {output_file}")
        except Exception as e:
            self.error.emit(str(e))

class PackageTodoGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Influent Package Maker for {plataforma} | QT5 Edition")
        self.resize(1200, 750)
        self.setFont(APP_FONT)
        self.setWindowIcon(QtGui.QIcon(IPM_ICON_PATH if os.path.exists(IPM_ICON_PATH) else ""))
        self.statusBar().showMessage("Preparado")
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QVBoxLayout(self.central)
        self.tabs = QTabWidget()
        self.tabs.setFont(TAB_FONT)
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(True)
        self.layout.addWidget(self.tabs)
        self.init_tabs()
        self.setMinimumSize(700, 500)
        self.setStyleSheet("""
            QMainWindow { background: #f8fafc; }
            QTabWidget::pane { border: 0; }
            QTabBar::tab:selected { background: #e3f2fd; }
            QLabel { font-size: 15px; }
            QListWidget { background: #f2f2f2; font-size: 12px; border-radius: 5px;}
        """)

    def init_tabs(self):
        self.tab_create = QWidget()
        self.tabs.addTab(self.tab_create, QIcon(TAB_ICONS["crear"]), "Crear Proyecto")
        self.init_create_tab()
        self.tab_build = QWidget()
        self.tabs.addTab(self.tab_build, QIcon(TAB_ICONS["construir"]), "Construir Paquete")
        self.init_build_tab()
        self.tab_manager = QWidget()
        self.tabs.addTab(self.tab_manager, QIcon(TAB_ICONS["gestor"]), "Gestor de Proyectos")
        self.init_manager_tab()
        self.tab_about = QWidget()
        self.tabs.addTab(self.tab_about, QIcon(TAB_ICONS["about"]), "Acerca de")
        self.init_about_tab()

    def init_create_tab(self):
        layout = QVBoxLayout()
        form_group = QGroupBox("Datos del Proyecto")
        form_layout = QVBoxLayout(form_group)
        self.input_empresa = QLineEdit()
        self.input_empresa.setPlaceholderText("Ejemplo: influent")
        self.input_empresa.setToolTip(LGDR_MAKE_MESSAGES["_LGDR_PUBLISHER_E"])
        form_layout.addWidget(QLabel("Fabricante:"))
        form_layout.addWidget(self.input_empresa)
        self.input_nombre_logico = QLineEdit()
        self.input_nombre_logico.setPlaceholderText("Ejemplo: mycoolapp")
        self.input_nombre_logico.setToolTip(LGDR_MAKE_MESSAGES["_LGDR_NAME_E"])
        form_layout.addWidget(QLabel("Nombre interno:"))
        form_layout.addWidget(self.input_nombre_logico)
        self.input_version = QLineEdit()
        self.input_version.setPlaceholderText("Ejemplo: 1.0")
        self.input_version.setToolTip(LGDR_MAKE_MESSAGES["_LGDR_VERSION_E"])
        form_layout.addWidget(QLabel("Versión:"))
        form_layout.addWidget(self.input_version)
        self.input_titulo = QLineEdit()
        self.input_titulo.setPlaceholderText("Ejemplo: MyCoolApp")
        self.input_titulo.setToolTip(LGDR_MAKE_MESSAGES["_LGDR_TITLE_E"])
        form_layout.addWidget(QLabel("Título completo:"))
        form_layout.addWidget(self.input_titulo)
        self.btn_create = QPushButton("Crear Proyecto")
        self.btn_create.setFont(BUTTON_FONT)
        self.btn_create.setStyleSheet(BTN_STYLES["success"])
        self.btn_create.setToolTip(LGDR_MAKE_MESSAGES["_LGDR_MAKE_BTN"])
        self.btn_create.setIcon(QIcon(TAB_ICONS["crear"]))
        self.btn_create.clicked.connect(self.create_package_action)
        self.create_status = QLabel("")
        self.create_status.setStyleSheet("color:#388e3c;")
        layout.addWidget(form_group)
        layout.addWidget(self.btn_create)
        layout.addWidget(self.create_status)
        self.tab_create.setLayout(layout)

    def create_package_action(self):
        empresa = self.input_empresa.text().strip().lower().replace(" ", "-") or "influent"
        nombre_logico = self.input_nombre_logico.text().strip().lower() or "mycoolapp"
        version = self.input_version.text().strip()
        if version == "":
             f"1-{getversion()}-danenone"
        else:
            version = f"{version}-{getversion()}-danenone"
        nombre_completo = self.input_titulo.text() or nombre_logico.strip().upper()
        folder_name = f"{empresa}.{nombre_logico}.v{version}"
        full_path = os.path.join(BASE_DIR, folder_name)
        try:
            for folder in DEFAULT_FOLDERS.split(","):
                os.makedirs(os.path.join(full_path, folder.strip()), exist_ok=True)
            main_script = os.path.join(full_path, f"{nombre_logico}.py")
            cmdwin = os.path.join(full_path, "autorun.bat")
            bashlinux = os.path.join(full_path, "autorun")
            lic = os.path.join(full_path, "LICENSE")
            fn = f"{empresa}.{nombre_logico}.v{version}"
            hv = hashlib.sha256(fn.encode()).hexdigest()
            storekey = os.path.join(full_path, ".storedetail")
            for folder in DEFAULT_FOLDERS.split(","):
                here_file = os.path.join(full_path, folder, f".{folder}-container")
                with open(here_file, "w") as f:
                    resultinityy = os.path.join(f"#store (sha256 hash):{folder}/.{hv}")
                    f.write(resultinityy)
            with open(storekey, "w") as f:
                f.write(f"#aiFlatr Store APP DETAIL | Correlation Engine for Influent OS\n#store key protection id:\n{hv}")
            with open(lic, "w") as f:
                f.write(f"""                   GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

                            Preamble

  The GNU General Public License is a free, copyleft license for
software and other kinds of works.

  The licenses for most software and other practical works are designed
to take away your freedom to share and change the works.  By contrast,
the GNU General Public License is intended to guarantee your freedom to
share and change all versions of a program--to make sure it remains free
software for all its users.  We, the Free Software Foundation, use the
GNU General Public License for most of our software; it applies also to
any other work released this way by its authors.  You can apply it to
your programs, too.

  When we speak of free software, we are referring to freedom, not
price.  Our General Public Licenses are designed to make sure that you
have the freedom to distribute copies of free software (and charge for
them if you wish), that you receive source code or can get it if you
want it, that you can change the software or use pieces of it in new
free programs, and that you know you can do these things.

  To protect your rights, we need to prevent others from denying you
these rights or asking you to surrender the rights.  Therefore, you have
certain responsibilities if you distribute copies of the software, or if
you modify it: responsibilities to respect the freedom of others.

  For example, if you distribute copies of such a program, whether
gratis or for a fee, you must pass on to the recipients the same
freedoms that you received.  You must make sure that they, too, receive
or can get the source code.  And you must show them these terms so they
know their rights.

  Developers that use the GNU GPL protect your rights with two steps:
(1) assert copyright on the software, and (2) offer you this License
giving you legal permission to copy, distribute and/or modify it.

  For the developers' and authors' protection, the GPL clearly explains
that there is no warranty for this free software.  For both users' and
authors' sake, the GPL requires that modified versions be marked as
changed, so that their problems will not be attributed erroneously to
authors of previous versions.

  Some devices are designed to deny users access to install or run
modified versions of the software inside them, although the manufacturer
can do so.  This is fundamentally incompatible with the aim of
protecting users' freedom to change the software.  The systematic
pattern of such abuse occurs in the area of products for individuals to
use, which is precisely where it is most unacceptable.  Therefore, we
have designed this version of the GPL to prohibit the practice for those
products.  If such problems arise substantially in other domains, we
stand ready to extend this provision to those domains in future versions
of the GPL, as needed to protect the freedom of users.

  Finally, every program is threatened constantly by software patents.
States should not allow patents to restrict development and use of
software on general-purpose computers, but in those that do, we wish to
avoid the special danger that patents applied to a free program could
make it effectively proprietary.  To prevent this, the GPL assures that
patents cannot be used to render the program non-free.

  The precise terms and conditions for copying, distribution and
modification follow.

                       TERMS AND CONDITIONS

  0. Definitions.

  "This License" refers to version 3 of the GNU General Public License.

  "Copyright" also means copyright-like laws that apply to other kinds of
works, such as semiconductor masks.

  "The Program" refers to any copyrightable work licensed under this
License.  Each licensee is addressed as "you".  "Licensees" and
"recipients" may be individuals or organizations.

  To "modify" a work means to copy from or adapt all or part of the work
in a fashion requiring copyright permission, other than the making of an
exact copy.  The resulting work is called a "modified version" of the
earlier work or a work "based on" the earlier work.

  A "covered work" means either the unmodified Program or a work based
on the Program.

  To "propagate" a work means to do anything with it that, without
permission, would make you directly or secondarily liable for
infringement under applicable copyright law, except executing it on a
computer or modifying a private copy.  Propagation includes copying,
distribution (with or without modification), making available to the
public, and in some countries other activities as well.

  To "convey" a work means any kind of propagation that enables other
parties to make or receive copies.  Mere interaction with a user through
a computer network, with no transfer of a copy, is not conveying.

  An interactive user interface displays "Appropriate Legal Notices"
to the extent that it includes a convenient and prominently visible
feature that (1) displays an appropriate copyright notice, and (2)
tells the user that there is no warranty for the work (except to the
extent that warranties are provided), that licensees may convey the
work under this License, and how to view a copy of this License.  If
the interface presents a list of user commands or options, such as a
menu, a prominent item in the list meets this criterion.

  1. Source Code.

  The "source code" for a work means the preferred form of the work
for making modifications to it.  "Object code" means any non-source
form of a work.

  A "Standard Interface" means an interface that either is an official
standard defined by a recognized standards body, or, in the case of
interfaces specified for a particular programming language, one that
is widely used among developers working in that language.

  The "System Libraries" of an executable work include anything, other
than the work as a whole, that (a) is included in the normal form of
packaging a Major Component, but which is not part of that Major
Component, and (b) serves only to enable use of the work with that
Major Component, or to implement a Standard Interface for which an
implementation is available to the public in source code form.  A
"Major Component", in this context, means a major essential component
(kernel, window system, and so on) of the specific operating system
(if any) on which the executable work runs, or a compiler used to
produce the work, or an object code interpreter used to run it.

  The "Corresponding Source" for a work in object code form means all
the source code needed to generate, install, and (for an executable
work) run the object code and to modify the work, including scripts to
control those activities.  However, it does not include the work's
System Libraries, or general-purpose tools or generally available free
programs which are used unmodified in performing those activities but
which are not part of the work.  For example, Corresponding Source
includes interface definition files associated with source files for
the work, and the source code for shared libraries and dynamically
linked subprograms that the work is specifically designed to require,
such as by intimate data communication or control flow between those
subprograms and other parts of the work.

  The Corresponding Source need not include anything that users
can regenerate automatically from other parts of the Corresponding
Source.

  The Corresponding Source for a work in source code form is that
same work.

  2. Basic Permissions.

  All rights granted under this License are granted for the term of
copyright on the Program, and are irrevocable provided the stated
conditions are met.  This License explicitly affirms your unlimited
permission to run the unmodified Program.  The output from running a
covered work is covered by this License only if the output, given its
content, constitutes a covered work.  This License acknowledges your
rights of fair use or other equivalent, as provided by copyright law.

  You may make, run and propagate covered works that you do not
convey, without conditions so long as your license otherwise remains
in force.  You may convey covered works to others for the sole purpose
of having them make modifications exclusively for you, or provide you
with facilities for running those works, provided that you comply with
the terms of this License in conveying all material for which you do
not control copyright.  Those thus making or running the covered works
for you must do so exclusively on your behalf, under your direction
and control, on terms that prohibit them from making any copies of
your copyrighted material outside their relationship with you.

  Conveying under any other circumstances is permitted solely under
the conditions stated below.  Sublicensing is not allowed; section 10
makes it unnecessary.

  3. Protecting Users' Legal Rights From Anti-Circumvention Law.

  No covered work shall be deemed part of an effective technological
measure under any applicable law fulfilling obligations under article
11 of the WIPO copyright treaty adopted on 20 December 1996, or
similar laws prohibiting or restricting circumvention of such
measures.

  When you convey a covered work, you waive any legal power to forbid
circumvention of technological measures to the extent such circumvention
is effected by exercising rights under this License with respect to
the covered work, and you disclaim any intention to limit operation or
modification of the work as a means of enforcing, against the work's
users, your or third parties' legal rights to forbid circumvention of
technological measures.

  4. Conveying Verbatim Copies.

  You may convey verbatim copies of the Program's source code as you
receive it, in any medium, provided that you conspicuously and
appropriately publish on each copy an appropriate copyright notice;
keep intact all notices stating that this License and any
non-permissive terms added in accord with section 7 apply to the code;
keep intact all notices of the absence of any warranty; and give all
recipients a copy of this License along with the Program.

  You may charge any price or no price for each copy that you convey,
and you may offer support or warranty protection for a fee.

  5. Conveying Modified Source Versions.

  You may convey a work based on the Program, or the modifications to
produce it from the Program, in the form of source code under the
terms of section 4, provided that you also meet all of these conditions:

    a) The work must carry prominent notices stating that you modified
    it, and giving a relevant date.

    b) The work must carry prominent notices stating that it is
    released under this License and any conditions added under section
    7.  This requirement modifies the requirement in section 4 to
    "keep intact all notices".

    c) You must license the entire work, as a whole, under this
    License to anyone who comes into possession of a copy.  This
    License will therefore apply, along with any applicable section 7
    additional terms, to the whole of the work, and all its parts,
    regardless of how they are packaged.  This License gives no
    permission to license the work in any other way, but it does not
    invalidate such permission if you have separately received it.

    d) If the work has interactive user interfaces, each must display
    Appropriate Legal Notices; however, if the Program has interactive
    interfaces that do not display Appropriate Legal Notices, your
    work need not make them do so.

  A compilation of a covered work with other separate and independent
works, which are not by their nature extensions of the covered work,
and which are not combined with it such as to form a larger program,
in or on a volume of a storage or distribution medium, is called an
"aggregate" if the compilation and its resulting copyright are not
used to limit the access or legal rights of the compilation's users
beyond what the individual works permit.  Inclusion of a covered work
in an aggregate does not cause this License to apply to the other
parts of the aggregate.

  6. Conveying Non-Source Forms.

  You may convey a covered work in object code form under the terms
of sections 4 and 5, provided that you also convey the
machine-readable Corresponding Source under the terms of this License,
in one of these ways:

    a) Convey the object code in, or embodied in, a physical product
    (including a physical distribution medium), accompanied by the
    Corresponding Source fixed on a durable physical medium
    customarily used for software interchange.

    b) Convey the object code in, or embodied in, a physical product
    (including a physical distribution medium), accompanied by a
    written offer, valid for at least three years and valid for as
    long as you offer spare parts or customer support for that product
    model, to give anyone who possesses the object code either (1) a
    copy of the Corresponding Source for all the software in the
    product that is covered by this License, on a durable physical
    medium customarily used for software interchange, for a price no
    more than your reasonable cost of physically performing this
    conveying of source, or (2) access to copy the
    Corresponding Source from a network server at no charge.

    c) Convey individual copies of the object code with a copy of the
    written offer to provide the Corresponding Source.  This
    alternative is allowed only occasionally and noncommercially, and
    only if you received the object code with such an offer, in accord
    with subsection 6b.

    d) Convey the object code by offering access from a designated
    place (gratis or for a charge), and offer equivalent access to the
    Corresponding Source in the same way through the same place at no
    further charge.  You need not require recipients to copy the
    Corresponding Source along with the object code.  If the place to
    copy the object code is a network server, the Corresponding Source
    may be on a different server (operated by you or a third party)
    that supports equivalent copying facilities, provided you maintain
    clear directions next to the object code saying where to find the
    Corresponding Source.  Regardless of what server hosts the
    Corresponding Source, you remain obligated to ensure that it is
    available for as long as needed to satisfy these requirements.

    e) Convey the object code using peer-to-peer transmission, provided
    you inform other peers where the object code and Corresponding
    Source of the work are being offered to the general public at no
    charge under subsection 6d.

  A separable portion of the object code, whose source code is excluded
from the Corresponding Source as a System Library, need not be
included in conveying the object code work.

  A "User Product" is either (1) a "consumer product", which means any
tangible personal property which is normally used for personal, family,
or household purposes, or (2) anything designed or sold for incorporation
into a dwelling.  In determining whether a product is a consumer product,
doubtful cases shall be resolved in favor of coverage.  For a particular
product received by a particular user, "normally used" refers to a
typical or common use of that class of product, regardless of the status
of the particular user or of the way in which the particular user
actually uses, or expects or is expected to use, the product.  A product
is a consumer product regardless of whether the product has substantial
commercial, industrial or non-consumer uses, unless such uses represent
the only significant mode of use of the product.

  "Installation Information" for a User Product means any methods,
procedures, authorization keys, or other information required to install
and execute modified versions of a covered work in that User Product from
a modified version of its Corresponding Source.  The information must
suffice to ensure that the continued functioning of the modified object
code is in no case prevented or interfered with solely because
modification has been made.

  If you convey an object code work under this section in, or with, or
specifically for use in, a User Product, and the conveying occurs as
part of a transaction in which the right of possession and use of the
User Product is transferred to the recipient in perpetuity or for a
fixed term (regardless of how the transaction is characterized), the
Corresponding Source conveyed under this section must be accompanied
by the Installation Information.  But this requirement does not apply
if neither you nor any third party retains the ability to install
modified object code on the User Product (for example, the work has
been installed in ROM).

  The requirement to provide Installation Information does not include a
requirement to continue to provide support service, warranty, or updates
for a work that has been modified or installed by the recipient, or for
the User Product in which it has been modified or installed.  Access to a
network may be denied when the modification itself materially and
adversely affects the operation of the network or violates the rules and
protocols for communication across the network.

  Corresponding Source conveyed, and Installation Information provided,
in accord with this section must be in a format that is publicly
documented (and with an implementation available to the public in
source code form), and must require no special password or key for
unpacking, reading or copying.

  7. Additional Terms.

  "Additional permissions" are terms that supplement the terms of this
License by making exceptions from one or more of its conditions.
Additional permissions that are applicable to the entire Program shall
be treated as though they were included in this License, to the extent
that they are valid under applicable law.  If additional permissions
apply only to part of the Program, that part may be used separately
under those permissions, but the entire Program remains governed by
this License without regard to the additional permissions.

  When you convey a copy of a covered work, you may at your option
remove any additional permissions from that copy, or from any part of
it.  (Additional permissions may be written to require their own
removal in certain cases when you modify the work.)  You may place
additional permissions on material, added by you to a covered work,
for which you have or can give appropriate copyright permission.

  Notwithstanding any other provision of this License, for material you
add to a covered work, you may (if authorized by the copyright holders of
that material) supplement the terms of this License with terms:

    a) Disclaiming warranty or limiting liability differently from the
    terms of sections 15 and 16 of this License; or

    b) Requiring preservation of specified reasonable legal notices or
    author attributions in that material or in the Appropriate Legal
    Notices displayed by works containing it; or

    c) Prohibiting misrepresentation of the origin of that material, or
    requiring that modified versions of such material be marked in
    reasonable ways as different from the original version; or

    d) Limiting the use for publicity purposes of names of licensors or
    authors of the material; or

    e) Declining to grant rights under trademark law for use of some
    trade names, trademarks, or service marks; or

    f) Requiring indemnification of licensors and authors of that
    material by anyone who conveys the material (or modified versions of
    it) with contractual assumptions of liability to the recipient, for
    any liability that these contractual assumptions directly impose on
    those licensors and authors.

  All other non-permissive additional terms are considered "further
restrictions" within the meaning of section 10.  If the Program as you
received it, or any part of it, contains a notice stating that it is
governed by this License along with a term that is a further
restriction, you may remove that term.  If a license document contains
a further restriction but permits relicensing or conveying under this
License, you may add to a covered work material governed by the terms
of that license document, provided that the further restriction does
not survive such relicensing or conveying.

  If you add terms to a covered work in accord with this section, you
must place, in the relevant source files, a statement of the
additional terms that apply to those files, or a notice indicating
where to find the applicable terms.

  Additional terms, permissive or non-permissive, may be stated in the
form of a separately written license, or stated as exceptions;
the above requirements apply either way.

  8. Termination.

  You may not propagate or modify a covered work except as expressly
provided under this License.  Any attempt otherwise to propagate or
modify it is void, and will automatically terminate your rights under
this License (including any patent licenses granted under the third
paragraph of section 11).

  However, if you cease all violation of this License, then your
license from a particular copyright holder is reinstated (a)
provisionally, unless and until the copyright holder explicitly and
finally terminates your license, and (b) permanently, if the copyright
holder fails to notify you of the violation by some reasonable means
prior to 60 days after the cessation.

  Moreover, your license from a particular copyright holder is
reinstated permanently if the copyright holder notifies you of the
violation by some reasonable means, this is the first time you have
received notice of violation of this License (for any work) from that
copyright holder, and you cure the violation prior to 30 days after
your receipt of the notice.

  Termination of your rights under this section does not terminate the
licenses of parties who have received copies or rights from you under
this License.  If your rights have been terminated and not permanently
reinstated, you do not qualify to receive new licenses for the same
material under section 10.

  9. Acceptance Not Required for Having Copies.

  You are not required to accept this License in order to receive or
run a copy of the Program.  Ancillary propagation of a covered work
occurring solely as a consequence of using peer-to-peer transmission
to receive a copy likewise does not require acceptance.  However,
nothing other than this License grants you permission to propagate or
modify any covered work.  These actions infringe copyright if you do
not accept this License.  Therefore, by modifying or propagating a
covered work, you indicate your acceptance of this License to do so.

  10. Automatic Licensing of Downstream Recipients.

  Each time you convey a covered work, the recipient automatically
receives a license from the original licensors, to run, modify and
propagate that work, subject to this License.  You are not responsible
for enforcing compliance by third parties with this License.

  An "entity transaction" is a transaction transferring control of an
organization, or substantially all assets of one, or subdividing an
organization, or merging organizations.  If propagation of a covered
work results from an entity transaction, each party to that
transaction who receives a copy of the work also receives whatever
licenses to the work the party's predecessor in interest had or could
give under the previous paragraph, plus a right to possession of the
Corresponding Source of the work from the predecessor in interest, if
the predecessor has it or can get it with reasonable efforts.

  You may not impose any further restrictions on the exercise of the
rights granted or affirmed under this License.  For example, you may
not impose a license fee, royalty, or other charge for exercise of
rights granted under this License, and you may not initiate litigation
(including a cross-claim or counterclaim in a lawsuit) alleging that
any patent claim is infringed by making, using, selling, offering for
sale, or importing the Program or any portion of it.

  11. Patents.

  A "contributor" is a copyright holder who authorizes use under this
License of the Program or a work on which the Program is based.  The
work thus licensed is called the contributor's "contributor version".

  A contributor's "essential patent claims" are all patent claims
owned or controlled by the contributor, whether already acquired or
hereafter acquired, that would be infringed by some manner, permitted
by this License, of making, using, or selling its contributor version,
but do not include claims that would be infringed only as a
consequence of further modification of the contributor version.  For
purposes of this definition, "control" includes the right to grant
patent sublicenses in a manner consistent with the requirements of
this License.

  Each contributor grants you a non-exclusive, worldwide, royalty-free
patent license under the contributor's essential patent claims, to
make, use, sell, offer for sale, import and otherwise run, modify and
propagate the contents of its contributor version.

  In the following three paragraphs, a "patent license" is any express
agreement or commitment, however denominated, not to enforce a patent
(such as an express permission to practice a patent or covenant not to
sue for patent infringement).  To "grant" such a patent license to a
party means to make such an agreement or commitment not to enforce a
patent against the party.

  If you convey a covered work, knowingly relying on a patent license,
and the Corresponding Source of the work is not available for anyone
to copy, free of charge and under the terms of this License, through a
publicly available network server or other readily accessible means,
then you must either (1) cause the Corresponding Source to be so
available, or (2) arrange to deprive yourself of the benefit of the
patent license for this particular work, or (3) arrange, in a manner
consistent with the requirements of this License, to extend the patent
license to downstream recipients.  "Knowingly relying" means you have
actual knowledge that, but for the patent license, your conveying the
covered work in a country, or your recipient's use of the covered work
in a country, would infringe one or more identifiable patents in that
country that you have reason to believe are valid.

  If, pursuant to or in connection with a single transaction or
arrangement, you convey, or propagate by procuring conveyance of, a
covered work, and grant a patent license to some of the parties
receiving the covered work authorizing them to use, propagate, modify
or convey a specific copy of the covered work, then the patent license
you grant is automatically extended to all recipients of the covered
work and works based on it.

  A patent license is "discriminatory" if it does not include within
the scope of its coverage, prohibits the exercise of, or is
conditioned on the non-exercise of one or more of the rights that are
specifically granted under this License.  You may not convey a covered
work if you are a party to an arrangement with a third party that is
in the business of distributing software, under which you make payment
to the third party based on the extent of your activity of conveying
the work, and under which the third party grants, to any of the
parties who would receive the covered work from you, a discriminatory
patent license (a) in connection with copies of the covered work
conveyed by you (or copies made from those copies), or (b) primarily
for and in connection with specific products or compilations that
contain the covered work, unless you entered into that arrangement,
or that patent license was granted, prior to 28 March 2007.

  Nothing in this License shall be construed as excluding or limiting
any implied license or other defenses to infringement that may
otherwise be available to you under applicable patent law.

  12. No Surrender of Others' Freedom.

  If conditions are imposed on you (whether by court order, agreement or
otherwise) that contradict the conditions of this License, they do not
excuse you from the conditions of this License.  If you cannot convey a
covered work so as to satisfy simultaneously your obligations under this
License and any other pertinent obligations, then as a consequence you may
not convey it at all.  For example, if you agree to terms that obligate you
to collect a royalty for further conveying from those to whom you convey
the Program, the only way you could satisfy both those terms and this
License would be to refrain entirely from conveying the Program.

  13. Use with the GNU Affero General Public License.

  Notwithstanding any other provision of this License, you have
permission to link or combine any covered work with a work licensed
under version 3 of the GNU Affero General Public License into a single
combined work, and to convey the resulting work.  The terms of this
License will continue to apply to the part which is the covered work,
but the special requirements of the GNU Affero General Public License,
section 13, concerning interaction through a network will apply to the
combination as such.

  14. Revised Versions of this License.

  The Free Software Foundation may publish revised and/or new versions of
the GNU General Public License from time to time.  Such new versions will
be similar in spirit to the present version, but may differ in detail to
address new problems or concerns.

  Each version is given a distinguishing version number.  If the
Program specifies that a certain numbered version of the GNU General
Public License "or any later version" applies to it, you have the
option of following the terms and conditions either of that numbered
version or of any later version published by the Free Software
Foundation.  If the Program does not specify a version number of the
GNU General Public License, you may choose any version ever published
by the Free Software Foundation.

  If the Program specifies that a proxy can decide which future
versions of the GNU General Public License can be used, that proxy's
public statement of acceptance of a version permanently authorizes you
to choose that version for the Program.

  Later license versions may give you additional or different
permissions.  However, no additional obligations are imposed on any
author or copyright holder as a result of your choosing to follow a
later version.

  15. Disclaimer of Warranty.

  THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
ALL NECESSARY SERVICING, REPAIR OR CORRECTION.

  16. Limitation of Liability.

  IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MODIFIES AND/OR CONVEYS
THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY
GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE
USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF
DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD
PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS),
EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF
SUCH DAMAGES.

  17. Interpretation of Sections 15 and 16.

  If the disclaimer of warranty and limitation of liability provided
above cannot be given local legal effect according to their terms,
reviewing courts shall apply local law that most closely approximates
an absolute waiver of all civil liability in connection with the
Program, unless a warranty or assumption of liability accompanies a
copy of the Program in return for a fee.

                     END OF TERMS AND CONDITIONS

            How to Apply These Terms to Your New Programs

  If you develop a new program, and you want it to be of the greatest
possible use to the public, the best way to achieve this is to make it
free software which everyone can redistribute and change under these terms.

  To do so, attach the following notices to the program.  It is safest
to attach them to the start of each source file to most effectively
state the exclusion of warranty; and each file should have at least
the "copyright" line and a pointer to where the full notice is found.

    <one line to give the program's name and a brief idea of what it does.>
    Copyright (C) <year>  <name of author>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

Also add information on how to contact you by electronic and paper mail.

  If the program does terminal interaction, make it output a short
notice like this when it starts in an interactive mode:

    <program>  Copyright (C) <year>  <name of author>
    This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
    This is free software, and you are welcome to redistribute it
    under certain conditions; type `show c' for details.

The hypothetical commands `show w' and `show c' should show the appropriate
parts of the General Public License.  Of course, your program's commands
might be different; for a GUI interface, you would use an "about box".

  You should also get your employer (if you work as a programmer) or school,
if any, to sign a "copyright disclaimer" for the program, if necessary.
For more information on this, and how to apply and follow the GNU GPL, see
<https://www.gnu.org/licenses/>.

  The GNU General Public License does not permit incorporating your program
into proprietary programs.  If your program is a subroutine library, you
may consider it more useful to permit linking proprietary applications with
the library.  If this is what you want to do, use the GNU Lesser General
Public License instead of this License.  But first, please read
<https://www.gnu.org/licenses/why-not-lgpl.html>.""")
            with open(cmdwin, "w") as f:
                f.write(f"""REM Hacer que "echo" tenga curva de aprendizaje, solo en Windows FlitPack Edition
echo e
echo @e
echo off
cls
echo Curveado!. Instalando dependencias...
pip install -r lib/requirements.txt
python {nombre_logico}.py
""")
            with open(bashlinux, "w") as f:
                f.write(f"""#!/usr/bin/env sh
pip install -r "./lib/requirements.txt"
clear
/usr/bin/python3 "./{nombre_logico}.py"
""")
            with open(main_script, "w") as f:
                f.write(f"""#!/usr/bin/env python
# -*- coding: utf-8 -*-
# kejq34/myapps/system/influent.shell.vIO-34-2.18-danenone.iflapp
# kejq34/home/{folder_name}/.gites
# App: {nombre_completo}
# publisher: {empresa}
# name: {nombre_logico}
# version: IO-{version}
# script: Python3
# nocombination
#  
#  Copyright 2025 Jesus Quijada <@JesusQuijada34>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  


def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
""")
            icon_dest = os.path.join(full_path, "app", "app-icon.ico")
            if os.path.exists(IPM_ICON_PATH):
                shutil.copy(IPM_ICON_PATH, icon_dest)
            requirements_path = os.path.join(full_path, "lib", "requirements.txt")
            with open(requirements_path, "w") as f:
                f.write("# Dependencias del paquete\n")
            self.create_details_xml(full_path, empresa, nombre_logico, nombre_completo, version)
            readme_path = os.path.join(full_path, "README.md")
            readme_text = f"""# {empresa} {nombre_completo}\n\nPaquete generado con Influent Package Maker.\n\n## Ejemplo de uso\npython3 {empresa}.{nombre_logico}.v{version}/{nombre_logico}.py\n\n##"""
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(readme_text)
            self.create_status.setText(f"✅ Paquete creado en: {folder_name}/\n🔐 Protegido con sha256: {hv}")
        except Exception as e:
            self.create_status.setStyleSheet(BTN_STYLES["danger"])
            self.create_status.setText(f"❌ Error: {str(e)}")

    def create_details_xml(self, path, empresa, nombre_logico, nombre_completo, version):
        newversion = getversion()
        full_name = f"{empresa}.{nombre_logico}.v{version}"
        hash_val = hashlib.sha256(full_name.encode()).hexdigest()
        rating = "Todas las edades"
        for keyword, rate in AGE_RATINGS.items():
            if keyword in nombre_logico.lower() or keyword in nombre_completo.lower():
                rating = rate
                break
        empresa = empresa.capitalize().replace("-", " ")
        root = ET.Element("app")
        ET.SubElement(root, "publisher").text = empresa
        ET.SubElement(root, "app").text = nombre_logico
        ET.SubElement(root, "name").text = nombre_completo
        ET.SubElement(root, "version").text = f"v{version}"
        ET.SubElement(root, "with").text = sys.platform
        ET.SubElement(root, "danenone").text = newversion
        ET.SubElement(root, "correlationid").text = hash_val
        ET.SubElement(root, "rate").text = rating
        tree = ET.ElementTree(root)
        tree.write(os.path.join(path, "details.xml"))

    def init_build_tab(self):
        layout = QVBoxLayout()
        form_group = QGroupBox("Construir Paquete")
        form_layout = QVBoxLayout(form_group)
        self.input_build_empresa = QLineEdit()
        self.input_build_empresa.setPlaceholderText("Ejemplo: influent")
        self.input_build_empresa.setToolTip(LGDR_BUILD_MESSAGES["_LGDR_PUBLISHER_E"])
        form_layout.addWidget(QLabel("Fabricante:"))
        form_layout.addWidget(self.input_build_empresa)
        
        self.input_build_nombre = QLineEdit()
        self.input_build_nombre.setPlaceholderText("Ejemplo: mycoolapp")
        self.input_build_nombre.setToolTip(LGDR_BUILD_MESSAGES["_LGDR_NAME_E"])
        form_layout.addWidget(QLabel("Nombre interno:"))
        form_layout.addWidget(self.input_build_nombre)
        
        self.input_build_version = QLineEdit()
        self.input_build_version.setPlaceholderText("Ejemplo: 1.0")
        self.input_build_version.setToolTip(LGDR_BUILD_MESSAGES["_LGDR_VERSION_E"])
        form_layout.addWidget(QLabel("Versión:"))
        form_layout.addWidget(self.input_build_version)
        
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItem(".iflapp NORMAL", "1")
        self.combo_tipo.addItem(".iflappb BUNDLE", "2")
        self.combo_tipo.setToolTip(LGDR_BUILD_MESSAGES["_LGDR_TYPE_DDL"])
        form_layout.addWidget(QLabel("Tipo de paquete:"))
        form_layout.addWidget(self.combo_tipo)
        
        self.btn_build = QPushButton("Construir paquete")
        self.btn_build.setFont(BUTTON_FONT)
        self.btn_build.setStyleSheet(BTN_STYLES["default"])
        self.btn_build.setIcon(QIcon(TAB_ICONS["construir"]))
        self.btn_build.setToolTip(LGDR_BUILD_MESSAGES["_LGDR_BUILD_BTN"])
        self.btn_build.clicked.connect(self.build_package_action)
        
        self.build_status = QLabel("")
        self.build_status.setStyleSheet("color:#0277bd;")
        layout.addWidget(form_group)
        layout.addWidget(self.btn_build)
        layout.addWidget(self.build_status)
        self.tab_build.setLayout(layout)

    def build_package_action(self):
        empresa = self.input_build_empresa.text().strip().lower() or "influent"
        nombre = self.input_build_nombre.text().strip().lower() or "mycoolapp"
        version = self.input_build_version.text().strip() or "1"
        tipo = self.combo_tipo.currentData()
        self.build_status.setText("🔨 Construyendo paquete...")
        self.build_thread = BuildThread(empresa, nombre, version, tipo)
        self.build_thread.progress.connect(lambda msg: self.build_status.setText(msg))
        self.build_thread.finished.connect(lambda msg: self.build_status.setText(msg))
        self.build_thread.error.connect(lambda msg: self.build_status.setText(f"❌ Error: {msg}"))
        self.build_thread.start()

    def init_manager_tab(self):
        layout = QVBoxLayout()
        splitter = QSplitter(Qt.Horizontal)
        proj_group = QGroupBox("Proyectos locales")
        proj_layout = QVBoxLayout(proj_group)
        self.projects_list = QListWidget()
        self.projects_list.setIconSize(QtCore.QSize(32, 32))
        self.projects_list.setAlternatingRowColors(True)
        self.projects_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.projects_list.setToolTip(LGDR_NAUFRAGIO_MESSAGES["_LGDR_LOCAL_LV"])
        proj_layout.addWidget(self.projects_list)
        splitter.addWidget(proj_group)
        
        apps_group = QGroupBox("Apps instaladas")
        apps_layout = QVBoxLayout(apps_group)
        self.apps_list = QListWidget()
        self.apps_list.setIconSize(QtCore.QSize(32, 32))
        self.apps_list.setAlternatingRowColors(True)
        self.apps_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.apps_list.setToolTip(LGDR_NAUFRAGIO_MESSAGES["_LGDR_INSTALLED_LV"])
        apps_layout.addWidget(self.apps_list)
        splitter.addWidget(apps_group)
        
        splitter.setSizes([1, 1])
        layout.addWidget(splitter)
        btn_row = QHBoxLayout()
        btn_refresh = QPushButton("Refrescar listas")
        btn_refresh.setFont(BUTTON_FONT)
        btn_refresh.setStyleSheet(BTN_STYLES["info"])
        btn_refresh.setIcon(QIcon(IPM_ICON_PATH))
        btn_refresh.setToolTip(LGDR_NAUFRAGIO_MESSAGES["_LGDR_REFRESH_BTN"])
        btn_refresh.clicked.connect(self.load_manager_lists)
        btn_row.addWidget(btn_refresh)
        
        btn_install = QPushButton("Instalar paquete")
        btn_install.setFont(BUTTON_FONT)
        btn_install.setStyleSheet(BTN_STYLES["success"])
        btn_install.setIcon(QIcon(TAB_ICONS["instalar"]))
        btn_install.setToolTip(LGDR_NAUFRAGIO_MESSAGES["_LGDR_INSTALL_BTN"])
        btn_install.clicked.connect(self.install_package_action)
        btn_row.addWidget(btn_install)
        
        btn_uninstall = QPushButton("Desinstalar paquete")
        btn_uninstall.setFont(BUTTON_FONT)
        btn_uninstall.setStyleSheet(BTN_STYLES["danger"])
        btn_uninstall.setIcon(QIcon(TAB_ICONS["desinstalar"]))
        btn_uninstall.setToolTip(LGDR_NAUFRAGIO_MESSAGES["_LGDR_UNINSTALL_BTN"])
        btn_uninstall.clicked.connect(self.uninstall_package_action)
        btn_row.addWidget(btn_uninstall)
        layout.addLayout(btn_row)
        
        self.manager_status = QLabel("")
        self.manager_status.setWordWrap(True)
        self.manager_status.setToolTip("Estado de la app")
        layout.addWidget(self.manager_status)
        self.tab_manager.setLayout(layout)
        self.load_manager_lists()
        self.projects_list.itemDoubleClicked.connect(lambda item: self.on_project_double_click(item))
        self.apps_list.itemDoubleClicked.connect(lambda item: self.on_app_double_click(item))

    def get_package_list(self, base):
        packages = []
        for d in os.listdir(base):
            folder = os.path.join(base, d)
            details_path = os.path.join(folder, "details.xml")
            icon_path = os.path.join(folder, "app", "app-icon.ico")
            if os.path.isdir(folder) and os.path.exists(details_path):
                try:
                    tree = ET.parse(details_path)
                    root = tree.getroot()
                    details = {child.tag: child.text for child in root}
                    empresa = details.get("publisher", "Origen Desconocido")
                    titulo = details.get("name", d)
                    version = details.get("version", "v?")
                    packages.append({
                        "folder": folder,
                        "empresa": empresa,
                        "titulo": titulo,
                        "version": version,
                        "icon": icon_path if os.path.exists(icon_path) else None,
                        "name": d,
                    })
                except Exception:
                    continue
        return packages

    def load_manager_lists(self):
        self.projects_list.clear()
        self.apps_list.clear()
        projects = self.get_package_list(BASE_DIR)
        for p in projects:
            icon = QIcon(p["icon"]) if p["icon"] else self.style().standardIcon(QStyle.SP_ComputerIcon)
            text = p['empresa'].capitalize()
            text = f"{text} {p['titulo']} | {p['version']}"
            item = QListWidgetItem(icon, text)
            item.setData(QtCore.Qt.UserRole, p)
            self.projects_list.addItem(item)
        apps = self.get_package_list(FLATR_APPS)
        for a in apps:
            icon = QIcon(a["icon"]) if a["icon"] else self.style().standardIcon(QStyle.SP_DesktopIcon)
            text = a['empresa'].capitalize()
            text = f"{text} {a['titulo']} | {a['version']}"
            item = QListWidgetItem(icon, text)
            item.setData(QtCore.Qt.UserRole, a)
            self.apps_list.addItem(item)

    def on_project_double_click(self, item):
        pkg = item.data(QtCore.Qt.UserRole)
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Proyecto: {pkg['titulo']}")
        dlg.resize(500, 480)
        l = QVBoxLayout(dlg)
        icon = QIcon(pkg["icon"]) if pkg["icon"] else self.style().standardIcon(QStyle.SP_ComputerIcon)
        empresa_cap = pkg['empresa'].capitalize()
        info = f"<b>Empresa:</b> {empresa_cap}<br><b>Título:</b> {pkg['titulo']}<br><b>Versión:</b> {pkg['version']}<br><b>Carpeta:</b> {pkg['folder']}"
        lbl = QLabel(info)
        lbl.setAlignment(QtCore.Qt.AlignLeft)
        l.addWidget(lbl)
        scripts_list = QListWidget()
        scripts_list.setIconSize(QtCore.QSize(24,24))
        l.addWidget(QLabel("Scripts .py disponibles para ejecutar:"))
        l.addWidget(scripts_list)
        py_files = []
        for root, _, files in os.walk(pkg["folder"]):
            for f in files:
                if f.endswith(".py"):
                    py_files.append(os.path.join(root, f))
        for pyf in py_files:
            item_script = QListWidgetItem(icon, os.path.relpath(pyf, pkg["folder"]))
            item_script.setData(QtCore.Qt.UserRole, pyf)
            scripts_list.addItem(item_script)
        run_btn = QPushButton("Ejecutar script seleccionado")
        run_btn.setFont(BUTTON_FONT)
        run_btn.setStyleSheet(BTN_STYLES["success"])
        run_btn.setToolTip(LGDR_NAUFRAGIO_MESSAGES["_LGDR_RUNPY_BTN"])
        l.addWidget(run_btn)
        install_btn = QPushButton("Instalar proyecto como app")
        install_btn.setFont(BUTTON_FONT)
        install_btn.setStyleSheet(BTN_STYLES["info"])
        install_btn.setToolTip(LGDR_NAUFRAGIO_MESSAGES["_LGDR_INSTALLPROJ_BTN"])
        l.addWidget(install_btn)
        uninstall_btn = QPushButton("Desinstalar proyecto")
        uninstall_btn.setFont(BUTTON_FONT)
        uninstall_btn.setStyleSheet(BTN_STYLES["danger"])
        uninstall_btn.setToolTip(LGDR_NAUFRAGIO_MESSAGES["_LGDR_UNINSTALLPROJ_BTN"])
        l.addWidget(uninstall_btn)
        status = QLabel("")
        l.addWidget(status)
        def run_script():
            s_item = scripts_list.currentItem()
            if not s_item:
                status.setText("Selecciona un script.")
                return
            script_path = s_item.data(QtCore.Qt.UserRole)
            import subprocess
            try:
                subprocess.Popen([sys.executable, script_path], cwd=os.path.dirname(script_path))
                status.setText(f"Ejecutando: {script_path}")
            except Exception as e:
                status.setText(f"Error: {e}")
        def install_project():
            # Busca el paquete .iflapp/.iflappb y lo instala como app
            found = False
            for ext in [".iflapp", ".iflappb"]:
                pkg_file = os.path.join(BASE_DIR, pkg["name"] + ext)
                if os.path.exists(pkg_file):
                    target_dir = os.path.join(FLATR_APPS, pkg["name"])
                    os.makedirs(target_dir, exist_ok=True)
                    try:
                        with zipfile.ZipFile(pkg_file, 'r') as zip_ref:
                            zip_ref.extractall(target_dir)
                        status.setText(f"✅ Proyecto instalado como app")
                        found = True
                        self.load_manager_lists()
                        break
                    except Exception as e:
                        status.setText(f"❌ Error al instalar: {e}")
            if not found:
                status.setText("❌ No se encontró paquete comprimido (.iflapp/.iflappb) para instalar")
        def uninstall_project():
            # Elimina la carpeta del proyecto (sin afectar apps instaladas)
            try:
                shutil.rmtree(pkg["folder"])
                status.setText(f"🗑️ Proyecto desinstalado")
                self.load_manager_lists()
            except Exception as e:
                status.setText(f"❌ Error al desinstalar: {e}")
        run_btn.clicked.connect(run_script)
        install_btn.clicked.connect(install_project)
        uninstall_btn.clicked.connect(uninstall_project)
        dlg.exec_()

    def on_app_double_click(self, item):
        pkg = item.data(QtCore.Qt.UserRole)
        dlg = QDialog(self)
        dlg.setWindowTitle(f"App instalada: {pkg['titulo']}")
        dlg.resize(500, 480)
        l = QVBoxLayout(dlg)
        icon = QIcon(pkg["icon"]) if pkg["icon"] else self.style().standardIcon(QStyle.SP_DesktopIcon)
        info = f"<b>Empresa:</b> {pkg['empresa']}<br><b>Título:</b> {pkg['titulo']}<br><b>Versión:</b> {pkg['version']}<br><b>Carpeta:</b> {pkg['folder']}"
        lbl = QLabel(info)
        lbl.setAlignment(QtCore.Qt.AlignLeft)
        l.addWidget(lbl)
        scripts_list = QListWidget()
        scripts_list.setIconSize(QtCore.QSize(24,24))
        l.addWidget(QLabel("Scripts .py disponibles para ejecutar:"))
        l.addWidget(scripts_list)
        py_files = []
        for root, _, files in os.walk(pkg["folder"]):
            for f in files:
                if f.endswith(".py"):
                    py_files.append(os.path.join(root, f))
        for pyf in py_files:
            item_script = QListWidgetItem(icon, os.path.relpath(pyf, pkg["folder"]))
            item_script.setData(QtCore.Qt.UserRole, pyf)
            scripts_list.addItem(item_script)
        run_btn = QPushButton("Ejecutar script seleccionado")
        run_btn.setFont(BUTTON_FONT)
        run_btn.setStyleSheet(BTN_STYLES["success"])
        run_btn.setToolTip(LGDR_NAUFRAGIO_MESSAGES["_LGDR_RUNPYAPP_BTN"])
        l.addWidget(run_btn)
        uninstall_btn = QPushButton("Desinstalar app")
        uninstall_btn.setFont(BUTTON_FONT)
        uninstall_btn.setStyleSheet(BTN_STYLES["danger"])
        uninstall_btn.setToolTip(LGDR_NAUFRAGIO_MESSAGES["_LGDR_UNINSTALLAPP_BTN"])
        l.addWidget(uninstall_btn)
        status = QLabel("")
        l.addWidget(status)
        def run_script():
            s_item = scripts_list.currentItem()
            if not s_item:
                status.setText("Selecciona un script.")
                return
            script_path = s_item.data(QtCore.Qt.UserRole)
            import subprocess
            try:
                subprocess.Popen([sys.executable, script_path], cwd=os.path.dirname(script_path))
                status.setText(f"Ejecutando: {script_path}")
            except Exception as e:
                status.setText(f"Error: {e}")
        def uninstall_app():
            try:
                shutil.rmtree(pkg["folder"])
                status.setText(f"🗑️ App desinstalada")
                self.load_manager_lists()
            except Exception as e:
                status.setText(f"❌ Error al desinstalar: {e}")
        run_btn.clicked.connect(run_script)
        uninstall_btn.clicked.connect(uninstall_app)
        dlg.exec_()

    def install_package_action(self):
        files = QFileDialog.getOpenFileNames(self, "Selecciona paquetes para instalar", BASE_DIR, "Paquetes (*.iflapp *.iflappb)")[0]
        for file_path in files:
            if not file_path:
                continue
            pkg_name = os.path.basename(file_path).replace(".iflapp", "").replace(".iflappb", "")
            target_dir = os.path.join(FLATR_APPS, pkg_name)
            os.makedirs(target_dir, exist_ok=True)
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(target_dir)
                self.manager_status.setText(f"✅ Instalado: {pkg_name} en Flatr Apps")
                # Asociación de extensión y menú inicio en Windows
                if sys.platform.startswith('win'):
                    self.setup_windows_shortcut(target_dir, pkg_name)
            except Exception as e:
                self.manager_status.setText(f"❌ Error al instalar {pkg_name}: {e}")
        self.load_manager_lists()

    def setup_windows_shortcut(self, target_dir, pkg_name):
        details_path = os.path.join(target_dir, "details.xml")
        if not os.path.exists(details_path):
            return
        try:
            tree = ET.parse(details_path)
            root = tree.getroot()
            nombre = root.findtext("name", pkg_name)
            empresa = root.findtext("publisher", "Influent")
            icon_path = os.path.join(target_dir, "app", "app-icon.ico")
            py_scripts = []
            for root_dir, _, files in os.walk(target_dir):
                for f in files:
                    if f.endswith(".py"):
                        py_scripts.append(os.path.join(root_dir, f))
            main_script = py_scripts[0] if py_scripts else None
            shortcut_name = f"{nombre} - Influent"
            try:
                import pythoncom
                import win32com.client
                from win32com.shell import shell, shellcon
                desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
                start_menu = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs")
                program_files = os.path.join(os.environ["ProgramFiles"], empresa, nombre)
                os.makedirs(program_files, exist_ok=True)
                for item in os.listdir(target_dir):
                    s = os.path.join(target_dir, item)
                    d = os.path.join(program_files, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        shutil.copy2(s, d)
                if main_script:
                    shell_obj = win32com.client.Dispatch("WScript.Shell")
                    shortcut = shell_obj.CreateShortcut(os.path.join(start_menu, f"{shortcut_name}.lnk"))
                    shortcut.TargetPath = sys.executable
                    shortcut.Arguments = f'"{main_script}"'
                    shortcut.WorkingDirectory = os.path.dirname(main_script)
                    shortcut.IconLocation = icon_path if os.path.exists(icon_path) else sys.executable
                    shortcut.Description = f"Influent App: {nombre}"
                    shortcut.Save()
            except Exception as e:
                self.manager_status.setText(self.manager_status.text() + f"\n⚠️ Error acceso directo: {str(e)}")
        except Exception as e:
            self.manager_status.setText(self.manager_status.text() + f"\n⚠️ Error detalles.xml: {str(e)}")

    def uninstall_package_action(self):
        item = self.apps_list.currentItem()
        if not item:
            self.manager_status.setText("Selecciona un paquete instalado para desinstalar.")
            return
        pkg = item.data(QtCore.Qt.UserRole)
        try:
            shutil.rmtree(pkg["folder"])
            self.manager_status.setText(f"🗑️ Desinstalado: {pkg['titulo']}")
        except Exception as e:
            self.manager_status.setText(f"❌ Error al desinstalar: {e}")
        self.load_manager_lists()

    def init_about_tab(self):
        layout = QVBoxLayout()
        about_text = (
            "<b>Influent Package Suite Todo en Uno</b><br>"
            "Creador, empaquetador e instalador de proyectos Influent (.iflapp, .iflappb) para terminal y sistema.<br><br>"
            "<b>Funciones:</b><ul>"
            "<li>Interfaz adaptable y moderna</li>"
            "<li>Gestor visual de proyectos y apps instaladas</li>"
            "<li>Instalación/Desinstalación fácil con doble clic</li>"
            "<li>Construcción de paquetes protegidos</li>"
            "<li>Accesos directos y menú inicio en Windows</li>"
            "<li>Soporte para iconos y detalles personalizados</li>"
            "<li>Ejecuta scripts .py desde la interfaz</li>"
            "<li>Paneles ajustables y organización por pestañas</li>"
            "</ul>"
            "<b>Autor:</b> Jesus Quijada (@JesusQuijada34)<br>"
            "<b>GitHub:</b> <a href='https://github.com/jesusquijada34/packagemaker/'>packagemaker</a>"
        )
        about_label = QLabel(about_text)
        about_label.setOpenExternalLinks(True)
        layout.addWidget(about_label)
        self.tab_about.setLayout(layout)

def main():
    app = QApplication(sys.argv)
    app.setFont(APP_FONT)
    w = PackageTodoGUI()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
