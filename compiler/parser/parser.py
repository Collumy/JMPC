from compiler.lexer.tokens import Tokens
from compiler.parser.statements.starts.event import parse_event
from compiler.parser.statements.starts.definition import parse_definition
from compiler.utils.define import parse_define
from compiler.utils.errors import error

from compiler.lexer.lexer import Lexer
from compiler.utils.imports import expand_imports

class Parser:
    def __init__(self, lexer, text, file_path="."):
        expanded = expand_imports(text, file_path)
        self.text = expanded
        self.lines = expanded.splitlines()

        self.lexer = Lexer(expanded)
        self.current = self.lexer.get_next_token()
        self.buffer = []

    def eat(self, expected_type):
        if self.current.type != expected_type:
            error(self, f"Ожидался токен {expected_type}, но получен {self.current.type}")
        if self.buffer:
            self.current = self.buffer.pop(0)
        else:
            self.current = self.lexer.get_next_token()

    def peek(self, offset=1):
        if offset == 0:
            return self.current
        while len(self.buffer) < offset:
            tok = self.lexer.get_next_token()
            self.buffer.append(tok)
        return self.buffer[offset - 1]

    
    def get_line(self, line_number):
        if 1 <= line_number <= len(self.lines):
            return self.lines[line_number - 1]
        return ""

    def parse(self):
        starts = []
        while self.current.type != Tokens.EOF:

            if self.current.type in (Tokens.NEWLINE, Tokens.DEDENT):
                self.eat(self.current.type)
                continue

            if self.current.type in (Tokens.EVENT, Tokens.FUNCTION, Tokens.PROCESS):
                if self.current.type == Tokens.EVENT: starts.append(parse_event(self))
                else: starts.append(parse_definition(self))
                continue

            if self.current.type == Tokens.DEFINE:
                parse_define(self)
                continue

            error(self, f"Ожидалось event/function/process, но получено другое")


        return starts