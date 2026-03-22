from compiler.lexer.tokens import Tokens
from compiler.ast.node import Event
from compiler.utils.code.errors import error
from compiler.parser.core.operations import parse_body

def parse_event(parser):
    parser.eat(Tokens.EVENT)

    if parser.current.type != Tokens.VARIABLE: error(parser, "После 'event' ожидается имя события")
    name = parser.current.value
    parser.eat(Tokens.VARIABLE)
    parser.eat(Tokens.COLON)

    parser.context = "event"
    body = parse_body(parser)

    return Event(name, body)