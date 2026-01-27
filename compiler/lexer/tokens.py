from enum import Enum, auto

class Tokens(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return count

    EVENT = auto()           # event
    FUNCTION = auto()        # function
    PROCESS = auto()         # process
    DEFINITION_CALL = auto() # call func Name() - вызов функции/процесса

    IMPORT = auto()          # import *
    FROM = auto()            # from * import *
    DEFINE = auto()          # define print = player::message

    SELECTOR = auto()        # селектор::
    IF = auto()              # if
    ELSE = auto()            # else
    ELIF = auto()            # elif
    WHILE = auto()           # while
    FOR = auto()             # for

    CODE_CONTROL = auto()    # break continue stop exit return wait()
    CONTROLLER = auto()      # controller catch():
    IDENTIFIER = auto()      # функция()
    SELECT = auto()

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