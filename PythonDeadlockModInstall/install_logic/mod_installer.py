import os
import zipfile
import shutil
import winreg
import json
import rarfile
import py7zr
import re


# ---------------------- Archive Extraction ----------------------
def extract_supported_archive(archive_path: str, extract_to: str) -> list[str]:
    extracted_files = []
    if archive_path.endswith(".zip"):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            extracted_files = zip_ref.namelist()
    elif archive_path.endswith(".rar"):
        with rarfile.RarFile(archive_path, 'r') as rar_ref:
            rar_ref.extractall(extract_to)
            extracted_files = rar_ref.namelist()
    elif archive_path.endswith(".7z"):
        with py7zr.SevenZipFile(archive_path, mode='r') as seven_z:
            seven_z.extractall(path=extract_to)
            extracted_files = [f for f in seven_z.getnames()]
    else:
        raise ValueError("Unsupported archive format")
    return extracted_files


# ---------------------- Mod Installation ----------------------
def install_mod_zip(zip_path: str, deadlock_root: str, confirm_overwrite_callback=None) -> tuple[bool, str]:
    if not zip_path.lower().endswith((".zip", ".rar", ".7z")):
        return False, "Unsupported archive format. Please use .zip, .rar, or .7z."

    citadel_dir = os.path.join(deadlock_root, "game", "citadel")
    addons_dir = os.path.join(citadel_dir, "addons")
    gameinfo_path = os.path.join(citadel_dir, "gameinfo.gi")
    mods_meta_path = os.path.join(addons_dir, "installed_mods.json")

    os.makedirs(addons_dir, exist_ok=True)
    temp_extract_path = os.path.join(addons_dir, "_temp_extract")
    if os.path.exists(temp_extract_path):
        shutil.rmtree(temp_extract_path)
    os.makedirs(temp_extract_path)

    try:
        extracted_files = extract_supported_archive(zip_path, temp_extract_path)
        vpk_files = [f for f in extracted_files if f.lower().endswith(".vpk")]
        if not vpk_files:
            return False, "No .vpk file found in the archive."

        mod_name = os.path.splitext(os.path.basename(zip_path))[0]
        installed_files = []

        mods_meta = {}
        if os.path.exists(mods_meta_path):
            with open(mods_meta_path, "r", encoding="utf-8") as f:
                mods_meta = json.load(f)

        if mod_name in mods_meta and confirm_overwrite_callback:
            if not confirm_overwrite_callback(mod_name):
                return False, f"Mod '{mod_name}' is already installed and was not overwritten."
            for old_file in mods_meta[mod_name]:
                old_path = os.path.join(addons_dir, old_file)
                if os.path.exists(old_path):
                    os.remove(old_path)

        for vpk_name in vpk_files:
            vpk_path = os.path.join(temp_extract_path, vpk_name)
            if not os.path.isfile(vpk_path):
                continue
            base_name = os.path.basename(vpk_name)
            name, ext = os.path.splitext(base_name)
            new_name = base_name
            count = 1
            while os.path.exists(os.path.join(addons_dir, new_name)):
                new_name = f"{name}_{count:02d}{ext}"
                count += 1
                if count > 99:
                    return False, "Too many conflicting .vpk files. Rename manually."
            shutil.copyfile(vpk_path, os.path.join(addons_dir, new_name))
            installed_files.append(new_name)

        shutil.rmtree(temp_extract_path)
        mods_meta[mod_name] = installed_files
        with open(mods_meta_path, "w", encoding="utf-8") as f:
            json.dump(mods_meta, f, indent=2)

        required_block = """                {
                    Mod citadel
                    Write citadel
                    Game citadel/addons
                    Game citadel
                    Game core
                }
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
    finally:
        if os.path.exists(temp_extract_path):
            shutil.rmtree(temp_extract_path)


# ---------------------- Mod Removal ----------------------
def remove_mod(mod_name: str, deadlock_root: str) -> tuple[bool, str]:
    citadel_dir = os.path.join(deadlock_root, "game", "citadel")
    addons_dir = os.path.join(citadel_dir, "addons")
    mods_meta_path = os.path.join(addons_dir, "installed_mods.json")

    if not os.path.exists(mods_meta_path):
        return False, "No mod metadata found. Cannot remove mod."

    try:
        with open(mods_meta_path, "r", encoding="utf-8") as f:
            mods_meta = json.load(f)

        if mod_name not in mods_meta:
            return False, f"Mod '{mod_name}' not found in metadata."

        for filename in mods_meta[mod_name]:
            path = os.path.join(addons_dir, filename)
            if os.path.exists(path):
                os.remove(path)

        del mods_meta[mod_name]

        with open(mods_meta_path, "w", encoding="utf-8") as f:
            json.dump(mods_meta, f, indent=2)

        return True, f"Mod '{mod_name}' removed successfully."

    except Exception as e:
        return False, f"Removal error: {str(e)}"


# ---------------------- Helpers ----------------------
def replace_search_paths(content: str, replacement_block: str) -> str:
    pattern = r"(SearchPaths\\s*{.*?})"
    new_content, count = re.subn(pattern, f"SearchPaths {replacement_block}", content, flags=re.DOTALL)
    if count == 0:
        new_content += f"\nSearchPaths {replacement_block}"
    return new_content


def check_duplicate_mods(mod_name: str, deadlock_root: str) -> bool:
    addons_dir = os.path.join(deadlock_root, "game", "citadel", "addons")
    mods_meta_path = os.path.join(addons_dir, "installed_mods.json")

    if not os.path.exists(mods_meta_path):
        return False

    try:
        with open(mods_meta_path, "r", encoding="utf-8") as f:
            mods_meta = json.load(f)
        return mod_name in mods_meta
    except Exception:
        return False


# ---------------------- Steam Integration ----------------------
def get_steam_path() -> str | None:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Valve\\Steam") as key:
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


def find_deadlock_install_path() -> str | None:
    steam_path = get_steam_path()
    if not steam_path:
        return None

    library_paths = get_steam_libraries(steam_path)
    for lib in library_paths:
        deadlock_path = os.path.join(lib, "steamapps", "common", "Deadlock")
        if os.path.isdir(deadlock_path):
            return deadlock_path

    return None
