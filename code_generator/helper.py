variable_map = {
    'boolean': 'i1',
    'character': 'i8',
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

variable_default = {
    'i1': '0',
    'i8': '0',
    'i8*': 'null',
    'i32': '0',
    'i64': '0',
    'float': '0.0',
}

variable_cast_func = {
    'i1': int,
    'i8': str,
    'i8*': str,
    'i32': int,
    'i64': int,
    'float': float,
}


def type_cast(type_a, type_b):
    if type_a == type_b:
        return ""
    if type_a == "float":
        return "fptosi"
    if type_b == "float":
        return "sitofp"
    if variable_order.index(type_a) < variable_order.index(type_b):
        if type_a == 'i1':
            return "zext"
        return "sext"
    if variable_order.index(type_a) > variable_order.index(type_b):
        return "trunc"
