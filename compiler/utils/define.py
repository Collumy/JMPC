from compiler.utils.errors import error
from compiler.parser.expressions.info import SELECTORS
from compiler.lexer.tokens import Tokens
from compiler.data_loader import load_json

# Загружаем реальные действия
ACTIONS1 = load_json("actions.json")
ACTIONS = {a["name"]: {"id": a["id"], "values": a["args"]} for a in ACTIONS1}

# Реестр кастомных действий
CUSTOM_ACTIONS = {}


def parse_define(parser):

    # define
    parser.eat(Tokens.DEFINE)

    # имя кастомного действия
    if parser.current.type != Tokens.VARIABLE:
        error(parser, "Ожидалось имя кастомного действия")

    name = parser.current.value
    parser.eat(Tokens.VARIABLE)

    # =
    parser.eat(Tokens.ASSIGN)

    # target (player/entity/world/variable)
    if parser.current.value not in SELECTORS:
        error(parser, "Ожидался объект (player/entity/world/variable)")

    target_token = parser.current.value
    target = SELECTORS[target_token]
    parser.eat(parser.current.type)

    # ::
    if parser.current.type != Tokens.DOUBLE_COLON:
        error(parser, "Ожидался '::' после объекта")
    parser.eat(Tokens.DOUBLE_COLON)

    # имя метода
    method = parser.current.value
    parser.eat(parser.current.type)

    # проверяем, что метод существует
    if method not in ACTIONS:
        error(parser, f"Действие '{method}' не найдено")

    arg_metas = ACTIONS[method]["values"]

    # сохраняем кастомное действие
    CUSTOM_ACTIONS[name] = {
        "target": target,
        "method": method,
        "args": arg_metas
    }

    return None