from compiler.lexer.tokens import Tokens
from compiler.utils.errors import error

from compiler.parser.statements.custom_actions.assignment import parse_assignment, parse_assign_block
from compiler.parser.statements.custom_actions.list import parse_list
from compiler.parser.statements.custom_actions.dict import parse_dict
from compiler.parser.statements.custom_actions.text import parse_text
from compiler.parser.statements.custom_actions.number import parse_number

# Список действий начинающихся с assign: list: dict:
STARTING_FROM = ["assign", "list", "l", "dict", "d", "map", "text", "t", "number", "n", "num", "custom", "c"]



def parse_body(parser):
    from compiler.parser.statements.if_else import parse_if
    from compiler.parser.statements.action import parse_action
    from compiler.parser.statements.repeat import parse_while
    from compiler.parser.statements.code_control import parse_code
    from compiler.parser.statements.controller import parse_controller
    from compiler.parser.statements.select import parse_selector
    from compiler.parser.statements.starts.call_definition import parse_call


    if parser.current.type != Tokens.NEWLINE: error(parser, "После ':' ожидается новая строка")
    parser.eat(Tokens.NEWLINE)

    if parser.current.type != Tokens.INDENT: error(parser, "После новой строки ожидается отступ")
    parser.eat(Tokens.INDENT)

    body = []
    else_counter = 0

    while parser.current.type != Tokens.DEDENT:
        if else_counter > 0: else_counter -= 1

        if parser.current.type == Tokens.NEWLINE:
            parser.eat(Tokens.NEWLINE); continue

        tok = parser.current

        if tok.type in (Tokens.EVENT, Tokens.FUNCTION, Tokens.PROCESS):
            error(parser, "Нельзя объявлять event/function/process внутри блоков")

        tokens = collect_statement_tokens(parser)

        # все действия по типу assign: list: dict:
        if tok.type == Tokens.VARIABLE and parser.peek().type == Tokens.COLON:
            value = tok.value
            if value in STARTING_FROM:
                if value in ("assign", "a"): node = parse_assign_block(parser)
                if value in ("list", "l"): node = parse_list(parser, tokens)
                if value in ("dict", "d", "map"): node = parse_dict(parser, tokens)
                if value in ("text", "t"): node = parse_text(parser, tokens)
                if value in ("number", "num", "n"): node = parse_number(parser, tokens)
                if value in ("custom", "c"): node = parse_action(parser, True)
                body.append(node)
                continue
            else: error(parser, "Неожиданное действие, ожидалось list/map/assign/text и подобные")

        # если
        if tok.type in (Tokens.IF, Tokens.ELSE, Tokens.ELIF):
            if tok.type in (Tokens.ELSE, Tokens.ELIF):
                if else_counter == 0: error(parser, "Ожидалось 'Если' или 'Иначе если' до этого действия")
            if tok.type == Tokens.IF or tok.type == Tokens.ELIF or (tok.type == Tokens.ELSE and parser.peek().type == Tokens.IF):
                else_counter = 2
            node = parse_if(parser)
            body.append(node)
            continue

        if tok.type in (Tokens.WHILE, Tokens.FOR, Tokens.CODE_CONTROL, Tokens.CONTROLLER,
                        Tokens.SELECT, Tokens.DEFINITION_CALL):
            if tok.type in (Tokens.WHILE, Tokens.FOR): node = parse_while(parser)
            if tok.type == Tokens.CONTROLLER: node = parse_controller(parser)
            if tok.type == Tokens.SELECT: node = parse_selector(parser)
            if tok.type == Tokens.DEFINITION_CALL: node = parse_call(parser)
            if tok.type == Tokens.CODE_CONTROL: node = parse_code(parser)

            if isinstance(node, list): body.append(node[0]); body.append(node[1])
            else: body.append(node)

            continue


        # все действия из jmcc с ::
        if (Tokens.DOUBLE_COLON in tokens) or (Tokens.DOT in tokens):
            node = parse_action(parser)
            body.append(node)
            continue

        if Tokens.ASSIGN in tokens:
            assignments = parse_assignment(parser)
            body.append(assignments)
            continue

        error(parser, "Неизвестная конструкция внутри блока")

    parser.eat(Tokens.DEDENT)
    return body




def collect_statement_tokens(parser):
    tokens = [parser.current.type]
    offset = 0

    while True:
        next_tok = parser.peek(offset)
        if next_tok.type in (Tokens.NEWLINE, Tokens.DEDENT, Tokens.EOF): break
        tokens.append(next_tok.type)
        offset += 1
    return tokens