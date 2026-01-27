from compiler.lexer.tokens import Tokens
from compiler.data_loader import load_json
from compiler.parser.expressions.expressions import parse_expression
from compiler.utils.errors import error
from compiler.ast.node import Argument, Condition
from compiler.ast.expressions import TypeList, TypeEnum, TypeVariable
from compiler.parser.core.parse_args import parse_all_arguments

from compiler.parser.expressions.info import SELECTORS, PLAYER_SELECTION, ENTITY_SELECTION, VARIABLES
from difflib import get_close_matches

ACTIONS1 = load_json("actions.json")
ACTIONS = {}
for action in ACTIONS1:
    id = action["id"]
    values = action["args"]
    ACTIONS[id] = {"id": id, "values": values}


def parse_condition(parser):
    selection = None
    custom = True
    inverted = None
    target = "variable"

    # player() / entity() / world()
    if parser.current.type != Tokens.LESS and parser.current.type != Tokens.LPAREN:
        custom = None
        if parser.current.value not in SELECTORS: 
            error(parser, "Ожидался player() entity() world(), но получено другое")
        target = SELECTORS[parser.current.value]
        parser.eat(parser.current.type)

    # <all>
    if parser.current.type == Tokens.LESS:
        parser.eat(Tokens.LESS)
        if parser.current.type != Tokens.VARIABLE: 
            error(parser, "Ожидался селектор в <>")
        selection = parser.current.value
        parser.eat(Tokens.VARIABLE)
        if parser.current.type != Tokens.GREATER: 
            error(parser, "Ожидался > для закрытия селектора")
        parser.eat(Tokens.GREATER)

    # Проверяем селектор
    if selection:
        if target not in ("player", "entity"):
            error(parser, "У этого объекта не может быть цели")

        if target == "player":
            if selection in PLAYER_SELECTION: 
                selection = PLAYER_SELECTION[selection]
            else: 
                error(parser, f"Неизвестный селектор: <{selection}>")

        if target == "entity":
            if selection in ENTITY_SELECTION: 
                selection = ENTITY_SELECTION[selection]
            else: 
                error(parser, f"Неизвестный селектор: <{selection}>")

    # Само действие 
    if parser.current.type != Tokens.LPAREN: 
        error(parser, "Ожидалась ( для условия")
    parser.eat(Tokens.LPAREN)

    # Инверсия (!)
    if parser.current.type == Tokens.EXCLAMATION:
        parser.eat(Tokens.EXCLAMATION)
        inverted = True
    if parser.current.type in VARIABLES and parser.current.value == "not":
        parser.eat(parser.current.type)
        inverted = True

    if not custom:
        # Стандартное условие
        method = parser.current.value
        if target == "player": method = "if_player_" + method
        if target == "entity": method = "if_entity_" + method
        if target == "world": method = "if_game_" + method
        if target == "variable": method = "if_variable_" + method

        parser.eat(Tokens.IDENTIFIER)
        
        if method not in ACTIONS:
            suggestions = get_close_matches(method, ACTIONS.keys(), 5, 0.3)
            msg = f"Действие {method} не найдено"

            if suggestions:
                msg += "\nВозможно, вы имели в виду:\n"
                for s in suggestions: msg += f"   - {s}\n"

            error(parser,msg)
        
        arg_metas = ACTIONS[method]["values"]

        args = parse_all_arguments(parser, arg_metas, method, {})

        if parser.current.type != Tokens.RPAREN: 
            error(parser, "Ожидалась ) после аргументов")
        parser.eat(Tokens.RPAREN)

        return Condition(target, method, args, inverted, selection)

















        # Кастомные условия
    else:

        value = parse_expression(parser)
        
        # Проверяем методы текста через точку
        if parser.current.type == Tokens.DOT:
            parser.eat(Tokens.DOT)
            
            method_name = parser.current.value
            if parser.current.type != Tokens.IDENTIFIER: error(parser, "Ожидалось имя метода после точки")
            parser.eat(Tokens.IDENTIFIER)
            
            # text.contains(...)
            if method_name in ("contains", "has", "includes"):
                method = "if_variable_text_contains"
                
                if parser.current.type != Tokens.LPAREN: error(parser, "Ожидалась ( после метода")
                parser.eat(Tokens.LPAREN)
                
                # Собираем значения для проверки
                compare_values = []
                if parser.current.type != Tokens.RPAREN:
                    while True:
                        compare_values.append(parse_expression(parser))
                        if parser.current.type == Tokens.COMMA: parser.eat(Tokens.COMMA)
                        else: break
                
                if parser.current.type != Tokens.RPAREN: error(parser, "Ожидалась ) после аргументов")
                parser.eat(Tokens.RPAREN)
                parser.eat(Tokens.RPAREN)
                
                args = [
                    Argument("value", value),
                    Argument("compare", TypeList(compare_values)),
                    Argument("ignore_case", TypeEnum("TRUE"))
                ]
                
                return Condition(target, method, args, inverted, selection)
            
            # text.startswith(...)
            elif method_name in ("startswith", "starts_with", "begins_with"):
                method = "if_variable_text_starts_with"
                
                if parser.current.type != Tokens.LPAREN:
                    error(parser, "Ожидалась ( после метода")
                parser.eat(Tokens.LPAREN)
                
                compare_values = []
                if parser.current.type != Tokens.RPAREN:
                    while True:
                        compare_values.append(parse_expression(parser))
                        if parser.current.type == Tokens.COMMA: parser.eat(Tokens.COMMA)
                        else: break
                
                if parser.current.type != Tokens.RPAREN: error(parser, "Ожидалась ) после аргументов")
                parser.eat(Tokens.RPAREN)
                parser.eat(Tokens.RPAREN)
                
                args = [
                    Argument("value", value),
                    Argument("compare", TypeList(compare_values)),
                    Argument("ignore_case", TypeEnum("TRUE"))
                ]
                
                return Condition(target, method, args, inverted, selection)
            
            # text.endswith(...)
            elif method_name in ("endswith", "ends_with"):
                method = "if_variable_text_ends_with"
                
                if parser.current.type != Tokens.LPAREN:
                    error(parser, "Ожидалась ( после метода")
                parser.eat(Tokens.LPAREN)
                
                compare_values = []
                if parser.current.type != Tokens.RPAREN:
                    while True:
                        compare_values.append(parse_expression(parser))
                        if parser.current.type == Tokens.COMMA: parser.eat(Tokens.COMMA)
                        else:  break
                
                if parser.current.type != Tokens.RPAREN:
                    error(parser, "Ожидалась ) после аргументов")
                parser.eat(Tokens.RPAREN)
                parser.eat(Tokens.RPAREN)
                
                args = [
                    Argument("value", value),
                    Argument("compare", TypeList(compare_values)),
                    Argument("ignore_case", TypeEnum("TRUE"))
                ]
                
                return Condition(target, method, args, inverted, selection)
            
            else:
                error(parser, f"Неизвестный метод '{method_name}' для условия")
    

        operator = None
        method = None
        
        if parser.current.type == Tokens.EQUAL:  # ==
            operator = "=="
            method = "if_variable_equals"
            parser.eat(Tokens.EQUAL)
        
        elif parser.current.type == Tokens.NOT_EQUAL:  # !=
            operator = "!="
            method = "if_variable_not_equals"
            parser.eat(Tokens.NOT_EQUAL)
        
        elif parser.current.type == Tokens.GREATER_EQUAL:  # >=
            operator = ">="
            method = "if_variable_greater_or_equals"
            parser.eat(Tokens.GREATER_EQUAL)
        
        elif parser.current.type == Tokens.LESS_EQUAL:  # <=
            operator = "<="
            method = "if_variable_less_or_equals"
            parser.eat(Tokens.LESS_EQUAL)
        
        elif parser.current.type == Tokens.GREATER:  # >
            operator = ">"
            method = "if_variable_greater"
            parser.eat(Tokens.GREATER)
        
        elif parser.current.type == Tokens.LESS:  # <
            operator = "<"
            method = "if_variable_less"
            parser.eat(Tokens.LESS)
        
        else:
            error(parser, f"Ожидался оператор сравнения (==, !=, >, <, >=, <=), но получено: {parser.current}")
        
        # Парсим правую часть (значения для сравнения)
        compare_values = []
        
        # Первое значение
        compare_values.append(parse_expression(parser))
        
        # Дополнительные значения через запятую (для == и !=)
        while parser.current.type == Tokens.COMMA:
            if operator not in ("==", "!="):
                error(parser, f"Оператор '{operator}' не поддерживает несколько значений")
            
            parser.eat(Tokens.COMMA)
            compare_values.append(parse_expression(parser))
        

        if parser.current.type != Tokens.RPAREN:
            error(parser, "Ожидалась ) для закрытия условия")
        parser.eat(Tokens.RPAREN)

        args = []
        
        if operator in ("==", "!="):
            args.append(Argument("value", value))
            args.append(Argument("compare", TypeList(compare_values)))
        
        elif operator in (">", ">=", "<", "<="):
            if len(compare_values) > 1:
                error(parser, f"Оператор '{operator}' принимает только одно значение для сравнения")
            
            args.append(Argument("value", value))
            args.append(Argument("compare", compare_values[0]))
        
        return Condition(target, method, args, inverted, selection)