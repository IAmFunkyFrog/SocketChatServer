import sys

from client import client
from server import server

HELP = """
Simple console chat application on sockets.
Expected 3 command line args:
- mode: might be 'server' or 'client'. If 'server' set then you will host char, otherwise try to connect
- host: ip to be connected (hosted)
- port: port to be connected (hosted)

Example: python3 ./main.py server localhost 5000
"""


def main():
    if len(sys.argv) != 4:
        print(HELP, file=sys.stderr)
        sys.exit(1)

    mode = sys.argv[1]
    host = sys.argv[2]
    try:
        port = int(sys.argv[3])
    except ValueError:
        print(f"Port expected to be integer number, but given {sys.argv[2]}", file=sys.stderr)
        sys.exit(1)

    match mode:
        case 'server':
            server(host, port)
        case 'client':
            client(host, port)
        case _:
            print("Unknown mode set!\n\n" + HELP, file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
