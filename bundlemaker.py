import sys, os, time, zipfile, hashlib, shutil
import xml.etree.ElementTree as ET

plataforma_platform = sys.platform
plataforma_name = os.name
if plataforma_platform.startswith("win"):
    home = os.path.join(os.environ["USERPROFILE"], "My Documents", "Influent Packages")
    apps = os.path.join(os.environ["USERPROFILE"], "My Documents", "Flatr Apps")
elif plataforma_platform.startswith("linux"):
    home = os.path.expanduser("~/Documentos/Influent Packages")
    apps = os.path.expanduser("~/Documentos/Flatr Apps")
else:
    home = "Influent Packages/"
    apps = "Flatr Apps/"

icon = "app/app-icon.ico"
folders = "bundle,res,data,code,bin,manifest,activity,theme,blob"
plataforma = plataforma_platform.capitalize()
nombre = plataforma_name.capitalize()
publisher = ""
bundle = ""
title = ""
version = ""
env = "knosthalij"
sub = ""
desk = f"""[Desktop Entry]
Name[es]={title}
Name={title}
GenericName[es]={sub}
GenericName={sub}
Exec={home}{dest}{bundle}
# Translators: Do NOT translate or transliterate this text (this is an icon file name)!
Icon={home}{dest}/bundle/bundle-icon.ico
Terminal={term}
Type=Application
StartupNotify=true
NoDisplay=false
OnlyShowIn=MATE;
X-MATE-Autostart-Phase=Desktop
X-MATE-Autostart-Notify=true
X-MATE-AutoRestart=true
X-MATE-Provides={bundle}"""

def getversion():
    newversion = time.strftime("%y.%m-%H.%M")
    return f"v{newversion}-{env}"
