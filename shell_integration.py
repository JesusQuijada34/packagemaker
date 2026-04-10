# Compatibilidad con la antigua ruta de importación de shell integration.
from shell.shellIntegration import ShellIntegration

__all__ = ['ShellIntegration']

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--install":
            ShellIntegration().install_all()
        elif sys.argv[1] == "--uninstall":
            ShellIntegration().uninstall_all()
        elif sys.argv[1] == "--create-shortcuts":
            ShellIntegration().create_shortcuts()
        else:
            print("Uso: python shell_integration.py --install|--uninstall|--create-shortcuts")
    else:
        print("Uso: python shell_integration.py --install|--uninstall|--create-shortcuts")
