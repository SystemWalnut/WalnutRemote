import asyncio
import subprocess

from telegram import Update

from walnut.utilities import parse_command


async def workstation(update: Update, context) -> None:
    command = parse_command(update.message, ["command", "duration"], ["_", ""])
    action = command.command.lower().strip()
    duration = command.duration.lower().strip()
    if duration == "":
        duration = "1"

    async def run_cmd_and_respond_status(cmd):
        process = await asyncio.create_subprocess_exec(
            *cmd,
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.wait()

        if process.returncode == 0:
            await update.message.set_reaction(["👍"])
        else:
            await update.message.set_reaction(["👎"])

    if action == "shutdown":
        if duration == "0" or duration == "1":
            await run_cmd_and_respond_status(["shutdown", "/p", "/f"])
        else:
            await run_cmd_and_respond_status(["shutdown", "/s", "/t", duration])
    elif action == "restart":
        await run_cmd_and_respond_status(["shutdown", "/r", "/t", duration])
    elif action == "logoff":
        await run_cmd_and_respond_status(["shutdown", "/l"])
    elif action == "hibernate":
        await run_cmd_and_respond_status(["shutdown", "/h"])
    elif action == "lock":
        await run_cmd_and_respond_status(
            ["rundll32.exe", "user32.dll", "LockWorkStation"]
        )
    elif action == "abort":
        await run_cmd_and_respond_status(["shutdown", "/a"])
    else:
        await update.message.reply_text(
            "possible commands are 'shutdown', 'restart', 'logoff', 'lock' and 'abort'"
        )
        await update.message.set_reaction(["👎"])


commands = {
    "workstation": workstation,
}
