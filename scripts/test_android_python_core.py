import json
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "android" / "app" / "src" / "main" / "python"))
import packagemaker_android as pm

with tempfile.TemporaryDirectory() as tmp:
    result = pm.create_project(tmp, {"publisher": "influent", "app": "demo", "version": "1.0.0", "author": "Test", "name": "Demo", "platform": "AlphaCube"})
    assert result["ok"]
    validation = pm.validate_project(result["path"])
    assert validation["ok"], validation
    package = pm.package_project(result["path"], str(Path(tmp) / "demo.iflapp"))
    assert package["ok"] and Path(package["path"]).is_file()
    print(json.dumps({"create": result, "validate": validation, "package": package}, ensure_ascii=False))
