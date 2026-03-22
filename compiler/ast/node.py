class Event:
    def __init__(self, name, body):
        self.type = "event"
        self.name = name
        self.body = body
        self.position = None

class Definition:
    def __init__(self, type, name, body, args, display):
        self.type = type
        self.name = name
        self.args = args
        self.body = body
        self.display = display
        self.position = None




class Action:
    def __init__(self, target, method, args, selection=None):
        self.target = target
        self.selection = selection
        self.method = method
        self.args = args

class Argument:
    def __init__(self, name, value):
        self.name = name
        self.value = value





class IfOperation:
    def __init__(self, condition, body):
        self.condition = condition   # класс условия
        self.body = body             # операции 

class ElseOperation:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class Condition:
    def __init__(self, target, method, args, inverted=None, selection=None):
        self.target = target         # player:: variable:: и тд
        self.method = method         # действие 
        self.args = args             # аргументы действия
        self.inverted = inverted     # НЕ        
        self.selection = selection   # <all>



class Repeat:
    def __init__(self, method, condition, body):
        self.method = method
        self.condition = condition
        self.body = body

class Controller:
    def __init__(self, method, body, args):
        self.method = method
        self.body = body
        self.args = args

class Select:
    def __init__(self, method, args=[], condition=None):
        self.method = method
        self.args = args
        self.condition = condition