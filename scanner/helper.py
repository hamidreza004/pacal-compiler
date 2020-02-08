src = None
pointer = None


def initiate(source):
    global src, pointer
    pointer = 0
    src = rearrange(source)


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


def rearrange(code):
    level = 0
    lines = code.split('\n')
    global_vars = []
    for i, line in enumerate(lines):
        if line.split(' ')[0] == "begin":
            level += 1
            continue
        if line.split(' ')[0] == "end":
            level -= 1
            continue
        if level == 0 and line.split(' ')[0] != "function" and line.split(' ')[0] != "procedure" and line.split(' ')[0] != '':
            global_vars.append(line)
            lines[i] = '$' + line

    for line in lines:
        if line != '' and line[0] == '$':
            continue
        global_vars.append(line)

    return '\n'.join(global_vars)

