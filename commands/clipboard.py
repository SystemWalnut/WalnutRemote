import pyperclip
from telegram import Update

from walnut.utilities import parse_command


async def clipboard(update: Update, context) -> None:
    command = parse_command(update.message, ["content"], [None])
    if command.content is None:
        try:
            await update.message.reply_markdown_v2(pyperclip.paste())
            await update.message.set_reaction(["👍"])
        except:
            await update.message.set_reaction(["👎"])
    else:
        try:
            pyperclip.copy(command.content)
            await update.message.set_reaction(["👍"])
        except Exception:
            await update.message.set_reaction(["👎"])


commands = {
    "clipboard": clipboard,
}
