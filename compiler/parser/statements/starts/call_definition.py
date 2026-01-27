from compiler.lexer.tokens import Tokens, Token
from compiler.parser.expressions.expressions import parse_expression
from compiler.utils.errors import error
from compiler.ast.node import Action, Argument
from compiler.ast.expressions import TypeEnum, TypeString, TypeList, TypeDict, TypeVariable

from compiler.parser.core.function_signatures import get_function, has_function
from compiler.parser.expressions.info import VARIABLES

PROCESS_ENUMS = [
      [
          "COPY",
          "DONT_COPY",
          "SHARE"
      ],
      [
          "CURRENT_SELECTION",
          "CURRENT_TARGET",
          "FOR_EACH_IN_SELECTION",
          "NO_TARGET"
      ]
]





def parse_call(parser):
    parser.eat(Tokens.DEFINITION_CALL)
    args = []

    # call function / call process
    if parser.current.type == Tokens.FUNCTION:
        parser.eat(Tokens.FUNCTION)
        kind = "function"; code_name = "call_function"
    elif parser.current.type == Tokens.PROCESS:
        parser.eat(Tokens.PROCESS)
        kind = "process"; code_name = "start_process"
    else:
        error(parser, "Ожидалось 'function', 'def' или 'process', 'proc' после call")


    # ---------- process<"local", "target"> ----------
    modes = {}
    if kind == "process" and parser.current.type == Tokens.LESS:
        parser.eat(Tokens.LESS)

        local_expr = parse_expression(parser)
        if isinstance(local_expr, TypeString):
            if local_expr.value not in PROCESS_ENUMS[0]: error(parser, f"Ожидалось {PROCESS_ENUMS[0]}, но получено другое")
            local_expr = TypeEnum(local_expr.value)
        else:
            error(parser, "Ожидался текст в качестве маркера")
        args.append(Argument("local_variables_mode", local_expr))


        if parser.current.type == Tokens.COMMA:
            parser.eat(Tokens.COMMA)

            target_expr = parse_expression(parser)
            if isinstance(target_expr, TypeString):
                if target_expr.value not in PROCESS_ENUMS[1]: error(parser, f"Ожидалось {PROCESS_ENUMS[1]}, но получено другое")
                target_expr = TypeEnum(target_expr.value)
            else:
                error(parser, "Ожидался текст в качестве маркера")
            args.append(Argument("target_mode", target_expr))

        parser.eat(Tokens.GREATER)



    # ---------- call function Name(...) ----------
    if parser.current.type in (Tokens.IDENTIFIER, Tokens.VARIABLE):
        name = parser.current.value
        args.append(Argument(f"{kind}_name", TypeString(name, "plain")))
        parser.eat(parser.current.type)

        if not has_function(name, kind):
            error(parser, f"Функция или процесс {name} не найдена, может вы перепутали тип?")
        func_info = get_function(name, kind)
        params = TypeDict(parse_args(func_info.args, parser))

        args.append(Argument("args", params))
        
        if parser.current.type == Tokens.MINUS:
            return [Action("code", code_name, args), parse_return(parser, func_info.returning)]

        return Action("code", code_name, args)



    # ---------- call function (Name) ----------
    if parser.current.type == Tokens.LPAREN:
        parser.eat(Tokens.LPAREN)
        name = parse_expression(parser)
        if isinstance(name, TypeString): name.parsing = "plain"

        args.append(Argument(f"{kind}_name", name))
        parser.eat(Tokens.RPAREN)

        return Action("code", code_name, args)


    error(parser, "Некорректный синтаксис вызова")










MISSING = "MISSING"

