"""Compatibilidad para la integración del shell de Windows.

El módulo real depende de APIs exclusivas de Windows. El wrapper debe seguir
siendo importable en Linux/macOS para que la CLI pueda informar que la acción
no está disponible, en lugar de fallar por un BOM o por ``winreg`` al importar.
"""

try:
    from shell.shellIntegration import ShellIntegration as _ShellIntegration
except ImportError as exc:
    _SHELL_IMPORT_ERROR = exc

    class ShellIntegration:
        """Marcador que informa cuando la integración solo está disponible en Windows."""

        def __init__(self, *args, **kwargs):
            raise ImportError(
                "La integración del shell solo está disponible en Windows."
            ) from _SHELL_IMPORT_ERROR
else:
    ShellIntegration = _ShellIntegration

__all__ = ["ShellIntegration"]


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        try:
            shell = ShellIntegration()
            action = sys.argv[1]
            if action == "--install":
                result = shell.install_all()
            elif action == "--uninstall":
                result = shell.uninstall_all()
            elif action == "--create-shortcuts":
                result = shell.create_shortcuts()
            else:
                print("Uso: python shell_integration.py --install|--uninstall|--create-shortcuts")
                raise SystemExit(2)
            raise SystemExit(0 if result else 1)
        except ImportError as exc:
            print(f"No disponible: {exc}")
            raise SystemExit(1)
    else:
        print("Uso: python shell_integration.py --install|--uninstall|--create-shortcuts")
        raise SystemExit(2)
