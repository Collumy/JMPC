from compiler.lexer.tokens import Tokens
from compiler.ast.node import IfOperation, ElseOperation
from compiler.parser.core.condition import parse_condition
from compiler.parser.core.operations import parse_body

def parse_if(parser):
    condition = None

    if parser.current.type == Tokens.IF:
        parser.eat(Tokens.IF)

        condition = parse_condition(parser)
        parser.eat(Tokens.COLON)
        body = parse_body(parser)

        return IfOperation(condition, body)
    
    elif parser.current.type == Tokens.ELSE and parser.peek().type == Tokens.COLON:
        parser.eat(Tokens.ELSE)
        parser.eat(Tokens.COLON)
        
        body = parse_body(parser)

        return ElseOperation(condition, body)
    
    else:
        parser.eat(parser.current.type)
        if parser.current.type == Tokens.IF: parser.eat(Tokens.IF)

        condition = parse_condition(parser)
        parser.eat(Tokens.COLON)
        body = parse_body(parser)

        return ElseOperation(condition, body)
        

        