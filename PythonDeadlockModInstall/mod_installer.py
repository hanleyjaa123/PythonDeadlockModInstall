import os
import zipfile
import shutil
import winreg

def install_mod_zip(zip_path: str, deadlock_root: str) -> tuple[bool, str]:
    """
    Installs a Deadlock mod from a ZIP containing a .vpk file.
    Extracts to the addons folder and updates gameinfo.gi if needed.
    """
    citadel_dir = os.path.join(deadlock_root, "game", "citadel")
    addons_dir = os.path.join(citadel_dir, "addons")
    gameinfo_path = os.path.join(citadel_dir, "gameinfo.gi")

    if not os.path.exists(addons_dir):
        os.makedirs(addons_dir)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            vpk_files = [f for f in zip_ref.namelist() if f.lower().endswith(".vpk")]

            if not vpk_files:
                return False, "No .vpk file found in the ZIP."

            for vpk_name in vpk_files:
                base_name = os.path.basename(vpk_name)
                name, ext = os.path.splitext(base_name)
                new_name = base_name
                count = 1

                # Avoid filename conflicts
                while os.path.exists(os.path.join(addons_dir, new_name)):
                    new_name = f"{name}_{count:02d}{ext}"
                    count += 1
                    if count > 99:
                        return False, "Too many conflicting .vpk files. Rename manually."

                # Extract the .vpk to the addons folder
                with zip_ref.open(vpk_name) as src, open(os.path.join(addons_dir, new_name), "wb") as dst:
                    shutil.copyfileobj(src, dst)

        # Update gameinfo.gi if needed
        required_block = """\
\t\t\t\t{
\t\t\t\t\tMod citadel
\t\t\t\t\tWrite citadel
\t\t\t\t\tGame citadel/addons
\t\t\t\t\tGame citadel
\t\t\t\t\tGame core
\t\t\t\t}
"""
        if os.path.exists(gameinfo_path):
            with open(gameinfo_path, "r", encoding="utf-8") as f:
                content = f.read()

            if "Game citadel/addons" not in content:
                new_content = replace_search_paths(content, required_block)
                with open(gameinfo_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
        else:
            return False, "gameinfo.gi not found. Please update manually."

        return True, "Mod installed successfully!"

    except zipfile.BadZipFile:
        return False, "Invalid ZIP file."
    except Exception as e:
        return False, f"Installation error: {str(e)}"

def replace_search_paths(content: str, replacement_block: str) -> str:
    import re
    pattern = r"(SearchPaths\s*{.*?})"
    new_content, count = re.subn(pattern, f"SearchPaths {replacement_block}", content, flags=re.DOTALL)
    if count == 0:
        new_content += f"\nSearchPaths {replacement_block}"
    return new_content

def find_deadlock_install_path() -> str | None:
    """
    Tries to locate Deadlock's install path from Steam.
    """
    steam_path = get_steam_path()
    if not steam_path:
        return None

    library_paths = get_steam_libraries(steam_path)
    for lib in library_paths:
        deadlock_path = os.path.join(lib, "steamapps", "common", "Deadlock")
        if os.path.isdir(deadlock_path):
            return deadlock_path

    return None

def get_steam_path() -> str | None:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
            value, _ = winreg.QueryValueEx(key, "SteamPath")
            return os.path.normpath(value)
    except Exception:
        return None

def get_steam_libraries(steam_path: str) -> list[str]:
    libraries = [os.path.join(steam_path)]
    vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")

    if not os.path.isfile(vdf_path):
        return libraries

    try:
        with open(vdf_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if '"' in line and ":" in line:
                parts = line.split('"')
                if len(parts) >= 5:
                    path = parts[3].replace("\\\\", "\\")
                    if os.path.isdir(path):
                        libraries.append(path)
    except Exception:
        pass

    return libraries
