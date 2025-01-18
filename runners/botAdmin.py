import functools
import hashlib
import time

from telegram import Update
from telegram.ext import Application, CommandHandler

from walnut.commands import commands
from walnut.env import env, session
from walnut.utilities import get_special_folder

db = get_special_folder("walnut").joinpath("adminUsers")


async def wrapper(wrappingFunctionName, wrappingFunction, update: Update, context):
    if not update.message.from_user.id in session and wrappingFunctionName != "start":
        currentTime = time.time()
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
    try:
        return await wrappingFunction(update, context)
    except Exception:
        pass

async def startup(self):
    await self.bot.sendMessage(int(env["DEVELOPER_TELEGRAM_ID"]), '#systemOnline')


def main() -> None:
    print("here-2")
    application = (
        Application.builder()
        .token(env["ADMIN_TELEGRAM_BOT_TOKEN"])
        .concurrent_updates(True)
        .build()
    )

    application.post_init = startup

    for commandName, commandFunction in commands.items():
        application.add_handler(
            CommandHandler(
                commandName,
                functools.partial(wrapper, commandName, commandFunction),
                block=False,
            )
        )

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
