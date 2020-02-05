word = input()
pointer = 0


def input_char():
    global pointer
    global word

    if pointer == len(word):
        try:
            word = input()
            pointer = 0
            return "\n"
        except EOFError:
            return None

    pointer += 1
    token = word[pointer - 1]
    if token == '\f' or token == '\r' or token == '\t' or token == '\v' or ord(token) == 32:
        return " "
    return token
