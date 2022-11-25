ENCODING = 'utf-8'
USERNAME_BYTES_SIZE = 256
CONTENT_BYTE_SIZE = 512
FULL_MESSAGE_WIDTH = USERNAME_BYTES_SIZE + CONTENT_BYTE_SIZE


class Message:
    def __init__(self, username: str, content: str):
        self._username = username
        self._content = content

    def __str__(self):
        return f'[{self._username}] {self._content}'

    def encode(self) -> bytes:
        username_encoded = self._username.encode(ENCODING)
        if len(username_encoded) <= USERNAME_BYTES_SIZE:
            username_encoded += b''.join([b'\n' for _ in range(USERNAME_BYTES_SIZE - len(username_encoded))])
        else:
            raise ValueError(f"Username width {len(username_encoded)} > {USERNAME_BYTES_SIZE} (USERNAME_BYTES_SIZE)")

        content_encoded = self._content.encode(ENCODING)
        if len(content_encoded) <= CONTENT_BYTE_SIZE:
            content_encoded += b''.join([b'\n' for _ in range(CONTENT_BYTE_SIZE - len(content_encoded))])
        else:
            raise ValueError(f"Content width {len(content_encoded)} > {CONTENT_BYTE_SIZE} (CONTENT_BYTE_SIZE)")

        return username_encoded + content_encoded

    @classmethod
    def decode(cls, message: bytes) -> 'Message':
        username = message[:USERNAME_BYTES_SIZE].rstrip().decode(ENCODING)
        content = message[USERNAME_BYTES_SIZE:].rstrip().decode(ENCODING)

        return Message(username, content)
