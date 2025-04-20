import os
import json
from turtle import color
from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QFileDialog, QMessageBox, QProgressBar,
    QHBoxLayout, QListWidget, QListWidgetItem, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer

from install_logic.mod_installer import install_mod_zip, remove_mod, find_deadlock_install_path
from install_logic.gamebanana_downloader import download_zip_from_gamebanana


class DeadlockModInstaller(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Deadlock Visual Mod Installer")
        self.setFixedSize(500, 540)

        # Apply dark mode stylesheet by default
        dark_mode_stylesheet = """
            QWidget {
                background-color: #2E2E2E;
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #444444;
                color: #FFFFFF;
                border: 1px solid #555555;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QLineEdit {
                background-color: #3E3E3E;
                color: #FFFFFF;
                border: 1px solid #555555;
            }
            QListWidget {
                background-color: #3E3E3E;
                color: #FFFFFF;
            }
            QProgressBar {
                background-color: #3E3E3E;
                color: #FFFFFF;
                border: 1px solid #555555;
            }
            QLabel {
                color: #FFFFFF;
            }
        """
        self.setStyleSheet(dark_mode_stylesheet)

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

        self.mods_list = QListWidget()
        self.layout.addWidget(self.mods_list)

        self.link_label = QLabel("<a href='https://gamebanana.com/mods/cats/33295' style='color: white;'>🔗 Find more mods here</a>")
        self.link_label.setOpenExternalLinks(True)
        self.link_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.link_label)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste GameBanana URL here; Example 'https://gamebanana.com/mods/571935'")
        self.layout.addWidget(self.url_input)

        self.url_button = QPushButton("Install Mod from URL")
        self.url_button.clicked.connect(self.install_mod_from_url)
        self.layout.addWidget(self.url_button)

        self.setLayout(self.layout)
        self.game_path = ""

        auto_path = find_deadlock_install_path()
        if auto_path:
            self.game_path = auto_path
            self.label.setText(f"✅ Auto-detected game folder:\n{auto_path}")
            self.mod_btn.setEnabled(True)
            self.refresh_mod_list()

    # Removed the toggle_dark_mode method and the dark_mode_btn



    def select_game_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Deadlock Install Folder")
        if folder:
            self.game_path = folder
            self.label.setText(f"Selected folder: {folder}")
            self.mod_btn.setEnabled(True)
            self.refresh_mod_list()

    def confirm_overwrite(self, mod_name: str) -> bool:
        confirm = QMessageBox.question(
            self,
            "Overwrite Mod?",
            f"The mod '{mod_name}' is already installed. Do you want to overwrite it?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return confirm == QMessageBox.StandardButton.Yes

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
                success, message = install_mod_zip(zip_path, self.game_path, self.confirm_overwrite)
                self.progress_bar.setValue(100)
                if success:
                    QMessageBox.information(self, "Success", message)
                    self.label.setText("✅ Mod installed successfully.")
                    self.refresh_mod_list()
                else:
                    QMessageBox.critical(self, "Error", message)
                    self.label.setText("❌ Installation failed.")
                self.progress_bar.setVisible(False)

            QTimer.singleShot(800, finish_install)
        else:
            QMessageBox.warning(self, "Warning", "You must select a folder and a ZIP file.")

    def install_mod_from_url(self):
        url = self.url_input.text().strip()
        if not url or not self.game_path:
            QMessageBox.warning(self, "Warning", "You must enter a URL and select a game folder.")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(20)
        self.label.setText("Downloading mod from URL...")

        def finish_download():
            zip_path = download_zip_from_gamebanana(url, os.path.join(self.game_path, "temp_mods"))
            if zip_path:
                success, message = install_mod_zip(zip_path, self.game_path, self.confirm_overwrite)
                self.progress_bar.setValue(100)
                if success:
                    QMessageBox.information(self, "Success", message)
                    self.label.setText("✅ Mod installed successfully.")
                    self.refresh_mod_list()
                else:
                    QMessageBox.critical(self, "Error", message)
                    self.label.setText("❌ Installation failed.")
            else:
                QMessageBox.critical(self, "Error", "Failed to download mod from URL.")
            self.progress_bar.setVisible(False)

        QTimer.singleShot(600, finish_download)

    def refresh_mod_list(self):
        self.mods_list.clear()
        mods_meta_path = os.path.join(self.game_path, "game", "citadel", "addons", "installed_mods.json")
        if os.path.exists(mods_meta_path):
            with open(mods_meta_path, "r", encoding="utf-8") as f:
                mods = json.load(f)
            for mod_name in mods:
                item = QListWidgetItem()
                widget = QWidget()
                layout = QHBoxLayout()
                label = QLabel(mod_name)
                remove_btn = QPushButton("Remove")
                remove_btn.clicked.connect(lambda checked, name=mod_name: self.remove_mod(name))
                layout.addWidget(label)
                layout.addWidget(remove_btn)
                layout.setContentsMargins(0, 0, 0, 0)
                widget.setLayout(layout)
                item.setSizeHint(widget.sizeHint())
                self.mods_list.addItem(item)
                self.mods_list.setItemWidget(item, widget)

    def remove_mod(self, mod_name):
        confirm = QMessageBox.question(self, "Confirm Removal", f"Are you sure you want to remove '{mod_name}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            success, message = remove_mod(mod_name, self.game_path)
            if success:
                QMessageBox.information(self, "Removed", message)
                self.refresh_mod_list()
            else:
                QMessageBox.critical(self, "Error", message)
