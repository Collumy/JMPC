from compiler.lexer.tokens import Tokens, Token
from compiler.lexer.keywords import KEYWORDS, VAR_PREFIXES, SELECTORS
from compiler.utils.code.errors import error

BRACKET_TOKENS = {
    '(': (Tokens.LPAREN, 'paren_depth', 1),
    ')': (Tokens.RPAREN, 'paren_depth', -1),
    '{': (Tokens.LBRACE, 'brace_depth', 1),
    '}': (Tokens.RBRACE, 'brace_depth', -1),
    '[': (Tokens.LBRACKET, 'bracket_depth', 1),
    ']': (Tokens.RBRACKET, 'bracket_depth', -1),
}

TWO_CHAR_TOKENS = {
    '+=': Tokens.PLUS_ASSIGN,
    '-=': Tokens.MINUS_ASSIGN,
    '*=': Tokens.STAR_ASSIGN,
    '/=': Tokens.SLASH_ASSIGN,
    '%=': Tokens.PERCENT_ASSIGN,
    '^=': Tokens.POW_ASSIGN,
    '++': Tokens.PLUS_PLUS,
    '--': Tokens.MINUS_MINUS,

    '::': Tokens.DOUBLE_COLON,

    '==': Tokens.EQUAL,
    '<=': Tokens.LESS_EQUAL,
    '>=': Tokens.GREATER_EQUAL,
    '!=': Tokens.NOT_EQUAL,
}

ONE_CHAR_TOKENS = {
    '=': Tokens.ASSIGN,
    '+': Tokens.PLUS,
    '-': Tokens.MINUS,
    '*': Tokens.STAR,
    '/': Tokens.SLASH,
    '%': Tokens.PERCENT,
    "^": Tokens.POW,

    '.': Tokens.DOT,
    ',': Tokens.COMMA,
    ':': Tokens.COLON,
    '!': Tokens.EXCLAMATION,

    '<': Tokens.LESS,
    '>': Tokens.GREATER
}



