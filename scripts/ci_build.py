import os
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

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
        }
        return metadata
    except Exception as e:
        print(f"❌ Error al parsear details.xml: {e}")
        sys.exit(1)

def create_iflapp(metadata):
    app_name = metadata['app']
    version = metadata['version']
    publisher = metadata['publisher']
    
    output_dir = Path("dist")
    output_dir.mkdir(exist_ok=True)
    
    iflapp_name = f"{publisher}.{app_name}.{version}-CI.iflapp"
    iflapp_path = output_dir / iflapp_name
    
    print(f"📦 Creando paquete: {iflapp_name}...")
    
    exclude_patterns = [".git", ".github", "dist", "build", "__pycache__", "*.pyc", ".gitignore"]
    
    with zipfile.ZipFile(iflapp_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in exclude_patterns]
            for file in files:
                if any(file.endswith(ext) for ext in [".pyc"]):
                    continue
                if file in exclude_patterns:
                    continue
                file_path = Path(root) / file
                arcname = file_path.relative_to(".")
                zf.write(file_path, arcname)
    
    print(f"✅ Paquete creado con éxito en: {iflapp_path}")
    return iflapp_path

if __name__ == "__main__":
    meta = get_metadata()
    create_iflapp(meta)
