from compiler.lexer.tokens import Tokens
from compiler.parser.expressions.expressions import parse_expression
from compiler.utils.code.errors import error
from compiler.ast.node import Action, Argument
from compiler.ast.expressions import TypeDict, TypeList

VARS = [
    Tokens.VARIABLE,
    Tokens.LINE_VARIABLE,
    Tokens.LOCAL_VARIABLE,
    Tokens.GAME_VARIABLE,
    Tokens.SAVE_VARIABLE
]

def parse_dict(parser, tokens):
    parser.eat(Tokens.VARIABLE)
    parser.eat(Tokens.COLON)
    if parser.current.type not in VARS: error(parser, "Ожидалась переменная для присвоения")
    tokens_types = [tok for tok in tokens][3:]

    if Tokens.DOT not in tokens_types:
        result = parse_expression(parser)

        if parser.current.type == Tokens.LBRACKET:
            parser.eat(Tokens.LBRACKET)
            key = parse_expression(parser)
            parser.eat(Tokens.RBRACKET)
            parser.eat(Tokens.ASSIGN)
            value = parse_expression(parser)

            return Action("variable", "set_variable_set_map_value", [
                          Argument("variable", result), Argument("map", result),
                          Argument("key", key), Argument("value", value)
            ]) 
        
        elif parser.current.type == Tokens.ASSIGN:
            parser.eat(Tokens.ASSIGN)

            if parser.current.type == Tokens.IDENTIFIER and parser.current.value == "len":
                parser.eat(Tokens.IDENTIFIER); parser.eat(Tokens.LPAREN)
                dict = parse_expression(parser)
                parser.eat(Tokens.RPAREN)

                return Action("variable", "set_variable_get_map_size", [
                    Argument("variable", result), Argument("map", dict)
                ])

            dict = parse_expression(parser)

            if parser.current.type in (Tokens.DEDENT, Tokens.NEWLINE):
                if not isinstance(dict, TypeDict): error(parser, "Ожидался словарь для присвоения")
                keys = []; values = []
                for arg in dict.items:
                    keys.append(arg[0]); values.append(arg[1])
                keys = TypeList(keys); values = TypeList(values)

                return Action("variable", "set_variable_create_map", [
                    Argument("variable", result), Argument("keys", keys), Argument("values", values)
                ])
        
            if parser.current.type == Tokens.LBRACKET:
                parser.eat(Tokens.LBRACKET)
                key = parse_expression(parser)
                parser.eat(Tokens.RBRACKET)

                return Action("variable", "set_variable_get_map_value", [
                    Argument("variable", result), Argument("map", dict), Argument("key", key)
                ])
            
            if parser.current.type == Tokens.PLUS:
                parser.eat(Tokens.PLUS)
                dict2 = parse_expression(parser)

                return Action("variable", "set_variable_append_map", [
                    Argument("variable", result), Argument("map", dict), Argument("other_map", dict2)
                ])
            
            error(parser, "Неизвестное действие")

        else:
            error(parser, "Неизвестное действие")

    else:

        from .custom_dot import handle_dot_method
        return handle_dot_method(parser, "map")