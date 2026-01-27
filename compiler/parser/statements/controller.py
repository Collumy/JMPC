from compiler.lexer.tokens import Tokens
from compiler.ast.node import Action, Controller
from compiler.parser.core.parse_args import parse_all_arguments
from compiler.parser.core.operations import parse_body
from compiler.utils.errors import error


CONTROLLER_ACTIONS = {
    "async_run": {
        "action": "controller_async_run",
        "aliases": ["async_run", "async"],
        "args": []
    },

    "do_not_run": {
        "action": "controller_do_not_run",
        "aliases": ["do_not_run", "skip"],
        "args": []
    },

    "exception": {
        "action": "controller_exception",
        "aliases": ["exception", "catch_error", "catch"],
        "args": [
            {"id": "variable", "type": "variable"}
        ]
    },

    "measure_time": {
        "action": "controller_measure_time",
        "aliases": ["measure_time", "time", "measure"],
        "args": [
            {"id": "variable", "type": "variable"},
            {"id": "duration", "type": "enum", "values": ["MICROSECONDS", "MILLISECONDS", "NANOSECONDS"]}
        ]
    }
}


def parse_controller(parser):
    parser.eat(Tokens.CONTROLLER)

    word = parser.current.value

    matched = None
    for meta in CONTROLLER_ACTIONS.values():
        if word in meta["aliases"]:
            matched = meta
            break

    if matched is None: error(parser, f"Неизвестное controller-действие: '{word}'")
    method = matched["action"]

    parser.eat(Tokens.IDENTIFIER)

    # controller action(...)
    args = []
    if "args" in matched and matched["args"]:
        args = parse_all_arguments(parser, matched["args"], method)
    else:
        # если нет аргументов, всё равно должны съесть ()
        if parser.current.type == Tokens.LPAREN:
            parser.eat(Tokens.LPAREN)
            if parser.current.type != Tokens.RPAREN:
                error(parser, f"{word}() не принимает аргументов")
            parser.eat(Tokens.RPAREN)

    if parser.current.type != Tokens.COLON:error(parser, "Ожидался ':' после controller-действия")
    parser.eat(Tokens.COLON)

    body = parse_body(parser)

    return Controller(method, body, args)
