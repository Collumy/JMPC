from compiler.lexer.tokens import Tokens
from compiler.parser.expressions.expressions import parse_expression
from compiler.utils.errors import error
from compiler.ast.node import Action, Argument
from compiler.ast.expressions import TypeVariable
from compiler.parser.expressions.info import VARIABLES, SELECTORS, ENTITY_SELECTION, PLAYER_SELECTION

from compiler.data_loader import load_json
from compiler.parser.core.parse_args import parse_all_arguments
from compiler.utils.define import CUSTOM_ACTIONS

from difflib import get_close_matches

ACTIONS1 = load_json("actions.json")
ACTIONS = {a["name"]: {"id": a["id"], "values": a["args"]} for a in ACTIONS1}


def parse_action(parser, iscustom=False):

    if iscustom:
        parser.eat(Tokens.VARIABLE)
        parser.eat(Tokens.COLON)


    assigned_vars = []

    if parser.current.type in VARIABLES and not iscustom:
        while parser.current.type != Tokens.ASSIGN:
            token = parser.current
            if token.type not in VARIABLES:
                error(parser, "Ожидалась переменная перед '='")

            assigned_vars.append(TypeVariable(token))
            parser.eat(token.type)

            if parser.current.type == Tokens.COMMA:
                parser.eat(Tokens.COMMA)
                continue
            if parser.current.type == Tokens.ASSIGN:
                break

            error(parser, "Ожидалась ',' или '='")

        parser.eat(Tokens.ASSIGN)


    is_dot_syntax = False
    first_var_arg = None
    selection = None


    # dot‑syntax: variable.method(...)
    if parser.current.type != Tokens.SELECTOR and not iscustom:
        first_var_arg = parse_expression(parser)

        if parser.current.type != Tokens.DOT:
            error(parser, "Ожидалась точка для вызова метода")
        parser.eat(Tokens.DOT)

        is_dot_syntax = True
        target = "variable"


    # selector::method
    if not is_dot_syntax and not iscustom:
        if parser.current.value not in SELECTORS:
            error(parser, f"Ожидался объект (player/entity/world/code/variable), получено: {parser.current}")

        target_token = parser.current.type
        target = SELECTORS.get(target_token, parser.current.value)

        parser.eat(parser.current.type)
        parser.eat(Tokens.DOUBLE_COLON)


    # Имя действия
    name = parser.current.value
    if iscustom:
        custom = CUSTOM_ACTIONS[name]
        target = custom["target"]
        name = custom["method"]


    if name not in ACTIONS:
        suggestions = get_close_matches(name, ACTIONS.keys(), 5, 0.3)
        msg = f"Действие {name} не найдено"

        if suggestions:
            msg += "\nВозможно, вы имели в виду:\n"
            for s in suggestions: msg += f"   - {s}\n"

        error(parser, msg)

    method = ACTIONS[name]["id"]
    arg_metas = ACTIONS[name]["values"]

    parser.eat(parser.current.type)


    # Селектор <all> / <nearest> / <random>
    if parser.current.type == Tokens.LESS:
        if target not in ("player", "entity"):
            error(parser, "Этот объект не поддерживает селекторы")

        parser.eat(Tokens.LESS)

        if parser.current.type != Tokens.VARIABLE:
            error(parser, "Ожидалось имя селектора")

        selection = parser.current.value
        parser.eat(Tokens.VARIABLE)

        if parser.current.type != Tokens.GREATER:
            error(parser, "Ожидался '>' после селектора")
        parser.eat(Tokens.GREATER)

        if target == "player":
            if selection not in PLAYER_SELECTION:
                error(parser, f"Неизвестный селектор <{selection}>")
            selection = PLAYER_SELECTION[selection]

        if target == "entity":
            if selection not in ENTITY_SELECTION:
                error(parser, f"Неизвестный селектор <{selection}>")
            selection = ENTITY_SELECTION[selection]
    
    extra = {
        "first_non_variables": [],
        "first_variables": []
    }

    if is_dot_syntax and first_var_arg is not None:
        extra["first_non_variables"].append(first_var_arg)

    for var in assigned_vars:
        extra["first_variables"].append(var)



    args = parse_all_arguments(parser, arg_metas, method, extra)


    # Вставляем объект из dot‑syntax как аргумент
    if is_dot_syntax and first_var_arg is not None:
        # Находим первый аргумент, который НЕ type="variable"
        first_non_variable_id = None
        for meta in arg_metas:
            if meta.get("type") != "variable":
                first_non_variable_id = meta["id"]
                break

        if first_non_variable_id is not None:
            already_set = any(a.name == first_non_variable_id for a in args)
            if not already_set:
                args.insert(0, Argument(first_non_variable_id, first_var_arg))


    result_slots = [meta["id"] for meta in arg_metas if meta.get("type") == "result" or "variable"]

    if len(assigned_vars) > len(result_slots):
        error(
            parser,
            f"Слишком много переменных слева от '=', метод '{name}' возвращает только {len(result_slots)} знач."
        )

    for var, slot in zip(assigned_vars, result_slots):
        already_set = any(a.name == slot for a in args)
        if not already_set:
            args.append(Argument(slot, var))

    return Action(target, method, args, selection)