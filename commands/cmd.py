import queue

from command_runner import command_runner_threaded
from telegram import Update
from telegram.constants import ParseMode

from walnut.utilities import escape_markdown, parse_command


async def cmd(update: Update, context) -> None:
    command = parse_command(update.message, ["cmd"], [None])
    cmdOutput = None
    currentIndex = 0
    currentOutput = ""

    async def callback_function(string):
        nonlocal cmdOutput, currentOutput
        currentOutput += str(string)
        newMessage = ""
        for cmd, output in sessionOutput:
            if output != "":
                newMessage += f"> {escape_markdown(cmd)}\n"
                newMessage += f"```text\n{escape_markdown(output)}\n```\n"
        newMessage += f"> {escape_markdown(sessionOutput[currentIndex][0])}\n"
        newMessage += f"```text\n{escape_markdown(currentOutput)}\n```\n"
        await cmdOutput.edit_text(newMessage, parse_mode=ParseMode.MARKDOWN_V2)

    if command.cmd is None:
        await update.message.set_reaction(["👎"])
        await update.message.reply_text("No Command Provided...")
        return None

    cmdScript = filter(lambda _: _, map(lambda _: _.strip(), command.cmd.split("\n")))
    sessionOutput = [[cmd, ""] for cmd in cmdScript]

    await update.message.set_reaction(["👀"])

    for index, cmd in enumerate(sessionOutput):

        if cmdOutput is None:
            tempMessage = escape_markdown(sessionOutput[index][0])
            cmdOutput = await update.message.reply_markdown_v2(f"> {tempMessage}")
        else:
            currentMessage = ""
            for session in sessionOutput:
                if session[1] != "":
                    currentMessage += f"> {escape_markdown(session[0])}\n"
                    currentMessage += f"```text\n{escape_markdown(session[1])}\n```\n"
            await cmdOutput.edit_text(
                currentMessage + f"> {escape_markdown(sessionOutput[index][0])}\n",
                parse_mode=ParseMode.MARKDOWN_V2,
            )

        currentIndex = index
        outputQueue = queue.Queue()
        threadResult = command_runner_threaded(
            cmd[0],
            stdout=outputQueue,
            shell=True,
            silent=True,
            method="poller",
            check_interval=0.8,
            priority="high",
            timeout=120,
        )

        readQueue = True
        while readQueue:
            try:
                currentLine = outputQueue.get(timeout=0.1)
            except queue.Empty:
                pass
            else:
                if currentLine is None:
                    readQueue = False
                else:
                    await callback_function(currentLine)

        currentOutput = ""
        _, output = threadResult.result()
        sessionOutput[index][1] = output

    await update.message.set_reaction(["👍"])


commands = {
    "cmd": cmd,
}
