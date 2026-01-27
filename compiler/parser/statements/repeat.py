from compiler.lexer.tokens import Tokens
from compiler.ast.node import Repeat, Argument
from compiler.ast.expressions import TypeEnum, TypeList, TypeVariable
from compiler.parser.core.condition import parse_condition
from compiler.parser.core.operations import parse_body
from compiler.parser.core.parse_args import parse_all_arguments
from compiler.parser.expressions.expressions import parse_expression
from compiler.utils.errors import error


from compiler.parser.expressions.info import VARIABLES
from compiler.data.loops import CYCLES

def parse_while(parser):
    condition = None

    if parser.current.type == Tokens.WHILE:
        parser.eat(Tokens.WHILE)

        if parser.current.value not in ("True", "true"):
            condition = parse_condition(parser)
            method = "repeat_while"
        else:
            parser.eat(Tokens.VARIABLE)
            method = "repeat_forever" 
        parser.eat(Tokens.COLON)
        body = parse_body(parser)

        return Repeat(method, condition, body)




    parser.eat(Tokens.FOR)

    vars = []

    if parser.current.type not in VARIABLES:
        error(parser, "Ожидалась переменная после for")
    vars.append(parse_expression(parser))

    if parser.current.type == Tokens.COMMA:
        parser.eat(Tokens.COMMA)
        if parser.current.type not in VARIABLES:
            error(parser, "Ожидалась вторая переменная")
        vars.append(parse_expression(parser))


    if parser.current.value != "in": error(parser, "Ожидалось 'in' после переменных")
    parser.eat(Tokens.VARIABLE)


    if parser.current.type != Tokens.IDENTIFIER: error(parser, "Ожидалось имя источника итерации")
    loop_name = parser.current.value.lower()
    parser.eat(Tokens.IDENTIFIER)

    # ищем в таблице
    loop_def = None
    for name, data in CYCLES.items():
        if loop_name == name or loop_name in data.get("aliases", []):
            loop_def = data
            loop_name = name
            break

    if loop_def is None: error(parser, f"Неизвестный тип цикла: {loop_name}")


    parsed_args = []

    method = loop_def["action"]
    arg_metas = loop_def["args"]


    if loop_name in ("list", "map"):
        if len(vars) == 1:
            vars = [None, vars[0]]
        elif len(vars) == 2:
            vars = [vars[0], vars[1]]
        else:
            error(parser, f"{loop_name}() принимает 1 или 2 переменные")
    

    extra = {
        "first_variables": vars,    
        "first_non_variables": []    
    }


    args = parse_all_arguments(parser, arg_metas, loop_name, extra=extra)

    if parser.current.type != Tokens.COLON: error(parser, "После for (...) ожидается ':'")
    parser.eat(Tokens.COLON)

    body = parse_body(parser)

    return Repeat(method, args, body)