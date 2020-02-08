from scanner.helper import input_char
import errors
from scanner.words import *

token = None
sym_table = [{} for i in range(101)]


def create_or_get(id):
    global sym_table
    for i in reversed(range(0, 100)):
        if sym_table[i].get(id) is not None:
            return sym_table[i][id]
    sym_table[100][id] = {'pre': id, 'name': id + ".100", 'level': 100}
    return sym_table[100][id]


def is_en_alpha(c):
    return ord('a') <= ord(c) <= ord('z') or ord('A') <= ord(c) <= ord('Z')


def initiate():
    global token
    token = input_char()


def check_eof():
    global token
    if token is None:
        raise errors.ScannerException(errors.SCANNER_EXCEPTION)


def srz(type, data):
    return {"type": type, "data": data}


def get_token():
    global token
    while token == ' ' or token == '\n':
        token = input_char()

    if token is None:
        return srz('$', None)

    if token == ':':
        token = input_char()
        if token == '=':
            token = input_char()
            return srz(':=', None)
        return srz(':', None)

    if token.isdigit() or token == '.':
        return get_token_number()

    if token == '\'':
        return get_token_char()

    if token == '"':
        return get_token_string()

    if token == '-':
        token = input_char()
        if token == '-':
            return get_token_comment_one_line()
        else:
            return srz('-', None)

    if token == '/':
        token = input_char()
        if token == '/':
            return get_token_comment_one_line()
        elif token == ' ' or token == '\n':
            return srz('/', None)
        else:
            raise errors.ScannerException(errors.SCANNER_EXCEPTION)

    if token == '<':
        token = input_char()

        if token == '-':
            token = input_char()
            if token == '-':
                return get_token_comment_multiple_lines()
            raise errors.ScannerException(errors.SCANNER_EXCEPTION)
        elif token == ' ' or token == '\n':
            return srz('<', None)
        elif token == '>':
            token = input_char()
            return srz('<>', None)
        elif token == '=':
            token = input_char()
            return srz('<=', None)
        else:
            raise errors.ScannerException(errors.SCANNER_EXCEPTION)

    if token == '>':
        token = input_char()
        if token == '=':
            token = input_char()
            return srz('>=', None)
        elif token == ' ' or token == '\n':
            return srz('>', None)
        else:
            raise errors.ScannerException(errors.SCANNER_EXCEPTION)

    if token == '~':
        token = input_char()
        return srz('~', None)

    if is_en_alpha(token):
        return get_token_id()

    if token == '|':
        token = input_char()
        return srz('bor', None)

    if token == ',':
        token = input_char()
        return srz('comma', None)
    if token in single_signs:
        c = token
        token = input_char()
        return srz(c, None)
    print(token)
    raise errors.ScannerException(errors.NO_VALID_TOKEN)


def get_token_real_number():
    global token
    ans = 0
    mul = 1
    while True:
        token = input_char()
        check_eof()
        if token.isdigit():
            mul *= 0.1
            ans = ans + (ord(token) - ord('0')) * mul
        else:
            return srz('constant', ('real', ans))


def get_token_number():
    global token
    if token == '.':
        return get_token_real_number()
    elif token == '0':
        token = input_char()
        check_eof()
        if token == 'x':
            ans = 0
            while True:
                token = input_char()
                check_eof()
                if token.isdigit():
                    ans = ans * 16 + ord(token) - ord('0')
                elif ord('A') <= ord(token.upper()) <= ord('F'):
                    ans = ans * 16 + ord(token.upper()) - ord('A') + 10
                else:
                    return srz('constant', ('integer', ans))
        if token == '.':
            return get_token_real_number()

        return srz('constant', ('integer', 0))
    else:
        ans = ord(token) - ord('0')
        while True:
            token = input_char()
            check_eof()
            if token.isdigit():
                ans = ans * 10 + ord(token) - ord('0')
            else:
                if token == '.':
                    ans = ans + get_token_real_number()['data'][1]
                    return srz('constant', ('real', ans))
                else:
                    return srz('constant', ('integer', ans))


def get_token_char():
    global token
    token = input_char()
    check_eof()
    ans = token
    token = input_char()
    check_eof()
    if token != "'":
        raise errors.ScannerException(errors.SCANNER_EXCEPTION)
    token = input_char()
    return srz('constant', ('character', ans))


def get_token_string():
    global token
    ans = ""
    while True:
        token = input_char()
        check_eof()
        if token == '"':
            token = input_char()
            return srz('constant', ('string', ans))
        ans += token


def get_token_comment_one_line():
    global token
    while True:
        token = input_char()
        check_eof()
        if token == '\n':
            token = input_char()
            return get_token()


def get_token_comment_multiple_lines():
    global token
    a = 0
    while True:
        token = input_char()
        check_eof()
        if token == '-':
            a += 1
        elif token == '>':
            if a >= 2:
                token = input_char()
                return get_token()
            a = 0
        else:
            a = 0


def get_token_id():
    global token
    ans = "" + token
    while True:
        token = input_char()

        if token is None or (not token.isdigit() and not is_en_alpha(token) and token != "_"):
            if ans in types:
                return srz('type', ans)
            if ans in key_token_words:
                return srz(ans, None)
            if ans in boolean_consts:
                return srz('constant', ('boolean', 1 if ans == "true" else 0))
            return srz('id', create_or_get(ans))

        ans += token
