import keyboard
from telegram import Update

from walnut.utilities import parse_command


async def keyboard_(update: Update, context) -> None:
    command = parse_command(update.message, ["command", "combination"], ["_", ""])

    if command.combination.strip() == "":
        await update.message.reply_text("a combination is required to act")
        await update.message.set_reaction(["👎"])
        return None

    if command.command.lower() == "press":
        keyboard.press_and_release(command.combination)
        await update.message.set_reaction(["👍"])
    elif command.command.lower() == "write":
        keyboard.write(command.combination)
        await update.message.set_reaction(["👍"])
    else:
        await update.message.reply_text("possible commands are 'write' and 'press'")
        await update.message.set_reaction(["👎"])


commands = {
    "keyboard": keyboard_,
}
