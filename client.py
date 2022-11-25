import selectors
import socket
import sys
from threading import Thread

import message
from message import FULL_MESSAGE_WIDTH, Message
from utils import recvall

SELECTOR = selectors.DefaultSelector()
APPLICATION_RUN = True


def dispatch_server_event(conn, mask):
    assert mask & selectors.EVENT_READ

    message = recvall(conn, FULL_MESSAGE_WIDTH)
    if message is None:
        print(f"Lost connection with {conn}", file=sys.stderr)
        conn.close()
        return

    print(Message.decode(message))


def selector_cycle():
    while True:
        events = SELECTOR.select(0.1)
        if not APPLICATION_RUN:
            return
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)


SELECTOR_THREAD = Thread(target=selector_cycle)


def client(host: str | int, port: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
    except ConnectionRefusedError:
        print(f"Connection refused from {host}:{port}", file=sys.stderr)
        sys.exit(1)
    except socket.gaierror as err:
        print(err, file=sys.stderr)
        sys.exit(1)
    except OverflowError as err:
        print(err, file=sys.stderr)
        sys.exit(1)

    username = input("Enter username: ")
    while len(username.encode(message.ENCODING)) > message.USERNAME_BYTES_SIZE:
        username = input("Try again, last username is long: ")
    sock.setblocking(False)
    SELECTOR.register(sock, selectors.EVENT_READ, dispatch_server_event)
    SELECTOR_THREAD.start()

    print("Now you can enter your messages and see others:")
    while True:
        try:
            content = input()
        except KeyboardInterrupt:
            global APPLICATION_RUN
            APPLICATION_RUN = False
            exit(0)
        try:
            sock.sendall(Message(username, content).encode())
        except ValueError as err:
            print(err, file=sys.stderr)
        except BrokenPipeError:
            print(f"Lost connection with {sock}", file=sys.stderr)
            sock.close()
            exit(1)
