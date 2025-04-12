import sys
import os
from PyQt6.QtGui import QIcon
from GUI import installer_window
from mod_installer import find_deadlock_install_path
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
