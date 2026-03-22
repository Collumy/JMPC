from compiler.lexer.tokens import Tokens
from compiler.data.data_loader import load_json
from compiler.parser.expressions.expressions import parse_expression
from compiler.utils.code.errors import error, check_method
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


def parse_condition(parser, ends_with = Tokens.COLON):
    selection = None; inverted = None
    custom = True; target = "variable"

    # Инверсия (!)
    if (parser.current.type == Tokens.EXCLAMATION) or (parser.current.value == "not"):
        parser.eat(parser.current.type)
        inverted = True

    # player() / entity() / world()
    if parser.current.value in SELECTORS:
        custom = False
        target = SELECTORS[parser.current.value]
        parser.eat(Tokens.SELECTOR)

        # <all>
        if parser.current.type == Tokens.LESS:
            parser.eat(Tokens.LESS)
            selection = parser.current.value

            if target not in ("player", "entity"):
                error(parser, "У этого объекта не может быть цели")

            if target == "player":
                if selection in PLAYER_SELECTION: selection = PLAYER_SELECTION[selection]
                else: error(parser, f"Неизвестный селектор: {selection}, возможные: {", ".join([i for i in PLAYER_SELECTION])}")

            if target == "entity":
                if selection in ENTITY_SELECTION: selection = ENTITY_SELECTION[selection]
                else: error(parser, f"Неизвестный селектор: {selection}, возможные: {", ".join([i for i in ENTITY_SELECTION])}")
            
            parser.eat(parser.current.type)
            parser.eat(Tokens.GREATER)
        
        # (метод либо .метод
        if parser.current.type in (Tokens.LPAREN, Tokens.DOT):
            parser.eat(parser.current.type)
        else: error(parser, "Ожидалась точка или (")

    # if equals()
    if custom and parser.current.type == Tokens.IDENTIFIER:
        method1 = "if_variable_" + parser.current.value
        if method1 in ACTIONS: custom = False
        

    # собственно метод
    if not custom:
        method = parser.current.value
        if target == "player": method = "if_player_" + method
        if target == "entity": method = "if_entity_" + method
        if target == "world": method = "if_game_" + method
        if target == "variable": method = "if_variable_" + method

        parser.eat(Tokens.IDENTIFIER)
        check_method(parser, method, ACTIONS)

        arg_metas = ACTIONS[method]["values"]
        args = parse_all_arguments(parser, arg_metas, method, {})

        if parser.current.type == Tokens.RPAREN: parser.eat(Tokens.RPAREN)

        return Condition(target, method, args, inverted, selection)

















        # Кастомные условия
    else:
        ends_with_rparen = False
        if parser.current.type == Tokens.LPAREN:
            parser.eat(Tokens.LPAREN)
            ends_with_rparen = True
        value = parse_expression(parser)
        
        # Проверяем методы текста через точку
        if parser.current.type == Tokens.DOT:
            parser.eat(Tokens.DOT)
            method = parser.current.value

            if method == "contains":     method = "if_variable_text_contains"
            elif method == "startswith": method = "if_variable_text_starts_with"
            elif method == "endswith":   method = "if_variable_text_ends_with"
            elif method == "exists":     method = "if_variable_exists"
            else: error(parser, f"Неизвестный метод '{method}' для условия")
            parser.eat(Tokens.IDENTIFIER)
            parser.eat(Tokens.LPAREN)

            # собираем аргументы
            if method != "if_variable_exists":
                compare_values = []
                while parser.current.type != Tokens.RPAREN:
                    compare_values.append(parse_expression(parser))
                    if parser.current.type == Tokens.COMMA: parser.eat(Tokens.COMMA)
                    else: break

                args = [
                    Argument("value", value),
                    Argument("compare", TypeList(compare_values)),
                    Argument("ignore_case", TypeEnum("TRUE")),
                ]
            else:
                parser.eat(Tokens.RPAREN)
                args = [Argument("variable", value)]

            return Condition(target, method, args, inverted, selection)

        # списки словари
        if parser.current.value == "in":
            parser.eat(parser.current.type)
            args = []
            if parser.current.value == "list":
                method = "if_variable_list_contains_value"
            elif parser.current.value in ("map", "dict"):
                method = "if_variable_map_has_key"
            else: error(parser, "Ожидалось list() либо dict()")

            parser.eat(parser.current.type)
            parser.eat(Tokens.LPAREN)
            thing = parse_expression(parser)
            parser.eat(Tokens.RPAREN)

            if method == "if_variable_list_contains_value":
                args = [Argument("list", thing), Argument("values", value)]
            if method == "if_variable_map_has_key":
                args = [Argument("map", thing), Argument("key", value)]

            return Condition(target, method, args, inverted, selection)



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
        


        if ends_with_rparen: parser.eat(Tokens.RPAREN)
        if parser.current.type != ends_with: error(parser, f"Ожидалась {ends_with} для закрытия условия")
        

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