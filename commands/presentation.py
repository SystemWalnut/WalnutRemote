from telegram import Update
from telegram.constants import ParseMode

from walnut.tools import get_presentation
from walnut.utilities import escape_markdown


async def presentation(update: Update, context) -> None:
    presentations = get_presentation()
    message = f"> Sending {len(presentations):02} Files\n\n"
    for ppt in presentations:
        message += f"```text\n{escape_markdown(str(ppt))}\n```\n"
    await update.message.set_reaction(["👀"])
    await update.message.reply_markdown_v2(message)
    errorOccurred = False
    for ppt in presentations:
        try:
            with ppt.open("rb") as pptFile:
                caption = escape_markdown(str(ppt).replace("\\\\", "\\"))
                await update.message.reply_document(
                    document=pptFile,
                    caption=f"> {caption}",
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
        except Exception:
            errorOccurred = True
    if not errorOccurred:
        await update.message.set_reaction(["👍"])
    else:
        await update.message.set_reaction(["👎"])


commands = {
    "presentation": presentation,
}
