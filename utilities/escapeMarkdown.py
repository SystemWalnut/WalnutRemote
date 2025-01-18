import re


escapedCharactersRegex = re.compile(r"([\\*_`\[\]()~>#+\-=|{}.!])")


def escape_markdown(string):
    return escapedCharactersRegex.sub(r"\\\1", str(string))
