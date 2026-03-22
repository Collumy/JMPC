from compiler.lexer.tokens import Tokens
from compiler.parser.expressions.expressions import parse_expression
from compiler.utils.code.errors import error
from compiler.ast.node import Action, Argument
from compiler.ast.expressions import TypeList, TypeString, TypeEnum

VARS = [
    Tokens.VARIABLE,
    Tokens.LINE_VARIABLE,
    Tokens.LOCAL_VARIABLE,
    Tokens.GAME_VARIABLE,
    Tokens.SAVE_VARIABLE
]

def parse_text(parser, tokens):
    parser.eat(Tokens.VARIABLE)
    parser.eat(Tokens.COLON)
    if parser.current.type not in VARS: 
        error(parser, "Ожидалась переменная для присвоения")
    
    tokens_types = [tok for tok in tokens][3:]

    # text: result = ...
    if Tokens.DOT not in tokens_types:
        result = parse_expression(parser)

        # text: text[index]
        if parser.current.type == Tokens.LBRACKET:
            parser.eat(Tokens.LBRACKET)
            index = parse_expression(parser)
            parser.eat(Tokens.RBRACKET)

            return Action("variable", "set_variable_get_char_at", [
                Argument("variable", result), 
                Argument("text", result),
                Argument("index", index)
            ])
        
        # text: result = ...
        elif parser.current.type == Tokens.ASSIGN:
            parser.eat(Tokens.ASSIGN)

            # text: result = len(text)
            if parser.current.type == Tokens.IDENTIFIER and parser.current.value == "len":
                parser.eat(Tokens.IDENTIFIER)
                parser.eat(Tokens.LPAREN)
                text = parse_expression(parser)
                parser.eat(Tokens.RPAREN)

                return Action("variable", "set_variable_text_length", [
                    Argument("variable", result), 
                    Argument("text", text)
                ])

            # text: result = ord(char)
            if parser.current.type == Tokens.IDENTIFIER and parser.current.value == "ord":
                parser.eat(Tokens.IDENTIFIER); parser.eat(Tokens.LPAREN)
                char = parse_expression(parser)
                parser.eat(Tokens.RPAREN)

                return Action("variable", "set_variable_char_to_number", [
                    Argument("variable", result), Argument("char", char)
                ])

            # text: result = chr(number) - символ из кода
            if parser.current.type == Tokens.IDENTIFIER and parser.current.value == "chr":
                parser.eat(Tokens.IDENTIFIER); parser.eat(Tokens.LPAREN)
                number = parse_expression(parser)
                parser.eat(Tokens.RPAREN)

                return Action("variable", "set_variable_to_char", [
                    Argument("variable", result), Argument("number", number)
                ])

            # Парсим первое выражение
            first_expr = parse_expression(parser)
            if parser.current.type == Tokens.PLUS:
                texts = [first_expr]
                
                while parser.current.type == Tokens.PLUS:
                    parser.eat(Tokens.PLUS)
                    texts.append(parse_expression(parser))
                texts = TypeList(texts)
                merging = TypeEnum("CONCATENATION")
                
                return Action("variable", "set_variable_text", [
                    Argument("variable", result), Argument("text", texts),
                    Argument("merging", merging)
                ])

            # text: result = "abc" * 5 (повторение)
            if parser.current.type == Tokens.STAR:
                parser.eat(Tokens.STAR)
                repeat = parse_expression(parser)

                return Action("variable", "set_variable_repeat_text", [
                    Argument("variable", result), Argument("text", first_expr), Argument("repeat", repeat)
                ])

            # text: result = text[start:end] (срез)
            if parser.current.type == Tokens.LBRACKET:
                parser.eat(Tokens.LBRACKET)
                start = None
                if parser.current.type != Tokens.COLON:
                    start = parse_expression(parser)


                if parser.current.type == Tokens.RBRACKET:  
                    parser.eat(Tokens.RBRACKET)
                    return Action("variable", "set_variable_get_char_at", [
                        Argument("variable", result), Argument("text", first_expr), Argument("index", start)
                    ])

                # Ожидаем :
                if parser.current.type != Tokens.COLON: error(parser, "Ожидалось : для среза")
                parser.eat(Tokens.COLON)
                
                # Парсим end
                end = None
                if parser.current.type != Tokens.RBRACKET:
                    end = parse_expression(parser)
                
                parser.eat(Tokens.RBRACKET)

                args = [
                    Argument("variable", result),
                    Argument("text", first_expr)
                ]
                if start is not None:
                    args.append(Argument("start", start))
                if end is not None:
                    args.append(Argument("end", end))

                return Action("variable", "set_variable_trim_text", args)

            # Простое присваивание: text: result = some_text
            if parser.current.type in (Tokens.DEDENT, Tokens.NEWLINE):
                # Если это просто строка, создаем действие text
                return Action("variable", "set_variable_text", [
                    Argument("variable", result),
                    Argument("text", TypeList([first_expr])),
                    Argument("merging", TypeString("CONCATENATION"))
                ])
            
            error(parser, "Неизвестное действие с текстом")

        else:
            error(parser, "Ожидалось = или [ после переменной")

    else:
        from .custom_dot import handle_dot_method
        return handle_dot_method(parser, "text")