import re
from compiler.utils.code.errors import error

TOKEN_REGEX = re.compile(
    r"""
    \s*
    (
        %[A-Za-z0-9_]+%          |   # %player%
        `[^`]*`                  |   # `любой текст`
        \d+                      |   # числа
        [A-Za-z_][A-Za-z0-9_]*   |   # идентификаторы
        [{}+\-*/%()

\[\]

,?:&|<>=!] |  # одиночные символы синтаксиса/операторов
        .                            # остальные одиночные символы
    )
    """,
    re.VERBOSE
)

def tokenize(text):
    tokens = []
    raw_tokens = TOKEN_REGEX.findall(text)
    i = 0

    while i < len(raw_tokens):
        tok = raw_tokens[i]

        # %player%
        if tok.startswith("%") and tok.endswith("%") and tok != "%":
            tokens.append(("RAW", tok))
            i += 1
            continue

        # `name`
        if tok.startswith("`") and tok.endswith("`"):
            inner = tok[1:-1]
            tokens.append(("BACKTICK", inner))
            i += 1
            continue

        # число
        if tok.isdigit():
            tokens.append(("NUMBER", tok))
            i += 1
            continue

        # идентификатор (возможный prefix`name`)
        if re.match(r"[A-Za-z_][A-Za-z0-9_]*$", tok):
            if (
                i + 1 < len(raw_tokens)
                and raw_tokens[i + 1].startswith("`")
                and raw_tokens[i + 1].endswith("`")
            ):
                prefix = tok
                name = raw_tokens[i + 1][1:-1]
                tokens.append(("PREFIXVAR", (prefix, name)))
                i += 2
                continue

            # обычный идентификатор
            tokens.append(("IDENT", tok))
            i += 1
            continue

        # всё остальное — символ
        tokens.append(("SYMBOL", tok))
        i += 1

    return tokens


class Number:
    def __init__(self, value): self.value = value

class Raw:
    def __init__(self, text): self.text = text

class Var:
    def __init__(self, scope, name):
        self.scope = scope
        self.name = name

class Call:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Index:
    def __init__(self, base, index):
        self.base = base
        self.index = index

class Entry:
    def __init__(self, base, key):
        self.base = base
        self.key = key


def resolve_scope(prefix):
    if prefix in ("i", "line"): return "_line"
    if prefix in ("l", "local"): return "_local"
    if prefix in ("g", "game"): return ""
    if prefix in ("s", "save"): return "_save"
    return prefix

def default_scope(context):
    if context == "event": return "_local"
    if context in ("function", "process"): return "_line"
    return "_local"


