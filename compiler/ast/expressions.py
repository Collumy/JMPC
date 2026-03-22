class TypeNumber:
    def __init__(self, value):
        self.value = float(value)
        self.type = "NUMBER"

class TypeString:
    def __init__(self, value, parsing="legacy"):
        self.value = value
        self.parsing = parsing
        self.type = "STRING"

class TypeVariable:
    def __init__(self, token):
        self.token = token
        self.value = token.value
        self.type = token.type   # локальная строчная и тд

class TypeList:
    def __init__(self, items):
        self.items = items

class TypeDict:
    def __init__(self, items):
        self.items = items

class TypeEnum:
    def __init__(self, value=None, variable=None):
        self.value = value
        self.variable = variable
        self.type = "ENUM"




class FunctionCall:
    def __init__(self, name, args, token, parser):
        self.name = name
        self.args = args
        self.token = token
        self.parser = parser

class NamedArgumentNode:
    def __init__(self, name, value):
        self.name = name
        self.value = value