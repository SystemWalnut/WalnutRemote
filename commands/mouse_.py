import json
import time

import mouse
from screeninfo import get_monitors
from telegram import Update

from walnut.utilities import escape_markdown, parse_command


async def mouse_(update: Update, context) -> None:
    command = parse_command(update.message, ["command", "combination"], ["_", ""])
    action = command.command.lower().strip()
    combination = command.combination.lower().strip()

    async def success():
        await update.message.set_reaction(["👍"])

    async def split_in_numbers(combination: str, splits: int = None):
        numbers = list(map(float, combination.replace(",", " ").split(" ")))
        if splits is None:
            return numbers
        numbers.extend([0] * splits)
        return numbers[:splits]

    if action == "click":
        mouse.click(combination)
        await success()
    elif action in ("double_click", "2click", "doubleclick"):
        mouse.double_click(combination)
        await success()
    elif action in ("right_click", "rclick", "rightclick"):
        mouse.right_click()
        await success()
    elif action == "scroll":
        steps = int(float(combination))
        durationGap = 1 / steps
        for _ in range(steps):
            mouse.wheel(1)
            time.sleep(durationGap)
        await success()
    elif action == "move":
        mouse.move(*await split_in_numbers(combination, 2), duration=0.5)
        await success()
    elif action == "drag":
        mouse.drag(*await split_in_numbers(combination, 4), duration=0.5)
        await success()
    elif action == "position":
        mouseX, mouseY = mouse.get_position()
        await update.message.reply_markdown_v2(
            "> " + escape_markdown(f"(x: {mouseX}, y: {mouseY})")
        )
        await success()
    elif action == "screen":
        message = ""
        for monitor in get_monitors():
            message += (
                "```json\n"
                + json.dumps(
                    dict(
                        name=monitor.name,
                        width=monitor.width,
                        height=monitor.height,
                        primary=monitor.is_primary,
                    ),
                    indent=2,
                )
                + "\n```\n"
            )
        await update.message.reply_markdown_v2(message)
        await success()
    else:
        await update.message.reply_text(
            "possible commands are 'click', 'double_click', 'right_click', 'scroll', 'move', 'drag', 'position' and 'screen'"
        )
        await update.message.set_reaction(["👎"])


commands = {
    "mouse": mouse_,
}
