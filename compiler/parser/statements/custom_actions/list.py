from compiler.lexer.tokens import Tokens
from compiler.parser.expressions.expressions import parse_expression
from compiler.utils.errors import error
from compiler.ast.node import Action, Argument

VARS = [
    Tokens.VARIABLE,
    Tokens.LINE_VARIABLE,
    Tokens.LOCAL_VARIABLE,
    Tokens.GAME_VARIABLE,
    Tokens.SAVE_VARIABLE
]

def parse_list(parser, tokens):
    parser.eat(Tokens.VARIABLE)
    parser.eat(Tokens.COLON)
    if parser.current.type not in VARS: error(parser, "Ожидалась переменная для присвоения")
    tokens_types = [tok for tok in tokens][3:]

    if Tokens.DOT not in tokens_types:
        result = parse_expression(parser)

        if parser.current.type == Tokens.LBRACKET:
            parser.eat(Tokens.LBRACKET)
            first = 0; second = 0     
            
            if parser.current.type != Tokens.COLON and parser.current.type != Tokens.DOUBLE_COLON:
                first = parse_expression(parser)      

                if parser.current.type == Tokens.RBRACKET:
                    parser.eat(Tokens.RBRACKET)
                    if parser.current.type != Tokens.ASSIGN: error(parser, "Ожидалось =, но получено другое")
                    parser.eat(Tokens.ASSIGN)
                    value = parse_expression(parser)
                    return Action("variable", "set_variable_set_list_value", [
                        Argument("variable", result), Argument("list", result),
                        Argument("number", first), Argument("value", value)])
                
                if parser.current.type != Tokens.COLON: error(parser, "Ожидалось :, но получено другое")


            elif parser.current.type == Tokens.DOUBLE_COLON:
                parser.eat(Tokens.DOUBLE_COLON)

                if parser.current.type != Tokens.NUMBER or parser.current.value != "-1":
                    error(parser, "Ожидалось число -1, чтобы перевернуть список")
                parser.eat(Tokens.NUMBER)

                if parser.current.type != Tokens.RBRACKET: error(parser, "Ожидалось ], но получено другое")            
                parser.eat(Tokens.RBRACKET)

                return Action("variable", "set_variable_reverse_list", [
                    Argument("variable", result),
                    Argument("list", result)
                ])           


            parser.eat(Tokens.COLON)
            if parser.current.type != Tokens.RBRACKET: second = parse_expression(parser)
            if parser.current.type != Tokens.RBRACKET: error(parser, "Ожидалось ] для закрытия слайса")
            parser.eat(Tokens.RBRACKET)

            args = [Argument("variable", result), Argument("list", result)]
            if first != 0: args.append(Argument("start", first))
            if second != 0: args.append(Argument("end", second))

            return Action("variable", "set_variable_trim_list", args)



        if parser.current.type == Tokens.PLUS_ASSIGN:
            parser.eat(Tokens.PLUS_ASSIGN)
            list_2 = parse_expression(parser)

            return Action("variable", "set_variable_append_list", [
                Argument("variable", result), Argument("list_1", result), Argument("list_2", list_2)
            ])



        if parser.current.type == Tokens.ASSIGN:
            parser.eat(Tokens.ASSIGN)
            
            if parser.current.type == Tokens.IDENTIFIER:
                parser.eat(Tokens.IDENTIFIER)
                parser.eat(Tokens.LPAREN)
                list_1 = parse_expression(parser)

                if parser.current.type != Tokens.RPAREN: error(parser, "Ожидалось ), но получено другое")
                parser.eat(Tokens.RPAREN)

                return Action("variable", "set_variable_get_list_length", [
                    Argument("variable", result), Argument("list", list_1)
                ])
            
            list_1 = parse_expression(parser)
            
            if parser.current.type in (Tokens.DEDENT, Tokens.NEWLINE):
                return Action("variable", "set_variable_create_list", [
                                Argument("values", list_1), Argument("variable", result)
                            ]) 
            
            if parser.current.type == Tokens.PLUS:
                parser.eat(Tokens.PLUS)
                list_2 = parse_expression(parser)

                return Action("variable", "set_variable_append_list", [
                    Argument("variable", result),
                    Argument("list_1", list_1), Argument("list_2", list_2)
                ])
            

            if parser.current.type == Tokens.LBRACKET:
                parser.eat(Tokens.LBRACKET)
                first = 0; second = 0
                
                if parser.current.type != Tokens.COLON and parser.current.type != Tokens.DOUBLE_COLON:
                    first = parse_expression(parser)      

                    if parser.current.type == Tokens.RBRACKET:
                        parser.eat(Tokens.RBRACKET)
                        return Action("variable", "set_variable_get_list_value", [
                            Argument("variable", result), Argument("list", list_1), Argument("number", first)
                        ])


                if parser.current.type == Tokens.DOUBLE_COLON:
                    parser.eat(Tokens.DOUBLE_COLON)

                    if parser.current.type != Tokens.NUMBER or parser.current.value != "-1":
                        error(parser, "Ожидалось число -1, чтобы перевернуть список")
                    parser.eat(Tokens.NUMBER)

                    if parser.current.type != Tokens.RBRACKET: error(parser, "Ожидалось ], но получено другое")            
                    parser.eat(Tokens.RBRACKET)

                    return Action("variable", "set_variable_reverse_list", [
                        Argument("variable", result), Argument("list", list_1)
                    ])           


                parser.eat(Tokens.COLON)
                if parser.current.type != Tokens.RBRACKET: second = parse_expression(parser)
                if parser.current.type != Tokens.RBRACKET: error(parser, "Ожидалось ] для закрытия слайса")
                parser.eat(Tokens.RBRACKET)

                args = [Argument("variable", result), Argument("list", list_1)]
                if first != 0: args.append(Argument("start", first))
                if second != 0: args.append(Argument("end", second))

                return Action("variable", "set_variable_trim_list", args)
            
        error(parser, "Действие не найдено")
    
    else:

        from .custom_dot import handle_dot_method
        return handle_dot_method(parser, "list")
