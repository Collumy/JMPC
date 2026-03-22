from compiler.ast.node import Action
from compiler.utils.code.errors import error
from compiler.lexer.tokens import Tokens
from compiler.parser.expressions.expressions import parse_expression
from compiler.parser.expressions.info import VARIABLES
from compiler.parser.core.parse_args import parse_all_arguments

from compiler.data.data_loader import load_json
METHOD_GROUPS = load_json("methods.json")

from difflib import get_close_matches

def handle_dot_method(parser, obj_type="list"):

    if parser.current.type not in VARIABLES:
        error(parser, "Ожидалась переменная перед точкой")

    first_var = parse_expression(parser)

    assigned_vars = []
    object_var = None

    if parser.current.type == Tokens.ASSIGN:
        parser.eat(Tokens.ASSIGN)        

        assigned_vars.append(first_var)
        object_var = parse_expression(parser)

    elif parser.current.type == Tokens.DOT:
        assigned_vars.append(first_var)
        object_var = first_var
    else: error(parser, "Ожидалось '=' или '.' после переменной")


    parser.eat(Tokens.DOT)

  

    if parser.current.type != Tokens.IDENTIFIER:
        error(parser, "Ожидалось имя метода после точки")

    method_name = parser.current.value
    parser.eat(Tokens.IDENTIFIER)

 
    if obj_type not in METHOD_GROUPS:
        error(parser, f"Тип '{obj_type}' не поддерживает методы")

    group = METHOD_GROUPS[obj_type]

    matched_method = None
    for method_key, meta in group.items():
        if method_name in meta["aliases"]:
            matched_method = meta
            break

    if matched_method is None:
        all_aliases = []
        for meta in group.values():
            all_aliases.extend(meta["aliases"])

        suggestions = get_close_matches(method_name, all_aliases, n=5, cutoff=0.4)

        if suggestions:
            error(parser, f"Метод '{method_name}' не найден. Возможно, вы имели в виду: {', '.join(suggestions)}")
        else:
            error(parser, f"Метод '{method_name}' не найден")


    if not "to_self" in matched_method:
        extra = {
            "first_non_variables": [object_var],  
            "first_variables": assigned_vars     
        }
    else:
        extra = {
            "first_variables": assigned_vars            
        }


    arg_metas = matched_method["args"]
    action_name = matched_method["action"]

    args = parse_all_arguments(parser, arg_metas, method_name, extra=extra)

    return Action("variable", action_name, args)