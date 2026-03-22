from compiler.lexer.tokens import Tokens
from compiler.parser.expressions.expressions import parse_expression, TypeList, TypeDict
from compiler.utils.code.errors import error
from compiler.ast.node import Action, Argument
from compiler.ast.expressions import TypeList


def parse_assignment(parser):
    assignments = []

    while True:
        target = parse_expression(parser)
        parser.eat(Tokens.ASSIGN)

        value_expr = parse_expression(parser)

        assignments.append((target, value_expr))


        if parser.current.type == Tokens.COMMA:
            parser.eat(Tokens.COMMA)
            if parser.current.type == Tokens.NL: parser.eat(Tokens.NL)
        else: break



    # Одно присваивание
    if len(assignments) == 1:
        target_token, value_expr = assignments[0]

        if isinstance(value_expr, TypeList):
            if len(value_expr.items) < 21:

                return Action("variable", "set_variable_create_list", [
                    Argument("variable", target_token), Argument("values", value_expr)
                ])
            
        if isinstance(value_expr, TypeDict):
            if len(value_expr.items) < 15:
                values_d = []; keys_d = []
                for item in value_expr.items:
                    keys_d.append(item[0]); values_d.append(item[1])

                return Action("variable", "set_variable_create_map_from_values", [
                    Argument("variable", target_token),
                    Argument("keys", TypeList(keys_d)), Argument("values", TypeList(values_d))
                ])
                

        return Action("variable", "set_variable_value", [
                Argument("variable", target_token), Argument("value", value_expr)
            ])

    # Несколько присваиваний
    variables = []
    values = []

    for target_token, value_expr in assignments:
        variables.append(target_token)
        values.append(value_expr)

    return Action("variable", "set_variable_multiple",
        [
            Argument("variables", TypeList(variables)),
            Argument("values", TypeList(values))
        ]
    )





def parse_assign_block(parser):
    parser.eat(Tokens.VARIABLE)
    parser.eat(Tokens.COLON)
    parser.eat(Tokens.NEWLINE)
    parser.eat(Tokens.INDENT)

    variables = []
    values = []

    while parser.current.type != Tokens.DEDENT:

        action = parse_assignment(parser)

        var_arg = action.args[0].value
        val_arg = action.args[1].value

        variables.append(var_arg)
        values.append(val_arg)

        if parser.current.type == Tokens.NEWLINE:
            parser.eat(Tokens.NEWLINE)

    parser.eat(Tokens.DEDENT)


    return Action("variable", "set_variable_multiple", [
            Argument("variables", TypeList(variables)),
            Argument("values", TypeList(values))
        ])