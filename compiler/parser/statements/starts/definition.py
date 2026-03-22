from compiler.lexer.tokens import Tokens
from compiler.ast.node import Definition
from compiler.ast.params import EnumParameter, PluralParameter, SingularParameter, EnumElement
from compiler.ast.expressions import TypeString, TypeList
from compiler.utils.code.errors import error
from compiler.parser.core.operations import parse_body
from compiler.parser.expressions.expressions import parse_expression
from compiler.parser.core.function_signatures import register_function

VALUES_TYPES = ["any", "text", "number", "location", "vector", "block", "item",
                "sound", "particle", "potion", "array", "map", "variable"]

PARAMS_SLOTS = [[], [13], [12, 14], [11, 13, 15], [10, 12, 14, 16], [11, 12, 13, 14, 15], [10, 11, 12, 14, 15, 16],
                [10,11,12,13,14,15,16], [9,10,11,12,13,14,15,16], [9,10,11,12,13,14,15,16,17,18]]

PARAMS_TYPES = {
    "singular": "singular",
    "single": "singular",
    "one": "singular",

    "plural": "plural",
    "multi": "plural",

    "enum": "enum",
    "marker": "enum"
}


def parse_definition(parser):
    display = {}
    ftype = True
    args = []
    
    if parser.current.type == Tokens.FUNCTION:
        if parser.current.value == "def": ftype = False
        parser.eat(Tokens.FUNCTION)
        dtype = "function"

    if parser.current.type == Tokens.PROCESS:
        if parser.current.value == "proc": ftype = False
        parser.eat(Tokens.PROCESS)
        dtype = "process"

    if parser.current.type not in (Tokens.VARIABLE, Tokens.IDENTIFIER):
        error(parser, f"После '{dtype}' ожидается название функции")
    name = parser.current.value
    parser.eat(parser.current.type)

    # отображаемая информация
    if parser.current.type == Tokens.LESS:
        parser.eat(Tokens.LESS)

        name_expr = parse_expression(parser)
        if not isinstance(name_expr, TypeString):
            error(parser, "Отображаемое имя должно быть строкой")
        display["name"] = name_expr

        if parser.current.type == Tokens.COMMA:
            parser.eat(Tokens.COMMA)
            item_expr = parse_expression(parser)
            display["icon"] = item_expr
        
        if parser.current.type == Tokens.COMMA:
            parser.eat(Tokens.COMMA)
            parser.eat(parser.current.type)
            display["hidden"] = "TRUE"

        parser.eat(Tokens.GREATER)
    

    # параметры
    if parser.current.type == Tokens.LPAREN:
        parser.eat(Tokens.LPAREN)
        if ftype: args = advanced_args(parser)
        else: args = basic_args(parser)

    # кастомное возвращение
    returning_amount = 0
    if parser.current.type == Tokens.MINUS:
        if dtype != "function": error(parser, "Возвращаемые значения можно делать только в функциях")
        parser.eat(Tokens.MINUS)
        parser.eat(Tokens.GREATER)
        if parser.current.type != Tokens.NUMBER: error(parser, "Ожидалось число возвращаемых значений")
        returning_amount = parser.current.value
        parser.eat(Tokens.NUMBER)
        
    parser.eat(Tokens.COLON)

    parser.context = dtype
    body = parse_body(parser)

    register_function(name, dtype, args, returning_amount)

    return Definition(dtype, name, body, args, display)



