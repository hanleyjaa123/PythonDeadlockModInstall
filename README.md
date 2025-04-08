# Deadlock Visual Mod Installer

[DOWNLOAD HERE](https://hanleyjaa.itch.io/deadlock-mod-installer)

A lightweight desktop tool for easily installing and managing visual mods for the game **Deadlock**.

Built with Python and PyQt6, this app allows users to:

- ✅ Automatically detect your Deadlock install folder  
- 📦 Install visual mod `.zip` files containing `.vpk` packages  
- 🌐 Download mods directly from [GameBanana](https://gamebanana.com/games/13937) using a URL  
- 🧹 Remove installed mods with one click  
- 🔄 Automatically update `gameinfo.gi` to activate your mods  
- 🧠 Detect and prompt before overwriting existing mods  
- 🗂️ Track installed mods with `installed_mods.json`  

---

## 🚀 Features

- **Auto Detection** – Detects Deadlock installation path from Steam  
- **GameBanana URL Support** – Paste a mod URL, auto-download and install the `.zip`  
- **Mod Overwrite Warning** – Prompts user before overwriting existing mods  
- **Installed Mods List** – Displays currently installed mods with remove buttons  
- **Installed Mods Tracker** – Saves mod list to `installed_mods.json`  
- **Clean PyQt6 Interface** – Simple, responsive GUI with progress bar  
- **GameBanana Hyperlink** – Easily jump to mod downloads

---

## 📁 How to Use

### 1. Run the App

2. Select Your Game Folder
Automatically detects your Deadlock install via Steam

Or select the game directory manually

3. Install Mods
📂 Install Mod ZIP – Choose a .zip containing a .vpk
                     OR:
🌐 Install Mod from URL – Paste a GameBanana URL and auto-install

4. Remove Mods
Installed mods show up in a list with Remove buttons

Mods are tracked via installed_mods.json

Confirms before removing

🧠 App Structure
```
PythonDeadlockModInstall/
├── PythonDeadlockModInstall.py     # Main PyQt GUI
├── mod_installer.py                # VPK handling, install/remove logic
├── gamebanana_downloader.py       # GameBanana API + ZIP downloader
├── icon.ico                        # App icon
├── temp_mods/                      # Temporary downloads
├── README.md                       # This file
└── .gitignore                      # Build + temp file exclusions

```
📦 Dependencies
Python 3.10 or newer

 - PyQt6

 - requests

Install them with:

```
pip install PyQt6 requests
```
💬 Feedback & Contributions
Pull requests and feedback are welcome!
Feel free to open an issue or fork the repo to contribute.
