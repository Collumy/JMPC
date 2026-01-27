from compiler.lexer.tokens import Tokens
from compiler.utils.errors import error
from compiler.parser.expressions.expressions import parse_expression
from compiler.ast.expressions import TypeEnum, TypeList, TypeVariable
from compiler.ast.node import Argument

MISSING = "MISSING"


def parse_all_arguments(parser, arg_metas, context_name="", extra=None):

    if extra is None: extra = {}
    first_vars = extra.get("first_variables", [])
    first_non_vars = extra.get("first_non_variables", [])


    if parser.current.type != Tokens.LPAREN: error(parser, "Ожидалась ( для аргументов")
    parser.eat(Tokens.LPAREN)

    parsed_args = []  # (arg_name or None, value)

    while parser.current.type != Tokens.RPAREN:
        arg_name = None

        # Именованный аргумент: name=value
        if parser.current.type == Tokens.VARIABLE and parser.peek(1).type == Tokens.ASSIGN:
            arg_name = parser.current.value
            parser.eat(Tokens.VARIABLE)
            parser.eat(Tokens.ASSIGN)

            if not any(meta["id"] == arg_name for meta in arg_metas):
                error(parser, f"Неизвестный аргумент '{arg_name}' для {context_name}")

        # Значение
        if parser.current.type in (Tokens.COMMA, Tokens.RPAREN):
            value = MISSING 
        else:
            value = parse_expression(parser)

        parsed_args.append((arg_name, value))

        if parser.current.type != Tokens.COMMA:
            break
        parser.eat(Tokens.COMMA)

    if parser.current.type != Tokens.RPAREN:
        error(parser, f"Ожидалась ')' после аргументов {context_name}")
    parser.eat(Tokens.RPAREN)



    final_args = {}

    # Переданные готовые аргументы
    for value in first_non_vars:
        for meta in arg_metas:
            if meta["type"] not in ("variable", "result") and meta["id"] not in final_args:
                final_args[meta["id"]] = value
                break
    
    for value in first_vars:
        for meta in arg_metas:
            if meta["type"] in ("variable", "result") and meta["id"] not in final_args:
                final_args[meta["id"]] = value
                break
    


    # Именованные аргументы
    for arg_name, value in parsed_args:
        if arg_name:
            if arg_name in final_args:
                error(parser, f"Аргумент '{arg_name}' указан дважды")
            if value != MISSING:
                final_args[arg_name] = value

    # Позиционные аргументы
    positional_values = [
        v for (n, v) in parsed_args
        if not n and v != MISSING
    ]


    for value in positional_values:
        placed = False

        # Если TypeVariable — пытаемся найти слот с таким же именем
        if isinstance(value, TypeVariable):
            var_name = value.token.value
            for meta in arg_metas:
                if meta["id"] == var_name and meta["id"] not in final_args:
                    final_args[var_name] = value
                    placed = True
                    break

        if placed:
            continue

        # Иначе — первый свободный слот
        for meta in arg_metas:
            arg_id = meta["id"]
            if arg_id not in final_args:
                final_args[arg_id] = value
                placed = True
                break

        if not placed:
            error(parser, f"Слишком много позиционных аргументов для {context_name}")



    args = []
    for meta in arg_metas:
            arg_id = meta["id"]
            raw_value = final_args.get(arg_id, MISSING)

            # Пропущено пользователем - пытаемся взять default
            if raw_value == MISSING:
                if "default" in meta:
                    raw_value = meta["default"]
                else:
                    continue

            # ENUM
            if meta["type"] == "enum":
                if isinstance(raw_value, TypeVariable):
                    # variable enum - используем первый вариант
                    args.append(Argument(arg_id, TypeEnum(meta["values"][0], raw_value)))
                    continue

                value = getattr(raw_value, "value", None)
                if value not in meta["values"]:
                    error(
                        parser,
                        f"Недопустимое значение '{value}' для аргумента '{arg_id}'. "
                        f"Допустимые: {', '.join(meta['values'])}"
                    )
                args.append(Argument(arg_id, TypeEnum(value)))
                continue

            if "array" in meta:
                if isinstance(raw_value, TypeList):
                    args.append(Argument(arg_id, raw_value))
                else:
                    args.append(Argument(arg_id, TypeList([raw_value])))
                continue

            # Обычный аргумент
            args.append(Argument(arg_id, raw_value))

    return args