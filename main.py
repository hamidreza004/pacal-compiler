from scanner.core import get_token
import sys
from scanner.helper import initiate

if __name__ == '__main__':

    args = sys.argv

    if len(args) != 2:
        print("Invalid number of argumnets.")
        print("Usage: python main.py src.ppp")
        exit()

    with open(args[1], 'r') as f:
        src = ''.join(f.readlines())

    initiate(src)

    while True:
        token = get_token()
        print(token)
        if token is None:
            break

    # TODO : Put Token in parser

    # TODO : PARSER (CodeGenerator is in parser)
