from walnut.commands.alive import commands as aliveCommands
from walnut.commands.browser import commands as browserCommands
from walnut.commands.clipboard import commands as clipboardCommands
from walnut.commands.cmd import commands as cmdCommands
from walnut.commands.keyboard_ import commands as keyboardCommands
from walnut.commands.mouse_ import commands as mouseCommands
from walnut.commands.presentation import commands as presentationCommands
from walnut.commands.screenshot import commands as screenshotCommands
from walnut.commands.start import commands as startCommands
from walnut.commands.workstation import commands as workstationCommands


_commands = [
    aliveCommands,
    browserCommands,
    clipboardCommands,
    cmdCommands,
    keyboardCommands,
    mouseCommands,
    presentationCommands,
    screenshotCommands,
    startCommands,
    workstationCommands,
]
commands = dict(sum(map(lambda _: list(_.items()), _commands), []))
