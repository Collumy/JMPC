import re

ANSI = {
    "&0": "\033[30m",
    "&1": "\033[34m",
    "&2": "\033[32m",
    "&3": "\033[36m",
    "&4": "\033[31m",
    "&5": "\033[35m",
    "&6": "\033[33m",
    "&7": "\033[37m",
    "&8": "\033[90m",
    "&9": "\033[94m",
    "&a": "\033[92m",
    "&b": "\033[96m",
    "&c": "\033[91m",
    "&d": "\033[95m",
    "&e": "\033[93m",
    "&f": "\033[97m",
    "&r": "\033[0m",
}


def minecraft_color(text: str) -> str:
    """Преобразует Minecraft-коды (&c, &e, &#FF0000) в ANSI-цвета."""

    # hex цвета: &#RRGGBB
    def hex_repl(match):
        hex_color = match.group(1)
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"\033[38;2;{r};{g};{b}m"

    # заменяем hex
    text = re.sub(r"&#([0-9A-Fa-f]{6})", hex_repl, text)

    # заменяем обычные цвета
    for code, ansi in ANSI.items():
        text = text.replace(code, ansi)

    return text + "\033[0m"