def parse_args(params, parser):
    result = {}

    # Нет параметров
    if parser.current.type != Tokens.LPAREN:
        if len(params) == 0: return result
        error(parser, "Ожидались аргументы в скобках")

    parser.eat(Tokens.LPAREN)

    # Пустые скобки
    if parser.current.type == Tokens.RPAREN:
        parser.eat(Tokens.RPAREN)
        for p in params:
            if p.default == None: error(parser, f"Параметр {p.name} должен иметь аргумент")

            name = TypeString(p.name)
            result[name] = p.default
            if p.type_key == "enum": result[name] = TypeString(p.default)
        return result

    # Сырые аргументы
    raw_args = []

    while parser.current.type != Tokens.RPAREN:
        arg_name = None

        # Именованный аргумент: name = value
        if parser.current.type == Tokens.VARIABLE and parser.peek(1).type == Tokens.ASSIGN:
            arg_name = parser.current.value
            parser.eat(Tokens.VARIABLE)
            parser.eat(Tokens.ASSIGN)

            # Проверяем существование аргумента
            if not any(p.name == arg_name for p in params):
                error(parser, f"Неизвестное имя аргумента '{arg_name}'")

        # Значение или пропуск
        if parser.current.type in (Tokens.COMMA, Tokens.RPAREN): value = MISSING
        else: value = parse_expression(parser)

        raw_args.append((arg_name, value))

        if parser.current.type != Tokens.COMMA: break
        parser.eat(Tokens.COMMA)
        if parser.current.type == Tokens.NL: parser.eat(Tokens.NL)


    if parser.current.type != Tokens.RPAREN:
        error(parser, "Ожидалась ')' после аргументов")
    parser.eat(Tokens.RPAREN)



    final_values = {}  

    # Именованные аргументы
    for arg_name, value in raw_args:
        if arg_name is None:
            continue
        if arg_name in final_values and final_values[arg_name] is not MISSING:
            error(parser, f"Аргумент '{arg_name}' указан дважды")
        if value is MISSING:
            error(parser, f"У аргумента '{arg_name}' отсутствует значение")
        
        final_values[arg_name] = value

    positional = [v for (n, v) in raw_args if n is None]
    param_index = 0

    for value in positional:
        # ищем следующий параметр по порядку
        if param_index >= len(params):
            error(parser, "Слишком много позиционных аргументов")

        p = params[param_index]

        # если этот параметр уже заполнен именованным — ошибка дублирования
        if p.name in final_values and final_values[p.name] is not MISSING:
            error(parser, f"Аргумент для параметра '{p.name}' уже задан (именованный + позиционный)")

        if value is MISSING:
            # пропуск через , , - только если есть default
            if p.default is None:
                error(
                    parser,
                    f"Параметр '{p.name}' не может быть пропущен, у него нет значения по умолчанию"
                )
            # помечаем как MISSING, чтобы потом подставить default
            final_values[p.name] = MISSING
        else:
            final_values[p.name] = value

        param_index += 1

    # 3. Подставляем default и формируем результат
    for p in params:
        raw_value = final_values.get(p.name, MISSING)

        if raw_value is MISSING:
            if p.default is None:
                error(parser, f"Параметр '{p.name}' должен иметь аргумент или значение по умолчанию")
            if getattr(p, "type_key", None) == "enum":
                value = TypeString(p.default)
            else:
                value = p.default
        else:
            value = raw_value
        
        if getattr(p, "type_key", None) == "plural":
            if not isinstance(value, TypeList):
                value = TypeList([value])

        key = TypeString(p.name)
        result[key] = value
    

    return result


def parse_return(parser, amount):
    parser.eat(Tokens.MINUS)
    if parser.current.type != Tokens.GREATER: error(parser, "Ожидался знак >")
    parser.eat(Tokens.GREATER)

    returning_list = []
    while parser.current.type != Tokens.NEWLINE:
        returning = parse_expression(parser)
        if not isinstance(returning, TypeVariable): error(parser, "Ожидалась переменная для присвоения результата")
        returning_list.append(returning)

        if parser.current.type == Tokens.COMMA: parser.eat(Tokens.COMMA)
        else: break
    
    if len(returning_list) != int(amount): error(parser, f"Эта функция возвращает {amount} значений, а не {len(returning_list)}")
    
    variables = []
    for i in range(len(returning_list)):
        fake_token = Token(Tokens.LOCAL_VARIABLE, f"jmpc_return{i+1}", 0, 0)
        variables.append(TypeVariable(fake_token))
    

    return Action("variable", "set_variable_multiple", [
                  Argument("variables", TypeList(returning_list)), Argument("values", TypeList(variables))
                  ])