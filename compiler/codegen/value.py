from compiler.ast.expressions import (
    FunctionCall,
    TypeDict,
    TypeList,
    TypeNumber,
    TypeString,
    TypeVariable,
    TypeEnum,
    NamedArgumentNode
)

from compiler.codegen.value_json import (
    make_text,
    make_number,
    make_array,
    make_map,
    make_location,
    make_vector,
    make_sound,
    make_potion,
    make_item,
    make_gamevalue,
    make_particle,
)

from compiler.codegen.extra.variables import generate_variable
from compiler.codegen.extra.items import generate_item
from compiler.parser.expressions.placeholders import placeholders
from compiler.data_loader import load_json
from compiler.utils.errors import error
import json


# Загрузка данных
POTIONS = load_json("potions.json")
SOUNDS_SOURCES = load_json("sound_sources.json")
PARTICLES = load_json("particles.json")
ITEMS = load_json("items.json")
GAMEVALUES = load_json("gamevalues.json")
VALUES = {v["id"] for v in GAMEVALUES}
VALUES_SELECTORS = load_json("gamevalues_selectors.json")


class Arg:
    __slots__ = ('type', 'required', 'default', 'name')
    
    def __init__(self, type, *, required=False, default=None, name=None):
        self.type = type
        self.required = required
        self.default = default
        self.name = name


FUNCTION_SIGNATURES = {
    "num": [Arg("text", required=True, name="expr")],
    
    "location": [
        Arg("number", default=0, name="x"),
        Arg("number", default=0, name="y"),
        Arg("number", default=0, name="z"),
        Arg("number", default=0, name="yaw"),
        Arg("number", default=0, name="pitch"),
    ],
    
    "vector": [
        Arg("number", default=0, name="x"),
        Arg("number", default=0, name="y"),
        Arg("number", default=0, name="z"),
    ],
    
    "potion": [
        Arg("text", default="speed", name="id"),
        Arg("number", default=0, name="level"),
        Arg("number", default=-1, name="duration"),
    ],
    
    "sound": [
        Arg("text", required=True, name="sound"),
        Arg("number", default=1, name="volume"),
        Arg("number", default=1, name="pitch"),
        Arg("text", default="", name="variation"),
        Arg("text", default="MASTER", name="source"),
    ],
    
    "item": [
        Arg("text", required=True, name="id"),
        Arg("text", default="", name="name"),
        Arg("number", default=1, name="count"),
        Arg("list", default=[], name="lore"),
        Arg("dict", default={}, name="nbt"),
        Arg("dict", default={}, name="tags")
    ],
    
    "value": [
        Arg("text", required=True, name="id"),
        Arg("text", default="null", name="selector")
    ],
    
    "particle": [
        Arg("text", required=True, name="id"),
        Arg("number", default=1, name="count"),
        Arg("number", default=0, name="spread_x"),
        Arg("number", default=0, name="spread_y"),
        Arg("number", default=-666, name="motion_x"),
        Arg("number", default=-666, name="motion_y"),
        Arg("number", default=-666, name="motion_z"),
        Arg("text", default="-666", name="material"),
        Arg("number", default=-666, name="color"),
        Arg("number", default=-666, name="size"),
        Arg("number", default=-666, name="to_color")
    ]
}


DEFAULT_VALUES = {
    "number": lambda v: make_number(v),
    "text": lambda v: make_text(v),
    "list": lambda v: make_array([]),
    "dict": lambda v: make_map({})
}


def parse_args(node, context, signature):
    positional = []
    named = {}

    for arg_node in node.args:
        if isinstance(arg_node, NamedArgumentNode):
            named[arg_node.name] = generate_value(arg_node.value, context)
        else:
            positional.append(generate_value(arg_node, context))

    result = []

    for i, arg_def in enumerate(signature):
        if arg_def.name in named:
            value = named[arg_def.name]
        elif i < len(positional):
            value = positional[i]
        elif not arg_def.required:
            default_func = DEFAULT_VALUES.get(arg_def.type)
            value = default_func(arg_def.default) if default_func else arg_def.default
        else:
            error(node, f"Отсутствует обязательный аргумент '{arg_def.name}'")

        validate_arg_type(node, arg_def, value)
        
        if arg_def.type == "number":
            value = value["number"]
        elif arg_def.type == "text":
            value = value["text"]

        result.append(value)

    return result


def validate_arg_type(node, arg_def, value):
    type_map = {
        "number": "number",
        "text": "text",
        "list": "array",
        "dict": "map"
    }
    
    expected_type = type_map.get(arg_def.type)
    if expected_type and value.get("type") != expected_type:
        error(node, f"Аргумент '{arg_def.name}' должен быть типа {arg_def.type}, получен {value.get('type')}")


