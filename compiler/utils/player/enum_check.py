from compiler.ast.expressions import TypeString, TypeVariable, TypeEnum
from compiler.parser.expressions.expressions import parse_expression
from compiler.utils.code.errors import error

def get_enum(parser, meta):
    value = parse_expression(parser)

    if isinstance(value, TypeVariable) or isinstance(value, TypeString):
        text = value.value.upper()
        short = {i[:len(text)]: i for i in meta}
        
        if text in meta:
            return TypeEnum(text)
        if text in short.keys():
            return TypeEnum(short[text])
        if isinstance(value, TypeVariable):
            return TypeEnum(meta[0], value)


     
    error(parser,
        f"Недопустимое значение '{value.value}' для маркера. "
        f"Допустимые: {', '.join(meta)}"
    )