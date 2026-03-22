from compiler.lexer.tokens import Tokens
from compiler.codegen.value_json import make_variable


def detect_scope(token, context):
    if token.type == Tokens.LINE_VARIABLE:
        return "line"

    if token.type == Tokens.LOCAL_VARIABLE:
        return "local"

    if token.type == Tokens.GAME_VARIABLE:
        return "game"

    if token.type == Tokens.SAVE_VARIABLE:
        return "save"

    if token.type == Tokens.VARIABLE:
        if context == "event":
            return "local"
        if context in ("function", "process"):
            return "line"

    return "line"


def generate_variable(token, context):
    scope = detect_scope(token, context)
    return make_variable(token.value, scope)
