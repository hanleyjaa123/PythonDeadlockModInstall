# Deadlock Visual Mod Installer

**A simple, open-source visual mod installer for Deadlock (by Valve).**

Deadlock Visual Mod Installer is a lightweight Windows utility that allows players to easily install `.vpk`-based visual mods into the Deadlock game without needing to manually copy files or edit system directories.

This tool is designed for ease-of-use, mod compatibility, and safety — no background processes, no internet access, and fully open source.

---

## 🔧 Features

- ✅ Automatically extracts `.vpk` files to the correct Deadlock `addons` directory
- ✅ Automatically renames conflicting `.vpk` files to avoid overwrites
- ✅ Detects and modifies the required section in `gameinfo.gi`
- ✅ Automatically locates your Deadlock installation via Steam (if available)
- ✅ Clean, modern GUI using PyQt6
- ✅ No installer required (portable `.exe`)
- ✅ Source code available and fully auditable

---

## 📥 Installation

### 🔒 Download

- You can download the latest **portable `.exe`** from the [Releases](https://github.com/Hanleyjaa123/deadlock-mod-installer/releases) tab.
- Or, clone the source and run it yourself:
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
### 🎮 How to Use

1. **Launch the app.**

2. The installer will **automatically try to detect your Deadlock install folder** via Steam.  
   - If it's **not found**, click **`Select Game Folder`** and choose it manually.

3. Click **`Install Mod ZIP`** and select a `.zip` file containing your `.vpk` mod.

4. The tool will handle the rest:
   - 📦 Extract the `.vpk` to: `Deadlock\game\citadel\addons\`
   - 🔁 Automatically rename the file if there's a conflict
   - 🛠 Patch `gameinfo.gi` to include the mod folder (if not already patched)

5. ✅ Launch Deadlock and enjoy your mod!

> ⚠️ **Note:** The standalone `.exe` may trigger antivirus false positives because it's unsigned and created with PyInstaller.  
> You can verify it's safe by reviewing or running the source code directly.
```bash
git clone https://github.com/your-username/deadlock-mod-installer.git
cd deadlock-mod-installer
pip install -r requirements.txt
python PythonDeadlockModInstall.py
```



