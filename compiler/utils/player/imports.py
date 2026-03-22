import os
from compiler.utils.code.errors import error

IMPORTED_FILES = set()
IMPORT_STACK = []


def warn_cycle(path):
    print(f"[Warning] Циклический импорт: {' -> '.join(IMPORT_STACK + [path])}")


def expand_imports(text, base_path):
    lines = text.splitlines()
    result = []

    for line in lines:
        stripped = line.strip()

        # -----------------------------
        # import file / import a.b.c
        # -----------------------------
        if stripped.startswith("import "):
            import_name = stripped[len("import "):].strip()

            rel_path = import_name.replace(".", "/") + ".jp"
            full_path = os.path.join(base_path, rel_path)

            if full_path in IMPORT_STACK:
                warn_cycle(full_path)
                continue

            if full_path in IMPORTED_FILES:
                continue

            IMPORT_STACK.append(full_path)

            try:
                with open(full_path, "r", encoding="utf8") as f:
                    imported_text = f.read()
            except FileNotFoundError:
                raise error(None, f"Файл '{rel_path}' не найден")

            imported_text = expand_imports(imported_text, os.path.dirname(full_path))

            IMPORT_STACK.pop()
            IMPORTED_FILES.add(full_path)

            result.append(imported_text)
            continue

        # -----------------------------
        # from file import func1, func2
        # -----------------------------
        if stripped.startswith("from "):
            rest = stripped[len("from "):].strip()
            file_part, sep, import_part = rest.partition(" import ")

            if not sep:
                raise error(None, "Ожидалось 'import' после from <file>")

            import_names = [x.strip() for x in import_part.split(",") if x.strip()]

            rel_path = file_part.replace(".", "/") + ".jp"
            full_path = os.path.join(base_path, rel_path)

            if full_path in IMPORT_STACK:
                warn_cycle(full_path)
                continue

            try:
                with open(full_path, "r", encoding="utf8") as f:
                    imported_text = f.read()
            except FileNotFoundError:
                raise error(None, f"Файл '{rel_path}' не найден")

            IMPORT_STACK.append(full_path)
            imported_text = expand_imports(imported_text, os.path.dirname(full_path))
            IMPORT_STACK.pop()

            extracted = extract_definitions(imported_text, import_names)
            result.append(extracted)
            continue

        # обычная строка
        result.append(line)

    return "\n".join(result)


def extract_definitions(text, names):
    lines = text.splitlines()
    result = []

    capture = False
    buffer = []

    for line in lines:
        stripped = line.strip()

        # начало определения
        if stripped.startswith(("function ", "def ", "process ", "proc ")):
            if buffer:
                result.append("\n".join(buffer))
                buffer = []

            parts = stripped.split()
            if len(parts) >= 2 and parts[1] not in names:
                capture = True
                buffer.append(line)
            else:
                capture = False
            continue

        if capture:
            buffer.append(line)

    if buffer:
        result.append("\n".join(buffer))
    
    return "\n\n".join(result)