class ExprParser:
    def __init__(self, tokens, outer_parser):
        self.tokens = tokens
        self.outer = outer_parser
        self.context = getattr(outer_parser, "context", "function")
        self.i = 0

    def peek(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else None

    def eat(self, kind=None, value=None):
        tok = self.peek()
        if not tok:
            error(self.outer, "Неожиданный конец выражения")

        if kind and tok[0] != kind:
            error(self.outer, f"Ожидался токен {kind}, получено {tok}")

        if value and tok[1] != value:
            error(self.outer, f"Ожидался символ '{value}', получено '{tok[1]}'")

        self.i += 1
        return tok

    def parse(self):
        nodes = []
        while self.peek():
            # останавливаемся на закрывающих скобках — их обрабатывает внешний код
            if self.peek()[0] == "SYMBOL" and self.peek()[1] in (")", "]", "}", ","):
                break
            nodes.append(self.parse_atom_or_op())
        return nodes

    def parse_atom_or_op(self):
        tok = self.peek()
        if not tok:
            error(self.outer, "Неожиданный конец выражения")

        kind, val = tok

        # RAW — просто текст
        if kind == "RAW":
            self.eat("RAW")
            return Raw(val)

        # prefix`name`
        if kind == "PREFIXVAR":
            prefix, name = val
            self.eat("PREFIXVAR")
            scope = resolve_scope(prefix)
            node = Var(scope, name)
            return self.parse_postfix(node)

        # `name`
        if kind == "BACKTICK":
            self.eat("BACKTICK")
            scope = default_scope(self.context)
            node = Var(scope, val)
            return self.parse_postfix(node)

        # число
        if kind == "NUMBER":
            self.eat("NUMBER")
            return Number(val)

        # идентификатор: либо вызов, либо просто текст
        if kind == "IDENT":
            ident = val
            self.eat("IDENT")
            # вызов функции
            if self.peek() and self.peek()[0] == "SYMBOL" and self.peek()[1] == "(":
                self.eat("SYMBOL", "(")
                args = []
                if not (self.peek() and self.peek()[0] == "SYMBOL" and self.peek()[1] == ")"):
                    args = self.parse_args()
                self.eat("SYMBOL", ")")
                node = Call(ident, args)
                return self.parse_postfix(node)
            # просто сырой текст (например, часть выражения)
            return Raw(ident)

        # (expr)
        if kind == "SYMBOL" and val == "(":
            self.eat("SYMBOL", "(")
            inner_nodes = self.parse()
            self.eat("SYMBOL", ")")
            # скобки сохраняем как текст
            return Raw("(" + "".join(emit(n) for n in inner_nodes) + ")")

        # любой другой символ — оператор, оставляем как текст
        if kind == "SYMBOL":
            self.eat("SYMBOL")
            return Raw(val)

        error(self.outer, f"Неожиданный токен {tok}")

    def parse_postfix(self, node):
        while True:
            tok = self.peek()
            if not tok:
                return node

            kind, val = tok

            # A[B]
            if kind == "SYMBOL" and val == "[":
                self.eat("SYMBOL", "[")
                idx_nodes = self.parse()
                self.eat("SYMBOL", "]")
                idx = Raw("".join(emit(n) for n in idx_nodes))
                node = Index(node, idx)
                continue

            # A{B}
            if kind == "SYMBOL" and val == "{":
                self.eat("SYMBOL", "{")
                key_nodes = self.parse()
                self.eat("SYMBOL", "}")
                key = Raw("".join(emit(n) for n in key_nodes))
                node = Entry(node, key)
                continue

            break

        return node

    def parse_args(self):
        args = [self.parse()]
        while self.peek() and self.peek()[0] == "SYMBOL" and self.peek()[1] == ",":
            self.eat("SYMBOL", ",")
            args.append(self.parse())
        return args


def emit(node):
    if isinstance(node, Number):
        return node.value

    if isinstance(node, Raw):
        return node.text

    if isinstance(node, Var):
        return f"%var{node.scope}({node.name})"

    if isinstance(node, Index):
        base = node.base
        idx = emit(node.index)
        if isinstance(base, Var):
            return f"%index{base.scope}({base.name},{idx})"
        return f"%index({emit(base)},{idx})"

    if isinstance(node, Entry):
        base = node.base
        key = emit(node.key)
        if isinstance(base, Var):
            return f"%entry{base.scope}({base.name},{key})"
        return f"%entry({emit(base)},{key})"

    if isinstance(node, Call):
        name = node.name
        # args — это списки узлов, сначала их склеиваем
        args = ["".join(emit(n) for n in arg) for arg in node.args]

        if name == "math":
            return f"%math({args[0]})"

        if name in ("value", "val"):
            return f"%val({args[0]})"

        if name == "len":
            first = node.args[0][0] if node.args and node.args[0] else None
            if isinstance(first, Var):
                v = first
                return f"%length{v.scope}({v.name})"
            error(node, "Ожидалась переменная, получено другое")

        return f"{name}({','.join(args)})"

    raise RuntimeError("Неизвестный тип AST-узла")


PLACEHOLDER_RE = re.compile(r"(?<!\\)\${(.*?)}\$", re.DOTALL)
SIMPLE_PLACEHOLDER_RE = re.compile(r"(?<!\\)\$(?!\{)([^\s$]+)")


def placeholders(text, parser):
    def repl(match):
        inner = match.group(1)
        tokens = tokenize(inner)
        expr_parser = ExprParser(tokens, parser)
        nodes = expr_parser.parse()
        return "".join(emit(n) for n in nodes)

    def simple_repl(match):
        inner = match.group(1)
        tokens = tokenize(inner)
        expr_parser = ExprParser(tokens, parser)
        nodes = expr_parser.parse()
        return "".join(emit(n) for n in nodes)

    text = PLACEHOLDER_RE.sub(repl, text)
    text = SIMPLE_PLACEHOLDER_RE.sub(simple_repl, text)

    text = text.replace(r"\$", "$")

    return PLACEHOLDER_RE.sub(repl, text)