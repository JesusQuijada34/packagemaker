from PyQt6.QtCore import QThread, pyqtSignal
from lib.moonFixWizard import verificar_github_username


class GitHubVerifyThread(QThread):
    """Thread para verificar username de GitHub"""
    finished = pyqtSignal(bool, str)  # bool success, str message_or_url

    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username

    def run(self):
        valido, resultado = verificar_github_username(self.username)
        # resultado será el URL si es valido, o mensaje de error si no
        self.finished.emit(valido, resultado)