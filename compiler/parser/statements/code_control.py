from compiler.lexer.tokens import Tokens, Token
from compiler.ast.node import Action, Argument
from compiler.ast.expressions import TypeVariable, TypeList
from compiler.parser.core.parse_args import parse_all_arguments
from compiler.parser.expressions.expressions import parse_expression
from compiler.utils.code.errors import error

from compiler.data.data_loader import load_json
CONTROL_ACTIONS = load_json("code.json")

def parse_code(parser):

    word = parser.current.value

    # Ищем действие по алиасам
    matched = None
    for meta in CONTROL_ACTIONS.values():
        if word in meta["aliases"]:
            matched = meta
            break

    if matched is None:
        error(parser, f"Ожидалось continue/break/return/wait..., но получено '{word}'")

    method = matched["action"]

    parser.eat(Tokens.CODE_CONTROL)

    if "args" in matched: args = parse_all_arguments(parser, matched["args"], method)
    else: args = []

    if method == "control_return_function" and parser.current.type != Tokens.NEWLINE:
        if parser.context != "function": error(parser, "Возвращать значения можно только в функции")
        return [parse_return(parser), Action("variable", method, args)]

    return Action("variable", method, args)





def parse_return(parser):
    returning_list = []
    while parser.current.type != Tokens.NEWLINE:
        returning_list.append(parse_expression(parser))

        if parser.current.type == Tokens.COMMA: parser.eat(Tokens.COMMA)
        else: break
    
    variables = []
    for i in range(len(returning_list)):
        fake_token = Token(Tokens.LOCAL_VARIABLE, f"jmpc_return{i+1}", 0, 0)
        variables.append(TypeVariable(fake_token))
    

    return Action("variable", "set_variable_multiple", [
                  Argument("variables", TypeList(variables)), Argument("values", TypeList(returning_list))
                  ])