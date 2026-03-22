from compiler.lexer.tokens import Tokens
from compiler.ast.node import Action, Controller
from compiler.parser.core.parse_args import parse_all_arguments
from compiler.parser.core.operations import parse_body
from compiler.utils.code.errors import error

from compiler.data.data_loader import load_json
ACTIONS = load_json("controller.json")


def parse_controller(parser):
    parser.eat(Tokens.CONTROLLER)
    parser.eat(Tokens.DOT)

    word = parser.current.value
    matched = None
    for meta in ACTIONS.values():
        if word in meta["aliases"]:
            matched = meta
            break
    
    if matched is None: error(parser, f"Неизвестное controller-действие: '{word}'")
    method = matched["action"]

    parser.eat(Tokens.IDENTIFIER)

    # controller.action(...)
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

    parser.eat(Tokens.COLON)
    body = parse_body(parser)

    return Controller(method, body, args)
