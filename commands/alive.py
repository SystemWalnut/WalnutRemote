from telegram import Update

from walnut.utilities import parse_command


async def alive(update: Update, context) -> None:
    command = parse_command(update.message)

    await update.message.set_reaction(["👍"])
    pythonString = ""
    for key, value in command._asdict().items():
        value = str(value)
        if "\n" in value:
            value = value.replace("'''", "\\'''")
            pythonString += f"{key} = '''{value}'''\n"
        else:
            value = value.replace("'", "\\'")
            pythonString += f"{key} = '{value}'\n"
    await update.message.reply_markdown_v2(f"```python\n{pythonString.strip()}\n```")


commands = {
    "alive": alive,
}
