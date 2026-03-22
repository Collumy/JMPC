from enum import Enum, auto

class Tokens(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return count

    EVENT = auto()           # event
    FUNCTION = auto()        # function
    PROCESS = auto()         # process

    IMPORT = auto()          # import *
    FROM = auto()            # from * import *
    DEFINE = auto()          # define print = player.message

    SELECTOR = auto()        # селектор.
    IF = auto()              # if
    ELSE = auto()            # else
    ELIF = auto()            # elif
    WHILE = auto()           # while
    FOR = auto()             # for

    CODE_CONTROL = auto()    # break continue stop exit return wait()
    CONTROLLER = auto()      # controller.
    IDENTIFIER = auto()      # функция()
    CUSTOM = auto()          # custom.
    SELECT = auto()          # select.

    LPAREN = auto()          # (
    RPAREN = auto()          # )
    LBRACKET = auto()        # [
    RBRACKET = auto()        # ]
    LBRACE = auto()          # {
    RBRACE = auto()          # }
 
    DOT = auto()             # .
    COMMA = auto()           # ,
    COLON = auto()           # :
    DOUBLE_COLON = auto()    # ::
    SEMICOLON = auto()       # ;
    BACKTICK = auto()        # `
    EXCLAMATION = auto()     # !

    PLUS = auto()            # +
    MINUS = auto()           # -
    STAR = auto()            # *
    SLASH = auto()           # /
    PERCENT = auto()         # %
    POW = auto()             # ^

    EQUAL = auto()           # ==
    PLUS_ASSIGN = auto()     # +=
    MINUS_ASSIGN = auto()    # -=
    STAR_ASSIGN = auto()     # *=
    SLASH_ASSIGN = auto()    # /=
    PERCENT_ASSIGN = auto()  # %/
    POW_ASSIGN = auto()      # ^=
    PLUS_PLUS = auto()       # ++
    MINUS_MINUS = auto()     # --

    ASSIGN = auto()          # =
    NOT_EQUAL = auto()       # !=
    LESS = auto()            # <
    GREATER = auto()         # >
    LESS_EQUAL = auto()      # <=
    GREATER_EQUAL = auto     # >=

    VARIABLE = auto()        # переменная
    LINE_VARIABLE = auto()   # строчная переменная
    LOCAL_VARIABLE = auto()  # локальная переменная
    GAME_VARIABLE = auto()   # игровая переменная
    SAVE_VARIABLE = auto()   # сохранённая переменная

    STRING = auto()          # тип: текст
    NUMBER = auto()          # тип: число

    NEWLINE = auto()         # конец строки
    NL = auto()              # перенос строки внутри скобок
    INDENT = auto()          # увеличение уровня отступа
    DEDENT = auto()          # уменьшение уровня отсутпа

    EOF = auto()             # конец файла

class Token():
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column


# Для ошибок
TOKENS_TEXT = {
    Tokens.EVENT: "event",
    Tokens.FUNCTION: "function",
    Tokens.PROCESS: "process",
    Tokens.IMPORT: "import",
    Tokens.FROM: "from",
    Tokens.DEFINE: "define",
    Tokens.SELECTOR: "selector",
    Tokens.IF: "if",
    Tokens.ELSE: "else",
    Tokens.ELIF: "elif",
    Tokens.WHILE: "while",
    Tokens.FOR: "for",
    Tokens.CODE_CONTROL: "wait",
    Tokens.CONTROLLER: "controller",
    Tokens.IDENTIFIER: "метод()",
    Tokens.CUSTOM: "custom",
    Tokens.SELECT: "select",

    Tokens.LPAREN: "Левая круглая скобка ‹(›",
    Tokens.RPAREN: "Правая круглая скобка ‹)›",
    Tokens.LBRACKET: "Левая квадратная скобка ‹[›",
    Tokens.RBRACKET: "Правая квадратная скобка ‹]›",
    Tokens.LBRACE: "Левая фигурная скобка ‹{›",
    Tokens.RBRACE: "Правая фигурная скобка ‹}›",

    Tokens.DOT: "Точка ‹.›",
    Tokens.COMMA: "Запятая ‹,›",
    Tokens.COLON: "Двоеточие ‹:›",
    Tokens.DOUBLE_COLON: "Двойное двоеточие ‹::›",
    Tokens.SEMICOLON: "Точка с запятой ‹;›",
    Tokens.BACKTICK: "Обратный апостроф ‹`›",
    Tokens.EXCLAMATION: "Восклицательный знак ‹!›",

    Tokens.PLUS: "Плюс ‹+›",
    Tokens.MINUS: "Минус ‹-›",
    Tokens.STAR: "Умножение ‹*›",
    Tokens.SLASH: "Деление ‹/›",
    Tokens.PERCENT: "Остаток от деления ‹%›",
    Tokens.POW: "Степень ‹^›",

    Tokens.EQUAL: "Равно ‹==›",
    Tokens.PLUS_ASSIGN: "Плюс-равно ‹+=›",
    Tokens.MINUS_ASSIGN: "Минус-равно ‹-=›",
    Tokens.STAR_ASSIGN: "Умножить-равно ‹*=›",
    Tokens.SLASH_ASSIGN: "Делить-равно ‹/=›",
    Tokens.PERCENT_ASSIGN: "Остаток-равно ‹%=›",
    Tokens.POW_ASSIGN: "Степень-равно ‹^=›",

    Tokens.PLUS_PLUS: "Инкремент ‹++›",
    Tokens.MINUS_MINUS: "Декремент ‹--›",

    Tokens.ASSIGN: "Присваивание ‹=›",
    Tokens.NOT_EQUAL: "Не равно ‹!=›",
    Tokens.LESS: "Меньше ‹<›",
    Tokens.GREATER: "Больше ‹>›",
    Tokens.LESS_EQUAL: "Меньше или равно ‹<=›",
    Tokens.GREATER_EQUAL: "Больше или равно ‹>=›",

    Tokens.VARIABLE: "Переменная/слово",
    Tokens.LINE_VARIABLE: "Строч. переменная",
    Tokens.LOCAL_VARIABLE: "Локал. переменная",
    Tokens.GAME_VARIABLE: "Игровая переменная",
    Tokens.SAVE_VARIABLE: "Сохр. переменная",

    Tokens.STRING: "Строка",
    Tokens.NUMBER: "Число",

    Tokens.NEWLINE: "Новая строка",
    Tokens.NL: "Новая строка",
    Tokens.INDENT: "Повышение пробелов",
    Tokens.DEDENT: "Понижение пробелов",

    Tokens.EOF: "Конец файла",
}