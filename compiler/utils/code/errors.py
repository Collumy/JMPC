from dataclasses import dataclass
from .colors import minecraft_color
from difflib import get_close_matches

@dataclass
class ErrorToken:
    line: int
    column: int


class CompileError(Exception):
    def __init__(self, message, line, column, length, source_line):
        self.message = message
        self.line = line
        self.column = column
        self.length = length
        self.source_line = source_line
        super().__init__(self.format())

    def format(self):
        # Стрелочки под ошибкой
        pointer = "&8" + "~" * (self.column-self.length) + "&c" + "^" * max(1, self.length)

        msg = (
            f"\n&c☠  Ошибка во {self.line} строке {self.column} символе &8({self.line}:{self.column})"
            f"\n&#FFD3D3 » {self.message}"
            f"\n&#FFEEC4{self.source_line}"
            f"\n{pointer}\n"
        )

        return minecraft_color(msg)



def error(node, message: str):
    if hasattr(node, "current"):
        token = node.current
        parser = node
    elif hasattr(node, "token"):
        token = node.token
        parser = node.parser if hasattr(node, "parser") else None
    else:
        token = node
        parser = node.parser if hasattr(node, "parser") else None
    
    if token is None:
        raise CompileError(
            message=message,
            line=0,
            column=0,
            length=1,
            source_line="(конец файла или внутренняя ошибка)"
        )
    
    length = token_length(token)
    
    line = token.line if hasattr(token, "line") else 0
    column = token.column if hasattr(token, "column") else 0

    raise CompileError(
        message=message,
        line=line,
        column=column,
        length=length,
        source_line=parser.get_line(line) if parser and hasattr(parser, "get_line") else ""
    )

def token_length(token):
    if token is None:
        return 1
    
    # 1. Если есть value и это строка
    if hasattr(token, "value") and isinstance(token.value, str):
        return len(token.value)

    # 2. Если есть raw текст токена
    if hasattr(token, "raw") and isinstance(token.raw, str):
        return len(token.raw)

    # 3. Если есть text
    if hasattr(token, "text") and isinstance(token.text, str):
        return len(token.text)

    # 4. Если есть literal (например строка)
    if hasattr(token, "literal") and isinstance(token.literal, str):
        return len(token.literal)

    return 1




from compiler.data.data_loader import load_json

ACTIONS1 = load_json("actions.json")
ACTIONS = [a["name"] for a in ACTIONS1]

def check_method(parser, method, methods = False):
    if methods: check = methods
    else: check = ACTIONS

    if method not in check:
        suggestions = get_close_matches(method, check, 5, 0.3)
        msg = f"Действие {method} не найдено"

        if suggestions:
            msg += "\nВозможно, вы имели в виду:\n"
            for s in suggestions: msg += f"   - {s}\n"

        error(parser, msg)