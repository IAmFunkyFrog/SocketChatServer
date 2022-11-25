import selectors
import socket
import sys

from message import FULL_MESSAGE_WIDTH, Message
from utils import recvall

SELECTOR = selectors.DefaultSelector()
MAX_CONNECTIONS = 100
CLIENT_QUEUE = dict()


def dispatch_client_event(client_conn, mask):
    if mask & selectors.EVENT_WRITE:
        send = client_conn.send(CLIENT_QUEUE[client_conn])
        if send != 0:
            print(f'Send bytes ({send}) to {client_conn}')
            CLIENT_QUEUE[client_conn] = CLIENT_QUEUE[client_conn][send:]

    if mask & selectors.EVENT_READ:
        message = recvall(client_conn, FULL_MESSAGE_WIDTH)
        if message is None:
            print(f"Lost connection with {client_conn}")
            SELECTOR.unregister(client_conn)
            client_conn.close()
        else:
            print("Got message:\n" + str(Message.decode(message)))
            conn_to_unregister = []
            for key in SELECTOR.get_map().values():
                conn = key.fileobj
                if conn not in CLIENT_QUEUE:
                    continue
                try:
                    print(f'Saving in buffer to {conn}')
                    CLIENT_QUEUE[conn] += message
                except BrokenPipeError:
                    print(f'Broken pipe with {conn}')
                    conn_to_unregister.append(conn)

            for conn in conn_to_unregister:
                SELECTOR.unregister(conn)
                conn.close()


def accept(sock, mask):
    conn, addr = sock.accept()
    print(f'Accepted {conn} from {addr}')
    conn.setblocking(False)
    CLIENT_QUEUE[conn] = b''
    SELECTOR.register(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, dispatch_client_event)


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
    except OSError as err:
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