def basic_args(parser):
    args = []

    # Одиночные параметры
    while parser.current.type != Tokens.RPAREN:
        args.append(parse_singular_param(parser))

        if parser.current.type == Tokens.COMMA:
            parser.eat(Tokens.COMMA)
            if parser.current.type == Tokens.NL: parser.eat(Tokens.NL)
        else:
            break

    parser.eat(Tokens.RPAREN)

    # Автоопределение слота
    ind = 0
    for arg in args:
        if len(args) < 10: arg.slot = PARAMS_SLOTS[len(args)][ind]
        else: arg.slot = ind % 9 + (ind // 9) * 18
        arg.desc_slot = arg.slot + 9
        ind += 1

    return args


def advanced_args(parser):
    args = []

    while parser.current.type != Tokens.RPAREN:
        if parser.current.type != Tokens.VARIABLE:
            if parser.current.type == Tokens.NL: parser.eat(Tokens.NL); continue
            error(parser, "Ожидался тип параметра: single/plural/enum (одиночный/множество/маркер)")

        type = parser.current.value
        parser.eat(Tokens.VARIABLE)
        if type not in PARAMS_TYPES: error(parser, "Такого типа параметра нет, попробуйте: single/plural/enum")
        type = PARAMS_TYPES[type]

        parser.eat(Tokens.COLON)

        if type == "singular": args.append(parse_singular_param(parser, True))
        if type == "plural":   args.append(parse_plural_param(parser))
        if type == "enum":     args.append(parse_enum_param(parser))


        if parser.current.type == Tokens.COMMA:
            parser.eat(Tokens.COMMA)
            if parser.current.type == Tokens.NL: parser.eat(Tokens.NL) 
        else:
            break

    parser.eat(Tokens.RPAREN)
    return args



# (a) / (a: text) / (a: text = "hi") / (a<"Текст">: text = "hi") / a<"Текст", слот, описание>: text = "hi"
def parse_singular_param(parser, slot_required=False):
    if parser.current.type != Tokens.VARIABLE: error(parser, "Ожидалось имя параметра")
    
    param_name = parser.current.value
    parser.eat(Tokens.VARIABLE)

    param_type = "any"
    param_default = None
    param_display = None
    param_slot = None
    param_desc_slot = None

    if parser.current.type == Tokens.LESS:
        parser.eat(Tokens.LESS)

        # Описание
        if parser.current.type != Tokens.STRING: error(parser, "Ожидалось описание параматера")
        param_display = parse_expression(parser).value

        # Слот
        if parser.current.type == Tokens.COMMA:
            parser.eat(Tokens.COMMA)
            if parser.current.type != Tokens.NUMBER: error(parser, "Ожидался номер слота параметра")
            param_slot = parse_expression(parser).value
        elif slot_required: error(parser, "Вам нужно указать слот параметра в <>, например test<'название', 13, 22>")
        
        # Слот описания
        if parser.current.type == Tokens.COMMA:
            parser.eat(Tokens.COMMA)
            if parser.current.type != Tokens.NUMBER: error(parser, "Ожидался номер слота описания параметра")
            param_desc_slot = parse_expression(parser).value
        elif slot_required: error(parser, "Вам нужно указать слот описания параметра в <>, например test<'название', 13, 22>")        

        parser.eat(Tokens.GREATER)        

    elif slot_required: error(parser, "Вам нужно указать слоты параметра в <>, например test<'название', 13, 22>")  


    if parser.current.type == Tokens.COLON:
        parser.eat(Tokens.COLON)

        # тип
        if parser.current.type != Tokens.VARIABLE: error(parser, "Ожидался тип параметра")
        param_type = parser.current.value
        if param_type not in VALUES_TYPES: error(parser, f"Такого типа параметра нет, вот все: {VALUES_TYPES}")
        parser.eat(Tokens.VARIABLE)

        # по умолчанию
    if parser.current.type == Tokens.ASSIGN:
        parser.eat(Tokens.ASSIGN)
        param_default = parse_expression(parser)
    
    return SingularParameter(param_name, param_slot, param_desc_slot, param_type, param_display, param_default)






# (multi: a<"Перем", [0,1,2], [9,10,11], "not">: text = ["1", "2", "3"])
def parse_plural_param(parser):
    if parser.current.type != Tokens.VARIABLE: error(parser, "Ожидалось имя параметра")
    
    param_name = parser.current.value
    parser.eat(Tokens.VARIABLE)

    param_type = "any"
    param_default = None
    param_display = None
    param_slots = None
    param_desc_slots = None
    param_ignore = "true"

    parser.eat(Tokens.LESS)

    # Описание
    if parser.current.type != Tokens.STRING: error(parser, "Ожидалось описание параматера")
    param_display = parse_expression(parser).value

    # Слоты
    parser.eat(Tokens.COMMA)
    param_slots = parse_list(parser)

    
    # Слот описания
    parser.eat(Tokens.COMMA)
    param_desc_slots = parse_list(parser)

    # Игнорирование
    if parser.current.type == Tokens.COMMA:
        param_ignore = "false"
        parser.eat(Tokens.COMMA); parser.eat(parser.current.type)

    parser.eat(Tokens.GREATER)        



    if parser.current.type == Tokens.COLON:
        parser.eat(Tokens.COLON)

        # тип
        if parser.current.type != Tokens.VARIABLE: error(parser, "Ожидался тип параметра")
        param_type = parser.current.value
        if param_type not in VALUES_TYPES: error(parser, f"Такого типа параметра нет, вот все: {VALUES_TYPES}")
        parser.eat(Tokens.VARIABLE)

        # по умолчанию
    if parser.current.type == Tokens.ASSIGN:
        parser.eat(Tokens.ASSIGN)
        param_default = parse_expression(parser)
        if not isinstance(param_default, TypeList): error(parser, f"Значение по умолчанию у параметра должно быть списком")
    
    return PluralParameter(param_name, param_slots, param_desc_slots, param_type, param_ignore, param_display, param_default)



def parse_list(parser):
    list = "["
    parser.eat(Tokens.LBRACKET)
    
    while parser.current.type != Tokens.RBRACKET:
        if parser.current.type != Tokens.NUMBER: error(parser, "Ожидалось число, но получен другой тип")
        list += parser.current.value
        parser.eat(Tokens.NUMBER)

        if parser.current.type == Tokens.COMMA:
            parser.eat(Tokens.COMMA)
            list += ","
    
    parser.eat(Tokens.RBRACKET)
    list += "]"

    return list






def parse_enum_param(parser):
    if parser.current.type != Tokens.VARIABLE: error(parser, "Ожидалось имя параметра")
    
    param_name = parser.current.value
    parser.eat(Tokens.VARIABLE)

    param_default = 0
    param_display = None
    param_slot = None
    param_elements = []

    parser.eat(Tokens.LESS)

    # Описание
    if parser.current.type != Tokens.STRING: error(parser, "Ожидалось описание параматера")
    param_display = parse_expression(parser).value

    # Слот
    parser.eat(Tokens.COMMA)
    if parser.current.type != Tokens.NUMBER: error(parser, "Ожидалось число слота параметра")
    param_slot = parse_expression(parser).value


    # Умолчание
    if parser.current.type == Tokens.COMMA:
        parser.eat(Tokens.COMMA)
        if parser.current.type != Tokens.NUMBER: error(parser, "Ожидался индекс параметра по умолчанию")
        param_default = parse_expression(parser).value
    
    parser.eat(Tokens.GREATER)
    parser.eat(Tokens.COLON)

    # Значения
    if parser.current.type == Tokens.NL: parser.eat(Tokens.NL)
    if parser.current.type != Tokens.LBRACKET: error(parser, "Ожидался список значений маркера")
    parser.eat(Tokens.LBRACKET)
    
    while parser.current.type != Tokens.RBRACKET:
        if parser.current.type == Tokens.NL: parser.eat(Tokens.NL) 
        param_elements.append(parse_enum_element(parser))
        
        if parser.current.type == Tokens.COMMA: parser.eat(Tokens.COMMA)
        else: break
    
    if parser.current.type == Tokens.NL: parser.eat(Tokens.NL) 
    if parser.current.type != Tokens.RBRACKET: error(parser, "Ожидался ] для закрытия списка значений маркера") 
    parser.eat(Tokens.RBRACKET)


    param_default = int(param_default)
    if param_default < len(param_elements):
        param_default = param_elements[param_default].name
    else:
        param_default = param_elements[0].name

    return EnumParameter(param_name, param_slot, param_elements, param_default, param_display)





def parse_enum_element(parser):
    if parser.current.type != Tokens.VARIABLE: error(parser, "Ожидалось имя элемента маркера: test<>")
    name = parser.current.value
    parser.eat(Tokens.VARIABLE)

    display_name = None
    icon = None

    if parser.current.type == Tokens.LESS:
        parser.eat(Tokens.LESS)

        if parser.current.type != Tokens.STRING: error(parser, "Ожидалась строка отображаемого элемента")
        display_name = parser.current.value
        parser.eat(Tokens.STRING)

        if parser.current.type == Tokens.COMMA:
            parser.eat(Tokens.COMMA)
            icon = parse_expression(parser)
        
        if parser.current.type != Tokens.GREATER: error(parser, "Ожидался символ >")
        parser.eat(Tokens.GREATER)
    
    return EnumElement(name, display_name, icon)