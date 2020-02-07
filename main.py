import sys
import csv
import errors
from scanner import helper
from scanner.core import get_token, initiate as scanner_initiate
from code_generator.core import generate, code, initiate as generator_initiate

GRAMMAR_PATH = 'table.csv'
START_STATE = 0
grammar = {}


def parse():
    global grammar
    state = START_STATE
    parse_stack = []
    token = get_token()
    while True:
        data = grammar[(state, token['type'])].split(' ')
        print(state, token, grammar[(state, token['type'])])
        if len(data) == 1:
            if data[0] == "ERROR":
                raise errors.ParserException(errors.ParserException)
            else:
                raise errors.ParserException(errors.INVALID_GRAMMAR)

        if len(data) == 2:
            if data[0] == "ACCEPT":
                generate(data[1], token['data'])
                print("Compilation completed with 0 errors.")
                exit()
            elif data[0] == "REDUCE":
                state = int(grammar[(parse_stack.pop(), data[1])].split(' ')[1][1:])
            else:
                raise errors.ParserException(errors.INVALID_GRAMMAR)
        if len(data) == 3:
            if data[0] == "SHIFT":
                state = int(data[1][1:])
                generate(data[2], token['data'])
                token = get_token()
            elif data[0] == "PUSH_GOTO":
                parse_stack.append(state)
                generate(data[2], token['data'])
                state = int(data[1][1:])
            elif data[0] == "GOTO":
                state = int(data[1][1:])
                generate(data[2], token['data'])
                token = get_token()
            else:
                raise errors.ParserException(errors.INVALID_GRAMMAR)


if __name__ == '__main__':
    args = sys.argv

    if len(args) != 2:
        print("Invalid number of arguments.")
        print("Usage: python main.py src.ppp")
        exit()

    with open(args[1], 'r') as f:
        src = ''.join(f.readlines())

    helper.initiate(src)
    scanner_initiate()

    with open(GRAMMAR_PATH, 'r') as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader)[1:]
        for row in reader:
            for j, cell in enumerate(row[1:]):
                grammar[(int(row[1].strip()), header[j].strip())] = cell.strip()
    print("Start Compiling...")

    generator_initiate()

    parse()

    for line in code:
        print(line)
