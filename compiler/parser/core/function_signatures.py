FUNCTION_SIGNATURES = {}

class FunctionSignature:
    def __init__(self, name, args, returning):
        self.name = name
        self.args = args
        self.returning = returning


def register_function(name, type, args, returning=0):
    name = type + "_" + name
    FUNCTION_SIGNATURES[name] = FunctionSignature(name, args, returning)

def get_function(name, type):
    name = type + "_" + name
    return FUNCTION_SIGNATURES[name]

def has_function(name, type):
    name = type + "_" + name
    return name in FUNCTION_SIGNATURES