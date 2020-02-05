import sys
import errors

src = None
pointer = None


def initiate(source):
    global src, pointer
    pointer = 0
    src = source


def input_char():
    global src
    global pointer

    if pointer >= len(src):
        return None

    token = src[pointer]
    pointer += 1
    if token == '\f' or token == '\r' or token == '\t' or token == '\v' or ord(token) == 32:
        return " "
    return token


def check_eof():
    global token
    if token is None:
        sys.exit(errors.SCANNER_EXCEPTION)
