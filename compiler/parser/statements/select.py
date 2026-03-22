from compiler.lexer.tokens import Tokens
from compiler.ast.node import Select
from compiler.parser.core.parse_args import parse_all_arguments
from compiler.parser.core.condition import parse_condition
from compiler.utils.code.errors import error, check_method
from compiler.data.data_loader import load_json


ACTIONS_JSON = load_json("actions.json")

SELECT_ACTIONS = {}

for entry in ACTIONS_JSON:
    if entry.get("object") != "select":
        continue

    name = entry["name"]                 
    action_id = entry["id"]                
    args = entry.get("args", [])
    sel_type = entry.get("type", "basic") 

    SELECT_ACTIONS[name] = {
        "action": action_id,
        "args": args,
        "type": sel_type
    }




def parse_selector(parser):
    parser.eat(Tokens.SELECT)
    parser.eat(Tokens.DOT)

    name = parser.current.value
    if name not in SELECT_ACTIONS:
        if f"{name}_by_conditional" not in SELECT_ACTIONS:
            check_method(parser, name, SELECT_ACTIONS)
        name += "_by_conditional"


    entry = SELECT_ACTIONS[name]
    method = entry["action"]
    arg_metas = entry["args"]
    sel_type = entry["type"]

    parser.eat(parser.current.type)

    condition = None
    args = []

    if sel_type == "basic_with_conditional":
        parser.eat(Tokens.LPAREN)
        condition = parse_condition(parser, Tokens.RPAREN)
        parser.eat(Tokens.RPAREN)

    else:
        args = parse_all_arguments(parser, arg_metas, method)


    return Select(method, args, condition)