import hashlib
import json
import time

import pyotp
from telegram import Update

from walnut.env import env, session
from walnut.utilities import get_special_folder, parse_command

totp = pyotp.TOTP(env["ADMIN_LOGIN_TOTP"])
dbAdmin = get_special_folder("walnut").joinpath("adminUsers")
dbBase = get_special_folder("walnut").joinpath("baseUsers")
dbAdmin.mkdir(parents=True, exist_ok=True)
dbBase.mkdir(parents=True, exist_ok=True)


async def start(update: Update, context):
    command = parse_command(
        update.message, ["action", "userid", "totp"], ["_", "_", "_"]
    )

    if not totp.verify(command.totp, valid_window=3):
        return None

    userHash = hashlib.md5(
        str(
            update.message.from_user.id if command.userid == "*" else command.userid
        ).encode()
    ).hexdigest()
    userHashAdminPath = dbAdmin.joinpath(userHash)
    userHashBasePath = dbBase.joinpath(userHash)
    currentTime = time.time()

    if command.action == "add":
        with userHashAdminPath.open("w") as userHashAdminFile:
            userHashAdminFile.write(str(currentTime))
        with userHashBasePath.open("w") as userHashBaseFile:
            userHashBaseFile.write(str(currentTime))
        session.append(update.message.from_user.id)
        await update.message.set_reaction(["🔥"])

    elif command.action == "remove":
        if update.message.from_user.id in session:
            session.remove(update.message.from_user.id)
        if userHashAdminPath.exists():
            userHashAdminPath.unlink()
        if userHashBasePath.exists():
            userHashBasePath.unlink()
        await update.message.set_reaction(["👍"])

    elif command.action == "check":
        status = dict(
            userId=(
                update.message.from_user.id if command.userid == "*" else command.userid
            ),
            admin=userHashAdminPath.exists(),
            base=userHashBasePath.exists(),
            userHash=userHash,
        )
        await update.message.reply_markdown_v2(
            f"```json\n{json.dumps(status, indent=2)}\n```"
        )
        await update.message.set_reaction(["👍"])

    else:
        await update.message.reply_text(
            "possible commands are 'add', 'restart', 'remove' and 'check'"
        )
        await update.message.set_reaction(["👎"])


commands = {
    "start": start,
}
