from compiler.lexer.tokens import Tokens
from compiler.parser.expressions.placeholders import placeholders
from compiler.ast.expressions import (
    TypeNumber,
    TypeString,
    TypeVariable,
    TypeList,
    TypeDict,
    FunctionCall,
    NamedArgumentNode
)
from compiler.utils.errors import error


def parse_expression(parser):
    token = parser.current

    if token.type == Tokens.NUMBER:
        parser.eat(Tokens.NUMBER)
        return TypeNumber(token.value)

    # ---------- STRING ----------
    if token.type == Tokens.STRING:
        parser.eat(Tokens.STRING)
        value = placeholders(token.value, parser)
        return TypeString(value)

    # ---------- FUNCTION CALL ----------
    if token.type == Tokens.IDENTIFIER and parser.peek().type == Tokens.LPAREN:
        return parse_function_call(parser)

    # ---------- VARIABLE ----------
    if token.type in (
        Tokens.VARIABLE,
        Tokens.GAME_VARIABLE,
        Tokens.LOCAL_VARIABLE,
        Tokens.SAVE_VARIABLE,
        Tokens.LINE_VARIABLE,
    ):
        parser.eat(token.type)
        token.value = placeholders(token.value, parser)
        return TypeVariable(token)

    # ---------- LIST ----------
    if token.type == Tokens.LBRACKET:
        return parse_list(parser)

    # ---------- DICT ----------
    if token.type == Tokens.LBRACE:
        return parse_dict(parser)

    error(parser, "Ожидалось выражение для присваивания, но получено другое")


# ============================================================
#  LIST: [a, b, c]
# ============================================================

def parse_list(parser):
    parser.eat(Tokens.LBRACKET)

    items = []
    while parser.current.type != Tokens.RBRACKET:
        if parser.current.type == Tokens.NL:
            parser.eat(Tokens.NL)
            if parser.current.type == Tokens.RBRACKET: break

        items.append(parse_expression(parser))

        if parser.current.type == Tokens.COMMA:
            parser.eat(Tokens.COMMA)


    parser.eat(Tokens.RBRACKET)
    return TypeList(items)


# ============================================================
#  DICT: {a: 1, b: 2}
# ============================================================

def parse_dict(parser):
    parser.eat(Tokens.LBRACE)

    items = []
    while parser.current.type != Tokens.RBRACE:
        if parser.current.type == Tokens.NL:
            parser.eat(Tokens.NL)
            if parser.current.type == Tokens.RBRACE: break           

        key = parse_expression(parser)
        if parser.current.type != Tokens.COLON: error(parser, "Ожидалось значение после ключа, но получено другое")
        parser.eat(Tokens.COLON)
        value = parse_expression(parser)
        items.append((key, value))

        if parser.current.type == Tokens.COMMA: parser.eat(Tokens.COMMA)

    parser.eat(Tokens.RBRACE)
    return TypeDict(items)


# ============================================================
#  FUNCTION CALL: name(expr, expr, ...)
# ============================================================

def parse_function_call(parser):
    func_token = parser.current
    func_name = parser.current.value

    parser.eat(Tokens.IDENTIFIER)
    parser.eat(Tokens.LPAREN)

    args = []

    if parser.current.type == Tokens.RPAREN:
        parser.eat(Tokens.RPAREN)
        return FunctionCall(func_name, args, func_token, parser)

    while True:

        if parser.current.type == Tokens.VARIABLE and parser.peek().type == Tokens.ASSIGN:
            # имя аргумента
            arg_name = parser.current.value
            parser.eat(Tokens.VARIABLE)

            parser.eat(Tokens.ASSIGN)

            # значение аргумента - полноценное выражение
            value = parse_expression(parser)

            args.append(NamedArgumentNode(arg_name, value))

        else:
            expr = parse_expression(parser)
            args.append(expr)

        # запятая - продолжаем
        if parser.current.type == Tokens.COMMA:
            parser.eat(Tokens.COMMA)
            continue

        # закрывающая скобка - конец
        if parser.current.type == Tokens.RPAREN:
            break

        error(parser, "Ожидалась ',' или ')'")

    parser.eat(Tokens.RPAREN)
    return FunctionCall(func_name, args, func_token, parser)