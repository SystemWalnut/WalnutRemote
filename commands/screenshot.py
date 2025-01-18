import datetime
from io import BytesIO

from PIL import ImageGrab
from telegram import Update


async def screenshot(update: Update, context) -> None:
    await update.message.set_reaction(["👀"])
    try:
        screenshot = ImageGrab.grab()
        fileName = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M")
        memoryFile = BytesIO()
        memoryFile.name = f"{fileName}.png"
        screenshot.save(memoryFile, "PNG")
        memoryFile.seek(0)
        await update.message.reply_document(
            document=memoryFile,
            read_timeout=360,
            write_timeout=360,
        )
        await update.message.set_reaction(["👍"])
    except Exception:
        await update.message.set_reaction(["👎"])


commands = {
    "screenshot": screenshot,
}
