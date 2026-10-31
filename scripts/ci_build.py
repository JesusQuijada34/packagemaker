import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.iflapp_format import pack_iflapp

def get_metadata():
    details_path = Path("details.xml")
    if not details_path.exists():
        print("❌ details.xml no encontrado")
        sys.exit(1)
    
    try:
        tree = ET.parse(details_path)
        root = tree.getroot()
        metadata = {
            'publisher': root.findtext('publisher') or root.findtext('empresa') or 'Unknown',
            'app': root.findtext('app') or root.findtext('name') or 'Unknown',
            'version': root.findtext('version') or 'v1.0',
            'platform': root.findtext('platform') or root.findtext('plataforma') or 'AlphaCube',
        }
        return metadata
    except Exception as e:
        print(f"❌ Error al parsear details.xml: {e}")
        sys.exit(1)

def create_iflapp(metadata, platform=None):
    allowed_platforms = {"Danenone", "Knosthalij", "AlphaCube"}
    platform = (platform or metadata.get("platform") or "AlphaCube").strip()
    if platform not in allowed_platforms:
        raise ValueError(f"Plataforma no válida: {platform}")
    app_name = metadata['app'].strip()
    version = metadata['version'].strip()
    publisher = metadata['publisher'].strip()
    if not version.startswith("v"):
        version = f"v{version}"
    for existing_platform in ("Danenone", "Knosthalij", "AlphaCube"):
        suffix = f"-{existing_platform}"
        if version.endswith(suffix):
            version = version[:-len(suffix)]
            break
    iflapp_name = f"{publisher}.{app_name}.{version}-{platform}.iflapp"
    
    output_dir = Path("dist")
    output_dir.mkdir(exist_ok=True)
    iflapp_path = output_dir / iflapp_name

    print(f"📦 Creando paquete blindado: {iflapp_name}...")

    # Contenedor ``.iflapp`` v2 (cabecera indexada + payload LZMA firmado), no un
    # ZIP. La identidad viaja en claro en la cabecera para poder inspeccionarla
    # sin descifrar ni descomprimir.
    identity = {
        "publisher": publisher,
        "app": app_name,
        "name": app_name,
        "version": version,
        "platform": platform,
    }
    pack_iflapp(Path("."), iflapp_path, identity=identity)

    print(f"✅ Paquete creado con éxito en: {iflapp_path}")
    return iflapp_path

if __name__ == "__main__":
    meta = get_metadata()
    create_iflapp(meta)
