import os
import requests

API_BASE = "https://api.gamebanana.com/Core/Item/Data"

def is_gamebanana_url(url: str) -> bool:
    return "gamebanana.com/mods/" in url

def extract_mod_id(url: str) -> str | None:
    try:
        parts = url.rstrip('/').split('/')
        return parts[-1] if parts[-1].isdigit() else None
    except Exception:
        return None

def get_download_url(mod_id: str) -> tuple[str | None, str | None]:
    """
    Uses the GameBanana API to get the download URL from Files().aFiles().
    """
    fields = "Files().aFiles()"
    api_url = f"{API_BASE}?itemtype=Mod&itemid={mod_id}&fields={fields}"

    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            file_list = response.json()
            if isinstance(file_list, list) and len(file_list) > 0:
                first_entry = file_list[0]
                if isinstance(first_entry, dict):
                    # Get the inner dict from first key in the outer dict
                    inner_dict = next(iter(first_entry.values()), {})
                    return inner_dict.get("_sDownloadUrl"), inner_dict.get("_sFile")
    except Exception as e:
        print(f"Error fetching GameBanana mod info: {e}")

    return None, None

def download_zip_from_gamebanana(url: str, save_dir: str) -> str | None:
    """
    Given a GameBanana mod URL, attempts to download the mod ZIP to a specified directory.
    Returns the full path to the downloaded file or None on failure.
    """
    if not is_gamebanana_url(url):
        print("Invalid GameBanana URL.")
        return None

    mod_id = extract_mod_id(url)
    if not mod_id:
        print("Could not extract mod ID from URL.")
        return None

    download_url, file_name = get_download_url(mod_id)
    if not download_url:
        print("Could not get a valid download URL from GameBanana API.")
        return None

    try:
        os.makedirs(save_dir, exist_ok=True)
        local_filename = os.path.join(save_dir, file_name or f"mod_{mod_id}.zip")
        with requests.get(download_url, stream=True) as r:
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return local_filename
    except Exception as e:
        print(f"Failed to download ZIP: {e}")
        return None
