import json

def make_text(value, parsing="legacy"):
    return {
        "type": "text",
        "text": value,
        "parsing": parsing,
    }

def make_localized_text(value):

    data = {
        "translations": {},
        "fallback": {
            "rawText": value,
            "parsingType": "LEGACY"
        }
    }

    return {
        "type": "localized_text",
        "data": json.dumps(data, ensure_ascii=False)
    }


def make_number(value):
    return {
        "type": "number",
        "number": value,
    }

def make_variable(value, scope="line"):
    return {
        "type": "variable",
        "variable": value,
        "scope": scope
    }


def make_location(x, y, z, yaw, pitch):
    data = {
        "type": "location",
        "x": x,
        "y": y,
        "z": z,
        "yaw": yaw,
        "pitch": pitch
    }
    if yaw is not None:
        data["yaw"] = yaw
    if pitch is not None:
        data["pitch"] = pitch
    return data


def make_vector(x, y, z):
    return {
        "type": "vector",
        "x": x,
        "y": y,
        "z": z,
    }


def make_sound(sound, pitch, volume, variation, source):
    data = {
        "type": "sound",
        "sound": sound,
        "pitch": pitch,
        "volume": volume,
        "variation": variation,
        "source": source,
    }
    return data


def make_particle(args):
    data = {
        "type": "particle",
        "particle_type": args[0],
        "count": args[1],
        "first_spread": args[2],
        "second_spread": args[3],
    }

    extra = ["", "", '', '', "x_motion", "y_motion", "z_motion", "material", "color", "size", "to_color"]
    for i in range(4,10):
        if args[i] != "-666" and args[i] != -666:
            print(extra[i], args[i])
            data[extra[i]] = args[i]
    print(data)
    return data


def make_potion(potion, amplifier, duration):
    return {
        "type": "potion",
        "potion": potion,
        "amplifier": amplifier,
        "duration": duration,
    }


def make_gamevalue(name, selection):
    return {
        "type": "game_value",
        "game_value": name,
        "selection": selection,
    }

def make_enum(value):
    return {
        "type": "enum",
        "enum": value,
    }

def make_item(item_base64):
    return {
        "type": "item",
        "item": item_base64,
    }


def make_array(values):
    return {
        "type": "array",
        "values": values,
    }


def make_map(values):
    return {
        "type": "map",
        "values": values,
    }


def make_empty():
    return {}
