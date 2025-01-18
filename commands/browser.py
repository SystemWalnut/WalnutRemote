import webbrowser

from telegram import Update

from walnut.utilities import parse_command


async def browser(update: Update, context) -> None:
    command = parse_command(update.message, ["url"], [None])
    if command.url is None:
        await update.message.reply_markdown_v2("> No URL provided")
        await update.message.set_reaction(["👎"])
    elif not command.url.startswith(("http:", "https:")):
        webbrowser.open(f"https://google.com/search?q={command.url}")
        await update.message.set_reaction(["👍"])
    else:
        webbrowser.open(command.url)
        await update.message.set_reaction(["👍"])


commands = {
    "browser": browser,
}
