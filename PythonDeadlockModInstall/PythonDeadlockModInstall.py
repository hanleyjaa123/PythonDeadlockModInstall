import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QFileDialog, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from mod_installer import install_mod_zip, find_deadlock_install_path

class DeadlockModInstaller(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Deadlock Visual Mod Installer")
        self.setFixedSize(400, 270)

        self.layout = QVBoxLayout()

        self.label = QLabel("Step 1: Select your Deadlock install folder")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label)

        self.folder_btn = QPushButton("Select Game Folder")
        self.folder_btn.clicked.connect(self.select_game_folder)
        self.layout.addWidget(self.folder_btn)

        self.mod_btn = QPushButton("Install Mod ZIP")
        self.mod_btn.clicked.connect(self.install_mod)
        self.mod_btn.setEnabled(False)
        self.layout.addWidget(self.mod_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)

        self.setLayout(self.layout)
        self.game_path = ""

        # Try auto-detect Deadlock installation
        auto_path = find_deadlock_install_path()
        if auto_path:
            self.game_path = auto_path
            self.label.setText(f"✅ Auto-detected game folder:\n{auto_path}")
            self.mod_btn.setEnabled(True)

    def select_game_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Deadlock Install Folder")
        if folder:
            self.game_path = folder
            self.label.setText(f"Selected folder: {folder}")
            self.mod_btn.setEnabled(True)

    def install_mod(self):
        zip_path, _ = QFileDialog.getOpenFileName(self, "Select Mod ZIP", "", "ZIP Files (*.zip)")
        if zip_path and self.game_path:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.label.setText("Installing mod...")

            QTimer.singleShot(200, lambda: self.progress_bar.setValue(25))
            QTimer.singleShot(400, lambda: self.progress_bar.setValue(50))
            QTimer.singleShot(600, lambda: self.progress_bar.setValue(75))

            def finish_install():
                success, message = install_mod_zip(zip_path, self.game_path)
                self.progress_bar.setValue(100)
                if success:
                    QMessageBox.information(self, "Success", message)
                    self.label.setText("✅ Mod installed successfully.")
                else:
                    QMessageBox.critical(self, "Error", message)
                    self.label.setText("❌ Installation failed.")
                self.progress_bar.setVisible(False)

            QTimer.singleShot(800, finish_install)
        else:
            QMessageBox.warning(self, "Warning", "You must select a folder and a ZIP file.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DeadlockModInstaller()
    window.show()
    sys.exit(app.exec())
