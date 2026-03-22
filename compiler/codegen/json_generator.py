from compiler.data.data_loader import load_json
from compiler.ast.node import Action, IfOperation, ElseOperation, Repeat, Controller, Select

from compiler.codegen.value import generate_value
from compiler.codegen.value_json import make_localized_text, make_enum
from compiler.codegen.extra.params import generate_parameter

from compiler.utils.code.errors import error


ACTIONS = load_json("actions.json")
ACTION_INDEX = {}
ACTIONS_BY_ID = {}
for action in ACTIONS:
    obj = action["object"]
    name = action["name"]
    ACTION_INDEX.setdefault(obj, {})[name] = action
    ACTIONS_BY_ID[action["id"]] = action


def generate_event(event):
    return {
        "type": "event",
        "event": event.name,
        "position": event.position,
        "operations": [generate_node(node, event.type) for node in event.body],
    }



def generate_definition(definition):
    values = []
    display = definition.display

    if "name" in display:
        values.append({"name": "display_name", "value": make_localized_text(display["name"].value)})
    if "hidden" in display:
        values.append({"name": "is_hidden", "value": make_enum(display["hidden"])})
    if "icon" in display:
        values.append({"name": "icon", "value": generate_value(display["icon"], None)})

    if definition.args:
        params_json = generate_parameter(definition.args)
        values.append({"name": "parameters", "value": {"type": "array", "values": params_json }})


    return {
        "type": definition.type,
        "name": definition.name,
        "values": values,
        "position": definition.position,
        "operations": [generate_node(node, definition.type) for node in definition.body]
    }



def generate_node(node, context):

    if isinstance(node, Action): return generate_action(node, context)
    if isinstance(node, IfOperation): return generate_if(node, context)
    if isinstance(node, ElseOperation): return generate_else(node, context)
    if isinstance(node, Repeat): return generate_while(node, context)
    if isinstance(node, Controller): return generate_controller(node, context)
    if isinstance(node, Select): return generate_select(node, context)

    error(node, "Неизвестный узел в json_generator.py")




def generate_action(action, context):
    selection = action.selection
    method = action.method
    action_meta = ACTIONS_BY_ID[method]

    # Генерация аргументов
    values = []
    for arg in action.args:
        if arg.value is not None:
            values.append(generate_argument(arg, action_meta, context))

    result = {
        "action": method,
        "values": values
    }
    if selection: result["selection"] = {"type": selection}

    return result









def generate_if(node, context):
    cond = node.condition

    action_meta = ACTIONS_BY_ID[cond.method]
    values = []
    for arg in cond.args:
        if arg.value is not None:
            values.append(generate_argument(arg, action_meta, context))

    result = {
        "action": cond.method,
        "values": values,
        "operations": [generate_node(op, context) for op in node.body]
    }

    if cond.selection: result["selection"] = {"type": cond.selection}
    if cond.inverted: result["is_inverted"] = True

    return result



def generate_else(node, context):
    result = {
        "action": "else",
        "values": [],
        "operations": [generate_node(op, context) for op in node.body]
    }
    
    # Если есть условие (else if)
    if node.condition is not None:
        cond = node.condition
        action_meta = ACTIONS_BY_ID[cond.method]
        
        values = []
        for arg in cond.args:
            if arg.value is not None:
                values.append(generate_argument(arg, action_meta, context))

        if values: result["values"] = values
        
        conditional = {
            "action": cond.method,
            "is_inverted": False
        }
        

        if cond.inverted: conditional["is_inverted"] = True
        
        result["conditional"] = conditional
    
    return result    





def generate_while(node, context):
    result = {
        "action": node.method,
        "values": [],
        "operations": [generate_node(op, context) for op in node.body]
    }

    if node.method == "repeat_forever": return result

    if node.method == "repeat_while":
        cond = node.condition
        action_meta = ACTIONS_BY_ID[cond.method]
        
        values = []
        for arg in cond.args:
            if arg.value is not None:
                values.append(generate_argument(arg, action_meta, context))

        if values: result["values"] = values
        
        conditional = {
            "action": cond.method,
            "is_inverted": False
        }
        
        if cond.inverted: conditional["is_inverted"] = True
        
        result["conditional"] = conditional

    else:

        action_meta = ACTIONS_BY_ID[node.method]
        
        values = []
        for arg in node.condition:
            if arg.value is not None:
                values.append(generate_argument(arg, action_meta, context))
        
        if values:
            result["values"] = values
    
    return result    


def generate_controller(node, context):
    action_meta = ACTIONS_BY_ID[node.method]
    values = []
    for arg in node.args:
        if arg.value is not None:
            values.append(generate_argument(arg, action_meta, context))

    return {
        "action": node.method,
        "values": values,
        "operations": [generate_node(op, context) for op in node.body]
    }



def generate_select(node, context):
    action_meta = ACTIONS_BY_ID[node.method]
    values = []
    for arg in node.args:
        if arg.value is not None:
            values.append(generate_argument(arg, action_meta, context))

    result = {
        "action": node.method,
        "values": values
    }

    if node.condition is not None:
        cond = node.condition
        cond_meta = ACTIONS_BY_ID[cond.method]

        cond_values = []
        for arg in cond.args:
            if arg.value is not None:
                cond_values.append(generate_argument(arg, cond_meta, context))

        result["conditional"] = {
            "action": cond.method,
            "is_inverted": cond.inverted if cond.inverted else False
        }

        if cond_values:
            result["values"] = cond_values

        if cond.selection:
            result["conditional"]["selection"] = {"type": cond.selection}

    return result













def generate_argument(arg, action_meta, context):

    arg_meta = next(
        (a for a in action_meta.get("args", []) if a["id"] == arg.name),
        None
    )

    if arg_meta is None: error(None, f"Неизвестный тип {arg.name} для действия {action_meta['id']}")
    
    value = generate_value(arg.value, context)

    return {
        "name": arg.name,
        "value": value
    }