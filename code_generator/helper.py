variable_map = {
    'boolean': 'i1',
    'char': 'i8',
    'integer': 'i32',
    'long': 'i64',
    'real': 'float',
    'string': 'i8*',
}

variable_order = [
    'i1',
    'i8',
    'i32',
    'i64',
    'float',
    'string',
]

variable_size = {
    'i1': '1',
    'i8': '1',
    'i8*': '8',
    'i32': '4',
    'i64': '8',
    'float': '4',
}


def type_cast(type_a, type_b):
    if type_a == type_b:
        return ""
    if type_a == "float":
        return "fptosi"
    if type_b == "float":
        return "sitofp"
    if variable_order.index(type_a) < variable_order.index(type_b):
        return "trunc"
    if variable_order.index(type_a) > variable_order.index(type_b):
        return "sext"
