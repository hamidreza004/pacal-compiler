from scanner.helper import input_char
import errors
import sys

key_words = [
    "array",
    "assign",
    "boolean",
    "break",
    "begin",
    "char",
    "continue",
    "do",
    "else",
    "end",
    "false",
    "function",
    "procedure",
    "if",
    "integer",
    "of",
    "real",
    "return",
    "string",
    "true",
    "while",
    "var",
    "and",
    "or"
]

all_words = {
    "array",
    "assign",
    "boolean",
    "break",
    "begin",
    "char",
    "continue",
    "do",
    "else",
    "end",
    "false",
    "function",
    "procedure",
    "if",
    "integer",
    "of",
    "real",
    "return",
    "string",
    "true",
    "while",
    "var",

    "and",
    "or",

    "+",
    "-",
    "*",
    "/",
    "&",
    "^",
    "|",
    "%",
    '~',

    "<",
    ">",
    "<=",
    ">=",
    "=",
    "<>",

    ")",
    "(",
    ":",
    ";",

}


def token_to_map(str):
    global all_words
    return all_words.index(str)


def map_to_token(ind):
    global all_words
    return all_words[ind]


token = input_char()


def get_token():
    global token

    while token == ' ' or token == '\n':
        token = input_char()

    if token is None:
        return None

    if ord('0') <= ord(token) <= ord('9'):
        return get_token_number()

    if token == '\'':
        return get_token_char()

    if token == '"':
        return get_token_string()

    if token == '-':
        token = input_char()
        if token == '-':
            return get_token_comment_one_line()
        elif token == ' ' or token == '\n':
            return token_to_map('-')
        else:
            return get_token_negative_number()

    if token == '/':
        token = input_char()
        if token == '/':
            return get_token_comment_one_line()
        elif token == ' ' or token == '\n':
            return token_to_map('/')
        else:
            sys.exit(errors.CONCAT_ERROR)

    if token == '<':
        token = input_char()
        if token == '-':
            return get_token_comment_multiple_line()
        elif token == ' ' or token == '\n':
            return token_to_map('<')
        elif token == '>':
            token = input_char()
            return token_to_map('<>')
        elif token == '=':
            token = input_char()
            return token_to_map('<=')
        else:
            sys.exit(errors.CONCAT_ERROR)

    if token == '>':
        token = input_char()
        if token == '=':
            token = input_char()
            return token_to_map('>=')
        elif token == ' ' or token == '\n':
            return token_to_map('>')
        else:
            sys.exit(errors.CONCAT_ERROR)

    if token == '~':
        return get_token_not_number()

    if token in ['+', '-', '*', '/', '&', '^', '|', '%', '~', ')', '(', ':', ';', '=']:
        token = input_char()
        return token_to_map(token)

    if ord('a') <= ord(token) <= ord('z') or ord('A') <= ord(token) <= ord('Z'):
        return get_token_id()

    return 1
