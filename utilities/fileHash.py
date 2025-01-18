import hashlib
from pathlib import Path

def _sha256sum(filePath):
    hash  = hashlib.sha256()
    byteSize  = bytearray(128*1024)
    mv = memoryview(byteSize)
    with Path(filePath).open(mode='rb', buffering=0) as f:
        while n := f.readinto(mv):
            hash.update(mv[:n])
    return hash.hexdigest()

def calculate_file_hash(filePath):
    return _sha256sum(filePath)