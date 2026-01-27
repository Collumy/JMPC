import gzip
import base64
import struct
from io import BytesIO
import re
from typing import Dict, List, Union, Any



HEX_COLOR_PATTERN = re.compile(r'&#([0-9A-Fa-f]{6})')
AMPERSAND_COLOR_PATTERN = re.compile(r'&([0-9a-fk-or])', re.IGNORECASE)



def convert_colors(text: str) -> str:
    """
    Конвертирует цветовые коды:
    - &a → §a
    - &#FFAA00 → §x§F§F§A§A§0§0
    """
    if not isinstance(text, str):
        return text

    # &a → §a
    text = AMPERSAND_COLOR_PATTERN.sub(r'§\1', text)

    # &#FFAA00 → §x§F§F§A§A§0§0
    def hex_repl(match):
        return "§x" + "".join(f"§{c}" for c in match.group(1))

    text = HEX_COLOR_PATTERN.sub(hex_repl, text)

    return text



def write_utf(out: BytesIO, text: str) -> None:
    """Записывает UTF-8 строку с префиксом длины."""
    encoded = text.encode("utf-8")
    out.write(struct.pack(">H", len(encoded)))
    out.write(encoded)


def write_tag(out: BytesIO, name: str, value: Any) -> None:
    """Записывает NBT-тег в зависимости от типа значения."""
    value_type = type(value)
    

    if value_type in (int, float):
        out.write(b'\x03')  # TAG_Int
        write_utf(out, name)
        out.write(struct.pack(">i", int(value)))
    
 
    elif value_type is str:
        out.write(b'\x08')  # TAG_String
        write_utf(out, name)
        write_utf(out, value)
    

    elif value_type is list:
        out.write(b'\x09')  # TAG_List
        write_utf(out, name)
        
        if len(value) == 0:
            # Пустой список → TAG_End
            out.write(b'\x00')  # element type
            out.write(struct.pack(">i", 0))  # length
        else:
            # Определяем тип элементов
            first_type = type(value[0])
            
            if first_type is str:
                out.write(b'\x08')  # TAG_String
            elif first_type in (int, float):
                out.write(b'\x03')  # TAG_Int
            elif first_type is dict:
                out.write(b'\x0A')  # TAG_Compound
            else:
                raise ValueError(f"Неподдерживаемый тип элемента списка: {first_type.__name__}")
            
            out.write(struct.pack(">i", len(value)))
            
            for item in value:
                if first_type is str:
                    write_utf(out, item)
                elif first_type in (int, float):
                    out.write(struct.pack(">i", int(item)))
                elif first_type is dict:
                    write_compound(out, item)
                    out.write(b'\x00')
    

    elif value_type is dict:
        out.write(b'\x0A')  # TAG_Compound
        write_utf(out, name)
        write_compound(out, value)
        out.write(b'\x00')  # TAG_End
    
    else:
        raise ValueError(f"Неподдерживаемый тип NBT: {value_type.__name__}")


def write_compound(out: BytesIO, data: Dict[str, Any]) -> None:
    """Записывает NBT Compound."""
    for key, value in data.items():
        write_tag(out, key, value)


def generate_item(args: Union[Dict[str, Any], List]) -> str:

    if isinstance(args, dict):
        item_id = args.get("id")
        name = args.get("name", "")
        count = args.get("count", 1)
        lore = args.get("lore", [])
        nbt = args.get("nbt", {})
        tags = args.get("tags", {})
    else:
        # Дополняем до 6 элементов
        args = list(args) + [None] * (6 - len(args))
        item_id, name, count, lore, nbt, tags = args
        name = name or ""
        count = count if count is not None else 1
        lore = lore or []
        nbt = nbt or {}
        tags = tags or {}

    name = convert_colors(name) if name else ""
    lore = [convert_colors(line) for line in lore] if lore else []

    components = build_components(name, lore, nbt, tags)

    data = {"id": item_id, "count": int(count)}
    if components:
        data["components"] = components

    return serialize_nbt(data)


def build_components(name: str, lore: List[str], nbt: Dict, tags: Dict) -> Dict:
    """Собирает словарь компонентов предмета."""
    components = {}

    if tags:
        public_bukkit_values = {
            f"justcreativeplus:{key}": str(value)
            for key, value in tags.items()
        }
        components["minecraft:custom_data"] = {
            "PublicBukkitValues": public_bukkit_values
        }

    if name:
        components["minecraft:custom_name"] = name

    if lore:
        components["minecraft:lore"] = lore

    if nbt:
        if "minecraft:custom_data" not in components:
            components["minecraft:custom_data"] = {}
        components["minecraft:custom_data"].update(nbt)

    return components


def serialize_nbt(data: Dict) -> str:
    """Сериализует NBT в Base64 GZIP."""
    raw = BytesIO()
    
    # ✅ Корневой compound tag
    raw.write(b'\x0A')
    write_utf(raw, "")
    write_compound(raw, data)
    raw.write(b'\x00')

    # ✅ GZIP + Base64
    gzipped = gzip.compress(raw.getvalue())
    return base64.b64encode(gzipped).decode("utf-8")