from .tokens import Tokens

KEYWORDS = {
    "event": Tokens.EVENT,

    "function": Tokens.FUNCTION,
    "def": Tokens.FUNCTION,
    "process": Tokens.PROCESS,
    "proc": Tokens.PROCESS,
    "call": Tokens.DEFINITION_CALL,

    "import": Tokens.IMPORT,
    "from": Tokens.FROM,
    "define": Tokens.DEFINE,

    "if": Tokens.IF,
    "elif": Tokens.ELIF,
    "else": Tokens.ELSE,

    "while": Tokens.WHILE,
    "for": Tokens.FOR,
    
    "wait": Tokens.CODE_CONTROL,
    "sleep": Tokens.CODE_CONTROL,
    "continue": Tokens.CODE_CONTROL,
    "break": Tokens.CODE_CONTROL,
    "exit": Tokens.CODE_CONTROL,
    "stop": Tokens.CODE_CONTROL,
    "return": Tokens.CODE_CONTROL,
    "error": Tokens.CODE_CONTROL,

    "controller": Tokens.CONTROLLER,
    "select": Tokens.SELECT
}

VAR_PREFIXES = {
    "i": Tokens.LINE_VARIABLE,
    "line": Tokens.LINE_VARIABLE,
    
    "l": Tokens.LOCAL_VARIABLE,
    "local": Tokens.LOCAL_VARIABLE,

    "g": Tokens.GAME_VARIABLE,
    "game": Tokens.GAME_VARIABLE,

    "s": Tokens.SAVE_VARIABLE,
    "save": Tokens.SAVE_VARIABLE
}