from compiler.lexer.tokens import Tokens
from compiler.parser.expressions.expressions import parse_expression
from compiler.utils.code.errors import error
from compiler.ast.node import Action, Argument
from compiler.ast.expressions import TypeList, TypeEnum, TypeNumber

VARS = [
    Tokens.VARIABLE,
    Tokens.LINE_VARIABLE,
    Tokens.LOCAL_VARIABLE,
    Tokens.GAME_VARIABLE,
    Tokens.SAVE_VARIABLE
]

def parse_number(parser, tokens):
    parser.eat(Tokens.VARIABLE)
    parser.eat(Tokens.COLON)
    if parser.current.type not in VARS: 
        error(parser, "Ожидалась переменная для присвоения")
    
    tokens_types = [tok for tok in tokens][3:]

    # number: result = ...
    if Tokens.DOT not in tokens_types:
        result = parse_expression(parser)
        
        # number: result = ...
        if parser.current.type == Tokens.ASSIGN:
            parser.eat(Tokens.ASSIGN)

            # number: result = abs(num)
            if parser.current.type == Tokens.IDENTIFIER and parser.current.value == "abs":
                parser.eat(Tokens.IDENTIFIER)
                parser.eat(Tokens.LPAREN)
                number = parse_expression(parser)
                parser.eat(Tokens.RPAREN)

                return Action("variable", "set_variable_absolute", [
                    Argument("variable", result),
                    Argument("number", number)
                ])

            # number: result = min(...)
            if parser.current.type == Tokens.IDENTIFIER and parser.current.value == "min":
                parser.eat(Tokens.IDENTIFIER)
                parser.eat(Tokens.LPAREN)
                
                values = []
                while parser.current.type != Tokens.RPAREN:
                    values.append(parse_expression(parser))
                    if parser.current.type == Tokens.COMMA:
                        parser.eat(Tokens.COMMA)
                    else: break
                
                parser.eat(Tokens.RPAREN)

                return Action("variable", "set_variable_min", [
                    Argument("variable", result),
                    Argument("value", TypeList(values))
                ])

            # number: result = max(...)
            if parser.current.type == Tokens.IDENTIFIER and parser.current.value == "max":
                parser.eat(Tokens.IDENTIFIER)
                parser.eat(Tokens.LPAREN)
                
                values = []
                while parser.current.type != Tokens.RPAREN:
                    values.append(parse_expression(parser))
                    if parser.current.type == Tokens.COMMA:
                        parser.eat(Tokens.COMMA)
                    else: break
                
                parser.eat(Tokens.RPAREN)

                return Action("variable", "set_variable_max", [
                    Argument("variable", result),
                    Argument("value", TypeList(values))
                ])

            # number: result = clamp(num, min, max)
            if parser.current.type == Tokens.IDENTIFIER and parser.current.value == "clamp":
                parser.eat(Tokens.IDENTIFIER)
                parser.eat(Tokens.LPAREN)
                
                number = parse_expression(parser)
                parser.eat(Tokens.COMMA)
                min_val = parse_expression(parser)
                parser.eat(Tokens.COMMA)
                max_val = parse_expression(parser)
                parser.eat(Tokens.RPAREN)

                return Action("variable", "set_variable_clamp", [
                    Argument("variable", result),
                    Argument("number", number),
                    Argument("min", min_val),
                    Argument("max", max_val)
                ])

            # number: result = round(num) или round(num, precision)
            if parser.current.type == Tokens.IDENTIFIER and parser.current.value == "round":
                parser.eat(Tokens.IDENTIFIER)
                parser.eat(Tokens.LPAREN)
                
                number = parse_expression(parser)
                precision = None
                round_type = TypeEnum("ROUND")
                
                if parser.current.type == Tokens.COMMA:
                    parser.eat(Tokens.COMMA)
                    precision = parse_expression(parser)
                
                parser.eat(Tokens.RPAREN)

                args = [
                    Argument("variable", result),
                    Argument("number", number),
                    Argument("round_type", round_type)
                ]
                if precision is not None:
                    args.insert(2, Argument("precision", precision))

                return Action("variable", "set_variable_round", args)

            # number: result = floor(num)
            if parser.current.type == Tokens.IDENTIFIER and parser.current.value == "floor":
                parser.eat(Tokens.IDENTIFIER)
                parser.eat(Tokens.LPAREN)
                number = parse_expression(parser)
                parser.eat(Tokens.RPAREN)

                return Action("variable", "set_variable_round", [
                    Argument("variable", result),
                    Argument("number", number),
                    Argument("round_type", TypeEnum("FLOOR"))
                ])

            # number: result = ceil(num)
            if parser.current.type == Tokens.IDENTIFIER and parser.current.value == "ceil":
                parser.eat(Tokens.IDENTIFIER)
                parser.eat(Tokens.LPAREN)
                number = parse_expression(parser)
                parser.eat(Tokens.RPAREN)

                return Action("variable", "set_variable_round", [
                    Argument("variable", result),
                    Argument("number", number),
                    Argument("round_type", TypeEnum("CEIL"))
                ])

            # number: result = log(num, base)
            if parser.current.type == Tokens.IDENTIFIER and parser.current.value == "log":
                parser.eat(Tokens.IDENTIFIER)
                parser.eat(Tokens.LPAREN)
                
                number = parse_expression(parser)
                parser.eat(Tokens.COMMA)
                base = parse_expression(parser)
                parser.eat(Tokens.RPAREN)

                return Action("variable", "set_variable_log", [
                    Argument("variable", result),
                    Argument("number", number),
                    Argument("base", base)
                ])

            # number: result = random(min, max) или randint(min, max)
            if parser.current.type == Tokens.IDENTIFIER and parser.current.value in ("random", "randint"):
                func_name = parser.current.value
                parser.eat(Tokens.IDENTIFIER)
                parser.eat(Tokens.LPAREN)
                
                min_val = parse_expression(parser)
                parser.eat(Tokens.COMMA)
                max_val = parse_expression(parser)
                parser.eat(Tokens.RPAREN)

                is_integer = TypeEnum("TRUE") if func_name == "randint" else TypeEnum("FALSE")

                return Action("variable", "set_variable_random_number", [
                    Argument("variable", result),
                    Argument("min", min_val),
                    Argument("max", max_val),
                    Argument("integer", is_integer)
                ])

            # Парсим первое выражение
            first_expr = parse_expression(parser)

            # number: result = 1 + 2 + 3 + 4 (сложение)
            if parser.current.type == Tokens.PLUS:
                values = [first_expr]
                
                while parser.current.type == Tokens.PLUS:
                    parser.eat(Tokens.PLUS)
                    values.append(parse_expression(parser))
                
                return Action("variable", "set_variable_add", [
                    Argument("variable", result),
                    Argument("value", TypeList(values))
                ])

            # number: result = 10 - 2 - 3 (вычитание)
            if parser.current.type == Tokens.MINUS:
                values = [first_expr]
                
                while parser.current.type == Tokens.MINUS:
                    parser.eat(Tokens.MINUS)
                    values.append(parse_expression(parser))
                
                return Action("variable", "set_variable_subtract", [
                    Argument("variable", result),
                    Argument("value", TypeList(values))
                ])

            # number: result = 2 * 3 * 4 (умножение)
            if parser.current.type == Tokens.STAR:
                values = [first_expr]
                
                while parser.current.type == Tokens.STAR:
                    parser.eat(Tokens.STAR)
                    values.append(parse_expression(parser))
                
                return Action("variable", "set_variable_multiply", [
                    Argument("variable", result),
                    Argument("value", TypeList(values))
                ])

            # number: result = 100 / 2 / 5 (деление)
            if parser.current.type == Tokens.SLASH:
                values = [first_expr]
                
                while parser.current.type == Tokens.SLASH:
                    parser.eat(Tokens.SLASH)
                    values.append(parse_expression(parser))
                
                return Action("variable", "set_variable_divide", [
                    Argument("variable", result),
                    Argument("value", TypeList(values))
                ])

            # number: result = num % 2 (остаток от деления)
            if parser.current.type == Tokens.PERCENT:
                parser.eat(Tokens.PERCENT)
                divisor = parse_expression(parser)

                return Action("variable", "set_variable_remainder", [
                    Argument("variable", result),
                    Argument("dividend", first_expr),
                    Argument("divisor", divisor)
                ])

            # number: result =  num ^ 2 (степень)
            if parser.current.type == Tokens.POW:
                parser.eat(parser.current.type)
                power = parse_expression(parser)

                return Action("variable", "set_variable_pow", [
                    Argument("variable", result),
                    Argument("base", first_expr),
                    Argument("power", power)
                ])

            # Простое присваивание
            if parser.current.type in (Tokens.DEDENT, Tokens.NEWLINE):
                return Action("variable", "set_variable", [
                    Argument("variable", result),
                    Argument("value", first_expr)
                ])
            
            error(parser, "Неизвестное действие с числом")

        # number: result += 5
        elif parser.current.type == Tokens.PLUS_ASSIGN:
            parser.eat(Tokens.PLUS_ASSIGN)
            value = parse_expression(parser)

            return Action("variable", "set_variable_increment", [
                Argument("variable", result),
                Argument("number", value)
            ])
        
        # number: result++
        elif parser.current.type == Tokens.PLUS_PLUS:
            parser.eat(Tokens.PLUS_PLUS)

            return Action("variable", "set_variable_increment", [
                Argument("variable", result),
                Argument("number", TypeNumber(1))
            ])           

        # number: result -= 5
        elif parser.current.type == Tokens.MINUS_ASSIGN:
            parser.eat(Tokens.MINUS_ASSIGN)
            value = parse_expression(parser)

            return Action("variable", "set_variable_decrement", [
                Argument("variable", result),
                Argument("number", value)
            ])
        
        # number: result--
        elif parser.current.type == Tokens.MINUS_MINUS:
            parser.eat(Tokens.MINUS_MINUS)

            return Action("variable", "set_variable_decrement", [
                Argument("variable", result),
                Argument("number", TypeNumber(1))
            ])           

        # number: result *= 5
        elif parser.current.type == Tokens.STAR_ASSIGN:
            parser.eat(Tokens.STAR_ASSIGN)
            value = parse_expression(parser)

            return Action("variable", "set_variable_multiply", [
                Argument("variable", result),
                Argument("value", TypeList([result, value]))
            ])

        # number: result /= 5
        elif parser.current.type == Tokens.SLASH_ASSIGN:
            parser.eat(Tokens.SLASH_ASSIGN)
            value = parse_expression(parser)

            return Action("variable", "set_variable_divide", [
                Argument("variable", result),
                Argument("value", TypeList([result, value]))
            ])

        # number: result %= 5
        elif parser.current.type == Tokens.PERCENT_ASSIGN:
            parser.eat(Tokens.PERCENT_ASSIGN)
            divisor = parse_expression(parser)

            return Action("variable", "set_variable_remainder", [
                Argument("variable", result),
                Argument("dividend", result),
                Argument("divisor", divisor)
            ])

        # number: result ^= 2
        elif parser.current.type == Tokens.POW_ASSIGN:
            parser.eat(parser.current.type)
            power = parse_expression(parser)

            return Action("variable", "set_variable_pow", [
                Argument("variable", result),
                Argument("base", result),
                Argument("power", power)
            ])

        else:
            error(parser, "Ожидалось =, +=, -=, *=, /=, %= или ^= после переменной")

    # number: result = num.method()
    else:
        error(parser, "У операций над числами нет действия с точкой")