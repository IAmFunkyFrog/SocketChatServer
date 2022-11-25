import selectors
import socket
import sys

from message import FULL_MESSAGE_WIDTH, Message
from utils import recvall

SELECTOR = selectors.DefaultSelector()
MAX_CONNECTIONS = 100


def dispatch_client_event(conn, mask):
    if mask & selectors.EVENT_READ:
        message = recvall(conn, FULL_MESSAGE_WIDTH)
        if message is None:
            print(f"Lost connection with {conn}")
            SELECTOR.unregister(conn)
            return

        print("Got message:\n" + str(Message.decode(message)))
        conn_to_unregister = []
        for key in SELECTOR.get_map().values():
            conn = key.fileobj
            try:
                conn.sendall(message)
            except BrokenPipeError:
                conn_to_unregister.append(conn)

        for conn in conn_to_unregister:
            SELECTOR.unregister(conn)


def accept(sock, mask):
    conn, addr = sock.accept()
    print(f'Accepted {conn} from {addr}')
    conn.setblocking(False)
    SELECTOR.register(conn, selectors.EVENT_READ, dispatch_client_event)


def server(host: str | int, port: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((host, port))
    except socket.gaierror as err:
        print(err, file=sys.stderr)
        sys.exit(1)
    except OverflowError as err:
        print(err, file=sys.stderr)
        sys.exit(1)
    sock.listen(MAX_CONNECTIONS)
    sock.setblocking(False)
    SELECTOR.register(sock, selectors.EVENT_READ, accept)

    while True:
        events = SELECTOR.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)
