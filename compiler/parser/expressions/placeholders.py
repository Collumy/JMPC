import re
from compiler.utils.errors import error

# ============================================================
# 1. Токенизация
# ============================================================

import re

TOKEN_REGEX = re.compile(
    r"""
    \s*
    (
        %[A-Za-z0-9_]+%          |   # %player%
        `[^`]*`                  |   # `любой текст`
        \d+                      |   # числа
        [A-Za-z_][A-Za-z0-9_]*   |   # идентификаторы
        [{}+\-*/%()\[\]]         |   # одиночные символы синтаксиса
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

        # --- RAW %player% ---
        if tok.startswith("%") and tok.endswith("%") and tok != "%":
            tokens.append(("RAW", tok))
            i += 1
            continue

        # --- BACKTICK `любой текст` ---
        if tok.startswith("`") and tok.endswith("`"):
            inner = tok[1:-1]
            tokens.append(("BACKTICK", inner))
            i += 1
            continue

        # --- NUMBER ---
        if tok.isdigit():
            tokens.append(("NUMBER", tok))
            i += 1
            continue

        # --- IDENT (возможный prefix для prefix`name`) ---
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

            # Обычный идентификатор
            tokens.append(("IDENT", tok))
            i += 1
            continue

        # --- ОДИНОЧНЫЕ СИМВОЛЫ СИНТАКСИСА ---
        if tok in "{}+-*/()[]":
            tokens.append(("SYMBOL", tok))
            i += 1
            continue
        
        # --- ВСЁ ОСТАЛЬНОЕ — SYMBOL ---
        tokens.append(("SYMBOL", tok))
        i += 1

    return tokens






class Number:
    def __init__(self, value):
        self.value = value

class Ident:
    def __init__(self, name):
        self.name = name

class Raw:
    def __init__(self, text):
        self.text = text

class Var:
    def __init__(self, scope, name):
        self.scope = scope
        self.name = name

class Call:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Binary:
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

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

    # expr = term (("+"|"-") term)*
    def parse_expr(self):
        node = self.parse_term()
        while True:
            tok = self.peek()
            if tok and tok[0] == "SYMBOL" and tok[1] in "+-":
                op = tok[1]
                self.eat("SYMBOL", op)
                right = self.parse_term()
                node = Binary(op, node, right)
            else:
                break
        return node

    # term = factor (("*"|"/") factor)*
    def parse_term(self):
        node = self.parse_factor()
        while True:
            tok = self.peek()
            if tok and tok[0] == "SYMBOL" and tok[1] in "*/%^":
                op = tok[1]
                self.eat("SYMBOL", op)
                right = self.parse_factor()
                node = Binary(op, node, right)
            else:
                break
        return node

    # factor = RAW | PREFIXVAR | BACKTICK | NUMBER | IDENT | IDENT(...) | "(" expr ")"
    def parse_factor(self):
        tok = self.peek()
        if not tok:
            error(self.outer, "Неожиданный конец выражения")

        # %player%
        if tok[0] == "RAW":
            self.eat("RAW")
            return Raw(tok[1])

        # prefixname — lhp, gPlayer, sLevel
        if tok[0] == "PREFIXVAR":
            prefix, name = tok[1]
            self.eat("PREFIXVAR")
            scope = resolve_scope(prefix)
            node = Var(scope, name)
            return self.parse_postfix(node)

        # любой текст — имя переменной целиком
        if tok[0] == "BACKTICK":
            self.eat("BACKTICK")
            name = tok[1]
            scope = default_scope(self.context)
            node = Var(scope, name)
            return self.parse_postfix(node)

        # число
        if tok[0] == "NUMBER":
            self.eat("NUMBER")
            return Number(tok[1])

        # идентификатор
        if tok[0] == "IDENT":
            ident = tok[1]
            self.eat("IDENT")

            # вызов функции
            if self.peek() and self.peek()[0] == "SYMBOL" and self.peek()[1] == "(":
                self.eat("SYMBOL", "(")
                args = self.parse_args()
                self.eat("SYMBOL", ")")
                node = Call(ident, args)
                return self.parse_postfix(node)

            # простая переменная
            scope = default_scope(self.context)
            node = Var(scope, ident)
            return self.parse_postfix(node)

        # (expr)
        if tok[0] == "SYMBOL" and tok[1] == "(":
            self.eat("SYMBOL", "(")
            node = self.parse_expr()
            self.eat("SYMBOL", ")")
            return self.parse_postfix(node)

        error(self.outer, f"Неожиданный токен {tok}")

    # postfix: только один [ ] или один { }, но внутри { } можно всё
    def parse_postfix(self, node):
        tok = self.peek()
        if not tok:
            return node

        # A[B]
        if tok[0] == "SYMBOL" and tok[1] == "[":
            self.eat("SYMBOL", "[")
            idx = self.parse_expr()
            self.eat("SYMBOL", "]")
            return Index(node, idx)

        # A{B}
        if tok[0] == "SYMBOL" and tok[1] == "{":
            self.eat("SYMBOL", "{")
            key = self.parse_expr()
            self.eat("SYMBOL", "}")
            return Entry(node, key)

        return node

    # args = expr ("," expr)*
    def parse_args(self):
        args = [self.parse_expr()]
        while self.peek() and self.peek()[0] == "SYMBOL" and self.peek()[1] == ",":
            self.eat("SYMBOL", ",")
            args.append(self.parse_expr())
        return args




def emit(node):
    if isinstance(node, Number):
        return node.value

    if isinstance(node, Ident):
        return node.name

    if isinstance(node, Raw):
        return node.text

    if isinstance(node, Var):
        return f"%var{node.scope}({node.name})"

    if isinstance(node, Binary):
        return f"{emit(node.left)}{node.op}{emit(node.right)}"

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
        args = [emit(a) for a in node.args]

        if name == "math":
            return f"%math({args[0]})"

        if name in ("value", "val"):
            return f"%val({args[0]})"

        if name == "min":
            if len(args) <= 2:
                return f"min({','.join(args)})"
            expr = f"min({args[-2]},{args[-1]})"
            for i in range(len(args) - 3, -1, -1):
                expr = f"min({args[i]},{expr})"
            return expr

        if name == "max":
            if len(args) <= 2:
                return f"max({','.join(args)})"
            expr = f"max({args[-2]},{args[-1]})"
            for i in range(len(args) - 3, -1, -1):
                expr = f"max({args[i]},{expr})"
            return expr

        if name == "clamp":
            if len(args) == 3:
                return f"min(max({args[0]},{args[1]}),{args[2]})"
            return f"clamp({','.join(args)})"

        if name == "len":
            if len(node.args) == 1 and isinstance(node.args[0], Var):
                v = node.args[0]
                return f"%length{v.scope}({v.name})"
            return f"len({args[0]})"

        return f"{name}({','.join(args)})"

    raise RuntimeError("Неизвестный тип AST-узла")





PLACEHOLDER_RE = re.compile(r"\$<(.*?)>", re.DOTALL)

def placeholders(text, parser):

    def repl(match):
        inner = match.group(1)
        tokens = tokenize(inner)
        expr_parser = ExprParser(tokens, parser)
        ast = expr_parser.parse_expr()
        return emit(ast)

    return PLACEHOLDER_RE.sub(repl, text)
