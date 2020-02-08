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

    ch = src[pointer]
    pointer += 1
    if ch == '\f' or ch == '\r' or ch == '\t' or ch == '\v' or ord(ch) == 32:
        return " "
    return ch