class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = text[0] if text else None
        #для ошибок
        self.line = 1
        self.column = 0

        self.indent_stack = [0]    # список уровней отступов
        self.pending_dedents = 0   # сколько DEDENT нужно выдать
        self.at_line_start = True  # мы в начале строки

        self.paren_depth = 0
        self.bracket_depth = 0
        self.brace_depth = 0
 
    # ---------------------------
    # Базовые функции
    # ---------------------------

    def advance(self):
        if self.current_char == "\n":
            self.line += 1
            self.column = 0
            self.at_line_start = True
        else:
            self.column += 1

        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def peek(self):
        pos = self.pos + 1
        if pos < len(self.text):
            return self.text[pos]
        return None
    
    # ---------------------------
    # Комментарии
    # ---------------------------

    def skip_line_comment(self):
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
    
    def skip_block_comment(self):
        self.advance()  # /
        self.advance()  # *
        
        while self.current_char is not None:
            if self.current_char == '*' and self.peek() == '/':
                self.advance(); self.advance(); return
            self.advance()
        error(self, "Незакрытый многострочный комментарий /* */")

    def is_empty_line(self):
        pos = self.pos
        while pos < len(self.text):
            ch = self.text[pos]
            if ch == '\n': return True
            if ch == '/' and pos + 1 < len(self.text):
                if self.text[pos + 1] == '/': return True
                if self.text[pos + 1] == '*': return True
            if ch == '#': return True
            if ch != ' ': return False
            pos += 1
        return True

    def is_empty_or_comment_line(self):
        pos = self.pos
        
        while pos < len(self.text) and self.text[pos] in (' ', '\t'): pos += 1
        if pos >= len(self.text): return True 
        
        ch = self.text[pos]
        if ch == '\n': return True 
        if ch == '#': return True 
        
        if ch == '/' and pos + 1 < len(self.text):
            next_ch = self.text[pos + 1]
            if next_ch == '/': return True 
            if next_ch == '*': return True  
        return False  

    # ---------------------------------------
    # Отступы
    # ---------------------------------------


    # Считает количество пробелов в начале строки
    def count_indent(self):
        count = 0
        pos = self.pos
        while pos < len(self.text) and self.text[pos] == " ":
            count += 1
            pos += 1
        return count
    
    # Генерирует INDENT/DEDENT как питончик
    def handle_indent(self):
        if not self.at_line_start: return None

        if self.paren_depth > 0 or self.brace_depth > 0 or self.bracket_depth > 0:
            while self.current_char == " ":
                self.advance()
            self.at_line_start = False
            return None
        
        if self.pending_dedents > 0:
            self.pending_dedents -= 1
            if self.pending_dedents == 0: self.at_line_start = False
            return Token(Tokens.DEDENT, None, self.line, self.column)

        indent = self.count_indent()
        last_indent = self.indent_stack[-1]

        if indent > last_indent:
            self.indent_stack.append(indent)
            while self.current_char == " ": self.advance()
            self.at_line_start = False
            return Token(Tokens.INDENT, indent, self.line, self.column)
        

        elif indent < last_indent:
            # вычисляем сколько DEDENT нужно выдать
            dedent_count = 0
            while len(self.indent_stack) > 1 and indent < self.indent_stack[-1]:
                self.indent_stack.pop()
                dedent_count += 1

            if len(self.indent_stack) > 0 and indent != self.indent_stack[-1]:
                error(self, f"Некорректный отступ {indent} пробелов (ожидалось {self.indent_stack[-1]})")

            # пропускаем пробелы
            while self.current_char == " ":
                self.advance()

            #  Выдаём первый DEDENT, остальные в pending
            if dedent_count > 0:
                self.pending_dedents = dedent_count - 1
                self.at_line_start = False
                return Token(Tokens.DEDENT, None, self.line, self.column)
        
        else:
            while self.current_char == " ": self.advance()
            self.at_line_start = False
            return None




    # ---------------------------------------------------------
    # Строки
    # ---------------------------------------------------------

    def make_backtick_variable(self):
        self.advance()
        result = ""
        while self.current_char is not None and self.current_char != "`":
            result += self.current_char
            self.advance()
        if self.current_char != "`":
            error(self, "Неожиданный символ `")
        self.advance()
        return result

    def make_string(self):
        if self.current_char in ('l', 'p', 'm', 'j') and self.peek() == '"':
            types = {'p': "plain", 'l': "legacy", 'm': "minimessage", 'j': "json"}

            parsing = types[self.current_char]
            self.advance()
            self.advance()  # начало текста
        elif self.current_char == '"':
            parsing = "legacy"
            self.advance()  # начало текста
        else:
            error(self, "Строка не начинается с ''")

        # Собираем содержимое строки
        result = []
        while self.current_char is not None and self.current_char != '"':
            result.append(self.current_char)
            self.advance()

        # Закрывающая кавычка
        if self.current_char == '"':
            self.advance()

        text = "".join(result)
        token = Token(Tokens.STRING, text, self.line, self.column)
        token.parsing = parsing
        return token

    # ---------------------------------------------------------
    # Числа: 5, 5.23, 2.0E100
    # ---------------------------------------------------------

    def make_number(self):
        result = []
        has_dot = False
        has_exp = False

        if self.current_char == "-":
            result.append("-"); self.advance()

        while self.current_char is not None:
            ch = self.current_char

            if ch.isdigit():
                result.append(ch)
            elif ch == '.' and not has_dot and not has_exp:
                has_dot = True
                result.append(ch)
            elif ch in ('e', 'E') and not has_exp:
                has_exp = True
                result.append(ch)
            else:
                break

            self.advance()

        return Token(Tokens.NUMBER, "".join(result), self.line, self.column)

    # ---------------------------------------------------------
    # Идентификатор
    # ---------------------------------------------------------

    def make_identifier(self):
        result = ""
        while (
            self.current_char is not None
            and (self.current_char.isalnum() or self.current_char in "_")
        ):
            result += self.current_char
            self.advance()

        return result
    
    # ---------------------------------------------------------
    # Главная функция
    # ---------------------------------------------------------

    def get_next_token(self):
        # сначала выдаём накопленные DEDENT
        if self.pending_dedents > 0:
            self.pending_dedents -= 1
            return Token(Tokens.DEDENT, None, self.line, self.column)

        while self.current_char is not None:
            if self.at_line_start:
                if self.is_empty_or_comment_line():
                    while self.current_char in (' ', '\t'):
                        self.advance()
                    
                    # Пропускаем комментарий если есть
                    if (self.current_char == '/' and self.peek() == '/') or self.current_char == "#":
                        self.skip_line_comment()
                    
                    if self.current_char == '/' and self.peek() == '*':
                        self.skip_block_comment()
                    
                    # Пропускаем \n
                    if self.current_char == '\n':
                        self.advance()
                        continue
                
                tok = self.handle_indent()
                if tok: return tok

            if (self.current_char == '/' and self.peek() == '/') or self.current_char == "#":
                self.skip_line_comment()
                continue
            
            if self.current_char == '/' and self.peek() == '*':
                self.skip_block_comment()
                continue

            # Обратный слэш в конце строки — продолжение строки
            if self.current_char == '\\' and self.peek() == '\n':
                self.advance()
                self.advance()
                continue

            if self.current_char == ';':
                self.advance()
                while self.current_char == ' ': self.advance()
                
                if self.paren_depth > 0 or self.bracket_depth > 0 or self.brace_depth > 0:
                    return Token(Tokens.NL, ';', self.line, self.column)
                
                return Token(Tokens.NEWLINE, ';', self.line, self.column)

            # новая строка
            if self.current_char == '\n':
                self.advance()

                # внутри скобок - NL
                if self.paren_depth > 0 or self.bracket_depth > 0 or self.brace_depth > 0:
                    self.at_line_start = True
                    return Token(Tokens.NL, '\\n', self.line, self.column)

                self.at_line_start = True
                return Token(Tokens.NEWLINE, '\\n', self.line, self.column)

            # пробелы
            if self.current_char == " ":
                if self.paren_depth > 0 or self.bracket_depth > 0 or self.brace_depth > 0:
                    while self.current_char == " ":
                        self.advance()
                    continue

                if not self.at_line_start:
                    self.advance()
                    continue

            # Строки: "" l"" p"" m"", j""
            if self.current_char in ('l', 'p', 'm', 'j') and self.peek() == '"': 
                return self.make_string()
            if self.current_char == '"':
                return self.make_string()

            # Числа
            if self.current_char.isdigit():
                return self.make_number()
            if self.current_char == "-" and self.peek() and self.peek().isdigit():
                return self.make_number()

            # Переменные `var`
            if self.current_char == "`":
                name = self.make_backtick_variable()
                return Token(Tokens.VARIABLE, name, self.line, self.column)

            # Идентификаторы (переменные, служебные слова, селекторы, функции)
            if self.current_char.isalpha() or self.current_char == "_":
                ident = self.make_identifier()
                
                if ident in KEYWORDS: return Token(KEYWORDS[ident], ident, self.line, self.column)
                if ident in SELECTORS: return Token(Tokens.SELECTOR, ident, self.line, self.column)

                if self.current_char == "(": return Token(Tokens.IDENTIFIER, ident, self.line, self.column)
                
                if ident in VAR_PREFIXES and self.current_char == "`":
                    var_type = VAR_PREFIXES[ident]; name = self.make_backtick_variable()
                    return Token(var_type, name, self.line, self.column)

                return Token(Tokens.VARIABLE, ident, self.line, self.column)

            # Символы
            ch = self.current_char
            next_ch = self.peek()

            if ch in BRACKET_TOKENS:
                token_type, depth_attr, depth_change = BRACKET_TOKENS[ch]
                self.advance()

                current_depth = getattr(self, depth_attr)
                setattr(self, depth_attr, current_depth + depth_change)
                return Token(token_type, ch, self.line, self.column)

            if next_ch:
                two_char = ch + next_ch
                if two_char in TWO_CHAR_TOKENS:
                    self.advance(); self.advance()
                    return Token(TWO_CHAR_TOKENS[two_char], two_char, self.line, self.column)
            
            if ch in ONE_CHAR_TOKENS:
                self.advance()
                return Token(ONE_CHAR_TOKENS[ch], ch, self.line, self.column)

            # Если встретился неизвестный символ
            error(self, f"Неожиданный символ: {ch!r}")
            
        # в конце файла — выдаём все оставшиеся DEDENT
        if len(self.indent_stack) > 1:
            self.indent_stack.pop()
            return Token(Tokens.DEDENT, None, self.line, self.column)

        return Token(Tokens.EOF, None, self.line, self.column)