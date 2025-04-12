import json
import sys
import os
import webbrowser
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QCursor
from GUI import installer_window
from mod_installer import install_mod_zip, remove_mod, find_deadlock_install_path
from gamebanana_downloader import download_zip_from_gamebanana
from PyQt6.QtWidgets import QApplication


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("icon.ico")))

    auto_path = find_deadlock_install_path()
    window = installer_window.DeadlockModInstaller()
    window.show()
    sys.exit(app.exec())
