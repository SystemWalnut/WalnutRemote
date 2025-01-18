import ctypes
from ctypes import wintypes
from pathlib import Path

folderMapping = {
    "desktop": 0,
    "documents": 5,
    "appdata": 26,
    "local_appdata": 28,
}


def check_special_folder(id):
    buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, id, None, 0, buf)
    return buf.value

def get_special_folder(id: str) -> Path:
    if id.lower() == "walnut":
        _walnut = get_special_folder("local_appdata").joinpath("WALNUT").absolute()
        _walnut.mkdir(parents=True, exist_ok=True)
        return _walnut
    return Path(check_special_folder(folderMapping.get(id.lower()))).absolute()