def extract_raw_value(value_json):
    """Конвертирует JSON-представление значения в Python-значение."""
    value_type = value_json.get("type")
    
    if value_type == "text":
        return value_json.get("text", "")
    
    if value_type == "number":
        return value_json.get("number", 0)
    
    if value_type == "array":
        return [extract_raw_value(item) for item in value_json.get("values", [])]
    
    if value_type == "map":
        result = {}
        values_dict = value_json.get("values", {})
        for key_json_str, val_json in values_dict.items():
            key_data = json.loads(key_json_str)
            key = extract_raw_value(key_data)
            result[key] = extract_raw_value(val_json)
        return result
    
    if value_type == "variable":
        error(None, "Переменные в item() не поддерживаются как сырые значения")
    
    return value_json


FUNCTION_HANDLERS = {}

def register_handler(name):
    def decorator(func):
        FUNCTION_HANDLERS[name] = func
        return func
    return decorator


@register_handler("num")
def handle_num(node, context, args):
    expr = placeholders("$<math(" + args[0] + ")>", None)
    return make_number(expr)


@register_handler("location")
def handle_location(node, context, args):
    return make_location(*args)


@register_handler("vector")
def handle_vector(node, context, args):
    return make_vector(*args)


@register_handler("potion")
def handle_potion(node, context, args):
    potion_id, level, duration = args
    if potion_id not in POTIONS:
        error(node, f"Неизвестное зелье '{potion_id}'")
    return make_potion(potion_id, level, duration)


@register_handler("sound")
def handle_sound(node, context, args):
    sound_id, volume, pitch, variation, source = args
    if source not in SOUNDS_SOURCES:
        error(node, f"Недопустимый источник звука '{source}'")
    return make_sound(sound_id, pitch, volume, variation, source)


@register_handler("particle")
def handle_particle(node, context, args):
    if args[0] not in PARTICLES:
        error(node, f"Недопустимый айди частицы '{args[0]}'")
    return make_particle(args)


@register_handler("item")
def handle_item(node, context, args):
    positional = []
    named = {}

    for arg_node in node.args:
        if isinstance(arg_node, NamedArgumentNode):
            named[arg_node.name] = generate_value(arg_node.value, context)
        else:
            positional.append(generate_value(arg_node, context))

    item_args = {}
    arg_names = ["id", "name", "count", "lore", "nbt", "tags"]
    
    for i, name in enumerate(arg_names):
        if name in named:
            item_args[name] = extract_raw_value(named[name])
        elif i < len(positional):
            item_args[name] = extract_raw_value(positional[i])

    if "id" not in item_args:
        error(node, "Отсутствует обязательный аргумент 'id' для item()")

    if item_args["id"] not in ITEMS:
        error(node, f"Недопустимый айди предмета '{item_args['id']}'")

    item = generate_item(item_args)
    return make_item(item)


@register_handler("value")
def handle_value(node, context, args):
    value_id, selector = args
    
    if value_id not in VALUES:
        error(node, f"Недопустимое игровое значение '{value_id}'")

    if selector in VALUES_SELECTORS:
        selector = f'{{"type":"{VALUES_SELECTORS[selector]}"}}'
    elif selector != "null":
        error(node, f"Недопустимый селектор '{selector}'")

    return make_gamevalue(value_id, selector)


def generate_function_call(node, context):
    name = node.name.lower()

    if name not in FUNCTION_SIGNATURES:
        error(node, f"Неизвестная функция {name}()")

    args = parse_args(node, context, FUNCTION_SIGNATURES[name])
    
    handler = FUNCTION_HANDLERS.get(name)
    if handler:
        return handler(node, context, args)
    
    error(node, f"Функция {name}() не реализована")


def generate_value(node, context):
    if isinstance(node, FunctionCall):
        return generate_function_call(node, context)
    
    if isinstance(node, NamedArgumentNode):
        return generate_value(node.value, context)

    if isinstance(node, TypeList):
        return make_array([generate_value(item, context) for item in node.items])

    if isinstance(node, TypeDict):
        result = {}
        # ✅ node.items это список [(key, value), ...]
        for k, v in node.items:
            key_json = generate_value(k, context)
            key_str = json.dumps(key_json, ensure_ascii=False)
            result[key_str] = generate_value(v, context)
        return make_map(result)

    if isinstance(node, TypeString):
        return make_text(node.value, parsing=getattr(node, "parsing", "legacy"))

    if isinstance(node, TypeNumber):
        return make_number(node.value)

    if isinstance(node, TypeVariable):
        return generate_variable(node.token, context)
    
    if isinstance(node, TypeEnum):
        result = {"type": "enum", "enum": node.value}
        
        if node.variable is not None:
            var = generate_variable(node.variable.token, context)
            result["variable"] = var["variable"]
            result["scope"] = var["scope"]
        
        return result

    error(node, f"Неизвестный тип значения: {type(node).__name__}")