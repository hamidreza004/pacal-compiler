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
    return word[pointer - 1]
