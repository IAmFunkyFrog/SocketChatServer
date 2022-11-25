def recvall(conn, byte_size):
    content = b''
    while len(content) < byte_size:
        message = conn.recv(byte_size - len(content))
        if len(message) == 0:
            return None
        else:
            content += message
    return content