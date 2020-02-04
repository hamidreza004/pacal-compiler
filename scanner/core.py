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
    "and",
    "or",
    "%",
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

    while token is not None and (ord(token) == ord(' ') or ord(token) == ord('\n')):
        token = input_char()

    if token is None:
        return None

    if ord('0') <= ord(token) <= ord('9'):
        return get_token_number()

    if ord(token) == ord('\''):
        return get_token_char()

    if ord(token) == ord('"'):
        return get_token_string()

    if ord(token) == ord('-'):
        token = input_char()
        if ord(token) == ord('-'):
            return get_token_comment_one_line()
        elif ord(token) == ord(' ') or ord(token) == ord('\n'):
            return token_to_map('-')
        else:
            return get_token_negative_number()

    if ord(token) == ord('/'):
        token = input_char()
        if ord(token) == ord('/'):
            return get_token_comment_one_line()
        elif ord(token) == ord(' ') or ord(token) == ord('\n'):
            return token_to_map('/')
        else:
            sys.exit(errors.CONCAT_ERROR)

    if ord(token) == ord('<'):
        token = input_char()
        if ord(token) == ord('-'):
            return get_token_comment_multiple_line()
        elif ord(token) == ord(' ') or ord(token) == ord('\n'):
                return token_to_map('<')
        else:
            sys.exit(errors.CONCAT_ERROR)

    if ord('a') <= ord(token) <= ord('z') or ord('A') <= ord(token) <= ord('Z'):
        return get_token_id()



    return 1
