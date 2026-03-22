from compiler.utils.code.errors import error, check_method
from compiler.parser.expressions.info import SELECTORS
from compiler.lexer.tokens import Tokens
from compiler.data.data_loader import load_json

# Загружаем реальные действия
ACTIONS1 = load_json("actions.json")
ACTIONS = {a["name"]: {"id": a["id"], "values": a["args"]} for a in ACTIONS1}

# Реестр кастомных действий
CUSTOM_ACTIONS = {}

def parse_define(parser):
    parser.eat(Tokens.DEFINE)
    if parser.current.type != Tokens.VARIABLE: error(parser, "Ожидалось имя кастомного действия")
    name = parser.current.value
    parser.eat(Tokens.VARIABLE)

    # = или as
    if (parser.current.type == Tokens.ASSIGN): parser.eat(Tokens.ASSIGN)
    elif (parser.current.type == Tokens.VARIABLE and parser.current.value == "as"): parser.eat(Tokens.VARIABLE)
    else: error(parser, "Ожидался = или as")

    # target. (player/entity/world/variable)
    if parser.current.value not in SELECTORS: error(parser, "Ожидался объект (player/entity/world/variable)")
    target = SELECTORS[parser.current.value]
    parser.eat(parser.current.type)
    if parser.current.type != Tokens.DOT: error(parser, "Ожидался '.' после объекта")
    parser.eat(Tokens.DOT)

    # имя метода
    method = parser.current.value
    check_method(parser, method)
    parser.eat(parser.current.type)

    arg_metas = ACTIONS[method]["values"]

    # сохраняем кастомное действие
    CUSTOM_ACTIONS[name] = {
        "target": target,
        "method": method,
        "args": arg_metas
    }

    return None