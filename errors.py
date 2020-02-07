SCANNER_EXCEPTION = "Scanner exception has occurred."
NO_VALID_TOKEN = "No valid character or semantic."
PARSER_EXCEPTION = "Semantic error has occurred."
INVALID_GRAMMAR = "Parse table is invalid."
DOUBLE_DECLARE = "One variable declare twice in same scope."
ARRAY_DIM_INTEGER = "Array dimension must be integer"
NOT_ARRAY = "It's an array."
NOT_DECLARED = "Variable not declared."


class ParserException(Exception):
    pass


class ScannerException(Exception):
    pass


class CodeGeneratorException(Exception):
    pass
