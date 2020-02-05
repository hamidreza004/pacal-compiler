SCANNER_EXCEPTION = "Scanner exception has occurred."
NO_VALID_TOKEN = "No valid character or semantic."
PARSER_EXCEPTION = "Semantic error has occurred."
INVALID_GRAMMAR = "Parse table is invalid."


class ParserException(Exception):
    pass


class ScannerException(Exception):
    pass
