import json
import os

DATA_DIR = os.path.dirname(__file__)
VALUES_CACHE = {}

def load_json(file: str):
    if not file.endswith(".json"): file += ".json"
    if file in VALUES_CACHE: return VALUES_CACHE[file]

    for root, dirs, files in os.walk(DATA_DIR):
        if file in files:
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf8") as f:
                data = json.load(f)
                VALUES_CACHE[file] = data
                return data
    raise FileNotFoundError(f"Файл '{file}' не найден в {DATA_DIR}")
