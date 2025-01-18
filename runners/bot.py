import datetime
import hashlib
import time
from collections import defaultdict
from io import BytesIO

import pyotp
from PIL import ImageGrab
from telegram import Update
from telegram.ext import Application, CommandHandler

from walnut.env import env
from walnut.utilities import get_special_folder, parse_command

totp = pyotp.TOTP(env["BASE_LOGIN_TOTP"])
db = get_special_folder("walnut").joinpath("baseUsers")
db.mkdir(parents=True, exist_ok=True)
session = []
coolDown = defaultdict(lambda: 0)


async def start(update: Update, context):
    command = parse_command(update.message, ["totp"], ["_"])

    if command.totp == "*":
        userHash = hashlib.md5(str(update.message.from_user.id).encode()).hexdigest()
        userHashFile = db.joinpath(userHash)
        if userHashFile.exists():
            userHashFile.unlink()
            if update.message.from_user.id in session:
                session.remove(update.message.from_user.id)
            await update.message.set_reaction(["👍"])
    elif totp.verify(command.totp, valid_window=3):
        userHash = hashlib.md5(str(update.message.from_user.id).encode()).hexdigest()
        userHashFile = db.joinpath(userHash).open("w")
        userHashFile.write(str(time.time()))
        userHashFile.close()
        await update.message.set_reaction(["🔥"])


async def screenshot(update: Update, context) -> None:
    currentTime = time.time()

    if not update.message.from_user.id in session:
        userHash = hashlib.md5(str(update.message.from_user.id).encode()).hexdigest()
        userHashFile = db.joinpath(userHash)
        if not userHashFile.exists():
            return None
        else:
            lastAccess = float(userHashFile.read_text())
            if (currentTime - lastAccess) > (7 * 24 * 60 * 60):
                userHashFile.unlink()
                await update.message.set_reaction(["🤮"])
                return None
            session.append(update.message.from_user.id)
            with userHashFile.open("w") as _userHashFile:
                _userHashFile.write(str(currentTime))

    if (currentTime - coolDown[update.message.from_user.id]) < 5:
        await update.message.reply_markdown_v2("> CoolDown: try after few seconds\\.")
        return None

    try:
        await update.message.set_reaction(["👀"])
        screenshot = ImageGrab.grab()
        fileName = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M")
        memoryFile = BytesIO()
        memoryFile.name = f"{fileName}.png"
        screenshot.save(memoryFile, "PNG")
        memoryFile.seek(0)
        await update.message.reply_document(document=memoryFile)
        await update.message.set_reaction(["👍"])
        coolDown[update.message.from_user.id] = time.time()
    except Exception:
        await update.message.set_reaction(["👎"])


async def startup(self):
    await self.bot.sendMessage(int(env["DEVELOPER_TELEGRAM_ID"]), "#systemOnline")


def main() -> None:
    application = Application.builder().token(env["BASE_TELEGRAM_BOT_TOKEN"]).build()

    application.post_init = startup

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("screenshot", screenshot))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
