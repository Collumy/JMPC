from compiler.ast.expressions import TypeDict, TypeVariable, TypeString
from compiler.lexer.tokens import Token
from compiler.codegen.value import generate_value
import copy


GLOBAL_JMPC_COUNTER = 1


def continue_handler(start_json):
    ops = start_json["operations"]
    rows, funcs = pack_into_continuations(ops, 40)

    flat_ops = []
    for row in rows:
        flat_ops.extend(row)
    
    start_json["operations"] = flat_ops
    handlers = [start_json]

    for name, body in funcs:
        handlers.append({
            "type": "function",
            "name": name,
            "operations": body,
            "values": []
        })
    
    return handlers


def block_weight(block: dict) -> int:
    if "operations" in block:
        base = 2
        for bl in block["operations"]:
            base += block_weight(bl)
        return base
    return 1


def collect_line_variables(blocks):
    vars_used = set()

    for block in blocks:
        for values in block.get("values", []):
            val = values["value"]
            if "values" not in val:
                val = [val]
            else:
                val = val["values"]

            for v in val:
                if v["type"] == "variable" and v["scope"] == "line":
                    vars_used.add(v["variable"])

    return vars_used


def is_piston(block: dict) -> bool:
    return "operations" in block


def clone_block(block: dict) -> dict:
    return copy.deepcopy(block)


def create_call_block(func_name):
    return {
        "action": "call_function",
        "values": [
            {"name": "function_name", "value": {"type": "text", "parsing": "legacy", "text": func_name}},
            {"name": "args", "value": {"type": "map", "values": {}}}
        ]
    }


def create_variable_save_block(vars_used):
    jmpc_lines = {}
    for var in vars_used:
        fake_token = Token("LINE_VARIABLE", var, 0, 0)
        jmpc_lines[TypeString(var)] = TypeVariable(fake_token)
    
    jmpc_lines = generate_value(TypeDict(jmpc_lines), None)

    return {
        "action": "set_variable_value",
        "values": [
            {"name": "variable", "value": {"type": "variable", "variable": "jmpc_lines", "scope": "local"}},
            {"name": "value", "value": jmpc_lines}
        ]
    }


def create_variable_restore_block():
    return {
        "action": "repeat_for_each_map_entry",
        "values": [
            {"name": "map", "value": {"type": "variable", "variable": "jmpc_lines", "scope": "local"}},
            {"name": "key_variable", "value": {"type": "variable", "variable": "jmpc_key", "scope": "line"}},
            {"name": "value_variable", "value": {"type": "variable", "variable": "jmpc_value", "scope": "line"}}
        ],
        "operations": [
            {
                "action": "set_variable_value",
                "values": [
                    {"name": "variable", "value": {"type": "variable", "variable": "%var_line(jmpc_key)", "scope": "line"}},
                    {"name": "value", "value": {"type": "variable", "variable": "jmpc_value", "scope": "line"}}
                ]
            }
        ]
    }


def pack_into_continuations(blocks, limit):
    rows = []
    functions = []
    current = []
    current_weight = 0

    i = 0
    while i < len(blocks):
        block = blocks[i]
        
        if is_piston(block):
            ops = block.get("operations", [])
            
            if len(ops) == 0:
                weight = block_weight(block)
                if current_weight + weight <= limit:
                    current.append(block)
                    current_weight += weight
                    i += 1
                    continue
            
            else:
                full_weight = block_weight(block)
                
                if current_weight + full_weight <= limit:
                    inner_limit = limit - 2 - 1
                    if inner_limit < 1:
                        inner_limit = 1
                    
                    sub_rows, sub_funcs = pack_into_continuations(ops, inner_limit)
                    
                    if len(sub_rows) > 1:
                        first_row = list(sub_rows[0])
                        
                        global GLOBAL_JMPC_COUNTER
                        inner_func_name = f"jmpc_cont{GLOBAL_JMPC_COUNTER}"
                        GLOBAL_JMPC_COUNTER += 1
                        
                        first_row.append(create_call_block(inner_func_name))
                        
                        block = clone_block(block)
                        block["operations"] = first_row
                        
                        inner_func_body = []
                        for row in sub_rows[1:]:
                            inner_func_body.extend(row)
                        
                        functions.append((inner_func_name, inner_func_body))
                        functions.extend(sub_funcs)
                    
                    else:
                        block = clone_block(block)
                        block["operations"] = sub_rows[0] if sub_rows else []
                        functions.extend(sub_funcs)
                    
                    weight = block_weight(block)
                    current.append(block)
                    current_weight += weight
                    i += 1
                    continue
                
                else:
                    empty_piston_weight = 2 + 1
                    
                    if current_weight + empty_piston_weight <= limit:
                        inner_func_name = f"jmpc_cont{GLOBAL_JMPC_COUNTER}"
                        GLOBAL_JMPC_COUNTER += 1
                        
                        empty_piston = clone_block(block)
                        empty_piston["operations"] = [create_call_block(inner_func_name)]
                        
                        current.append(empty_piston)
                        current_weight += empty_piston_weight
                        
                        sub_rows, sub_funcs = pack_into_continuations(ops, limit)
                        
                        inner_func_body = []
                        for row in sub_rows:
                            inner_func_body.extend(row)
                        
                        functions.append((inner_func_name, inner_func_body))
                        functions.extend(sub_funcs)
                        
                        i += 1
                        continue
        
        weight = block_weight(block)

        if current_weight + weight <= limit:
            current.append(block)
            current_weight += weight
            i += 1
            continue

        func_name = f"jmpc_cont{GLOBAL_JMPC_COUNTER}"
        GLOBAL_JMPC_COUNTER += 1

        vars_used = collect_line_variables(current)

        if len(vars_used) > 0:
            current.append(create_variable_save_block(vars_used))

        current.append(create_call_block(func_name))
        rows.append(current)

        func_body = []
        if len(vars_used) > 0:
            func_body.append(create_variable_restore_block())

        func_body.append(block)
        func_body.extend(blocks[i+1:])

        sub_rows, sub_funcs = pack_into_continuations(func_body, limit)

        flat_body = []
        for row in sub_rows:
            flat_body.extend(row)

        functions.append((func_name, flat_body))
        functions.extend(sub_funcs)

        return rows, functions

    if current:
        rows.append(current)

    return rows, functions