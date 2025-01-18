import json
import re
from collections import namedtuple

import yaml

codeBlockRegex = re.compile(
    r"^(/[a-zA-Z0-9_]+)[\n|\s]+```(?P<language>[a-zA-Z]+\n)?(?P<code>.*?)```[\n|\s]{0,}$",
    re.DOTALL,
)
singleLineRegex = re.compile(r"([^\s~]+|`[^`]*`)")


def parse_command(
    message, sequence: list = [], defaults: list = [], *, multiline=False
):
    messageMarkdown = str(message.text_markdown_v2)
    messageText = str(message.text)
    codeBlockMatch = codeBlockRegex.match(messageMarkdown)
    outputTuple = namedtuple(
        "Command", sequence or ["command"], defaults=defaults or [None]
    )

    if codeBlockMatch:
        blockLanguage = codeBlockMatch.group("language").strip().lower()
        blockCode = codeBlockMatch.group("code").strip()
        if blockLanguage == "json":
            return outputTuple(**json.loads(blockCode))
        elif blockLanguage == "yaml" or blockLanguage == "yml":
            return outputTuple(**yaml.load(blockCode))
        else:
            return outputTuple(blockCode)

    if not multiline:
        messageText = messageText.replace("\n", " ")

    if len(sequence) <= 1:
        messageSplit = messageText.split(" ", 1)
        if len(messageSplit) != 1:
            return outputTuple(messageSplit[-1].strip())
        else:
            return outputTuple(None)

    messageSplit = list(
        filter(
            lambda _: _,
            list(map(lambda _: _.strip("`"), singleLineRegex.findall(messageText))),
        )
    )

    messageSplit = messageSplit[1 : len(sequence)] + [
        " ".join(messageSplit[len(sequence) :])
    ]

    return outputTuple(*list(messageSplit))
