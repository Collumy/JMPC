from compiler.codegen.value import generate_value
from compiler.codegen.value_json import make_localized_text
from compiler.ast.params import EnumParameter, PluralParameter, SingularParameter, EnumElement
import json

def generate_parameter(args):
    params_json = []

    for index, param in enumerate(args):
        if isinstance(param, SingularParameter): params_json.append(generate_single(param))
        if isinstance(param, PluralParameter): params_json.append(generate_multi(param))
        if isinstance(param, EnumParameter): params_json.append(generate_enum(param))

    return params_json


# Одиночный параметр
def generate_single(param):
    if param.default is None:
        default_json = "{}"
        required = "true"
    else:
        dv = generate_value(param.default, None)
        default_json = json.dumps(dv, ensure_ascii=False)
        required = "false"

    if param.display_name:
        desc_json = make_localized_text(param.display_name)["data"]
    else:
        desc_json = "{\"translations\":{}}"

    return {
        "type": "parameter",
        "type_key": param.type_key,
        "description": desc_json,
        "name": param.name,
        "value_type": param.value_type,
        "is_required": required,
        "default_value": default_json,
        "slot": param.slot,
        "description_slot": param.desc_slot
    }

# Множественный параметр
def generate_multi(param):
    if param.default is None:
        default_json = "{}"
        required = "true"
    else:
        dv = generate_value(param.default, None)
        default_json = json.dumps(dv, ensure_ascii=False)
        required = "false"
    
    if param.display_name:
        desc_json = make_localized_text(param.display_name)["data"]
    else:
        desc_json = "{\"translations\":{}}"
    
    return {
        "type": "parameter",
        "type_key": param.type_key,
        "description": desc_json,
        "name": param.name,
        "value_type": param.value_type,
        "is_required": required,
        "ignore_empty_values": param.ignore_empty,
        "default_value": default_json,
        "slots": param.slots,
        "description_slots": param.desc_slots
    }

# Маркер
def generate_enum(param):
    if param.display_name:
        desc_json = make_localized_text(param.display_name)["data"]
    else:
        desc_json = "{\"translations\":{}}"


    elements_json = []
    elements_names = []
    for el in param.elements:

        el_json = {"name": el.name}

        if el.display_name: el_json["display_name"] = json.loads(make_localized_text(el.display_name)["data"])
        else: el_json["display_name"] = {"translations":{}}

        if el.icon:
            el_json["icon"] = generate_value(el.icon, None)["item"] 
        else:
            el_json["icon"] = "H4sIAAAAAAAA/+NiYGBm4HZJLEkMSy0qzszPY2AQjOBgYMpMYZDKzcxLTS5KTCuxykhNLCqJz0+LL8lIjS9OTWRmYE3OL80rYWBgYGQAAOJSs3VDAAAA"

        el_json_string = json.dumps(el_json, ensure_ascii=False)
        elements_json.append(el_json_string)

        elements_names.append(el.name)
    
    elements_json = json.dumps(elements_json, ensure_ascii=False)

    return {
        "type": "parameter",
        "type_key": param.type_key,
        "description": desc_json,
        "name": param.name,
        "slot": param.slot,
        "elements": elements_json,
        "default_element": param.default
    }
