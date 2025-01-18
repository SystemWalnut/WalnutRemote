import ctypes
from ctypes import wintypes
from io import StringIO
from pathlib import Path

from cryptography.fernet import Fernet
from dotenv import dotenv_values

rootPath = Path(__file__).parent.absolute()
envPath = rootPath.joinpath("encrypted.env")
_keyPath = rootPath.parent.joinpath(".key")

if _keyPath.is_file() and _keyPath.exists():
    keyPath = _keyPath
else:
    buffer = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, 28, None, 0, buffer)
    keyPath = Path(buffer.value).joinpath("WALNUT", ".key")

fernet = Fernet(keyPath.read_bytes())
envFileContent = StringIO(fernet.decrypt(envPath.read_bytes()).decode())
envFileContent.seek(0)

env = dotenv_values(stream=envFileContent)
session = []
