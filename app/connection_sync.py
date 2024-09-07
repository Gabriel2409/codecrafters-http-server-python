import socket
from app.http import HttpRequest
from app.api import handle_req


def receive_msg(conn: socket.socket, buf_len: int = 1024):
    chunks = []

    try:
        while True:
            chunk = conn.recv(buf_len)
            if not chunk:
                break
            chunks.append(chunk)
            if len(chunk) < buf_len:
                break
    except socket.error as e:
        print(f"Socket error while receiving: {e}")

    return b"".join(chunks)


def send_msg(conn: socket.socket, msg: bytes):
    total_sent = 0
    msg_len = len(msg)

    try:
        while total_sent < msg_len:
            sent = conn.send(msg[total_sent:])
            total_sent += sent
    except socket.error as e:
        print(f"Socket error while sending: {e}")


def handle_connection(conn: socket.socket):
    """Synchronous way to handle one connection"""
    with conn:
        msg = receive_msg(conn=conn)
        req = HttpRequest.from_bytes(msg)
        res = handle_req(req)
        send_msg(conn=conn, msg=res.to_bytes())
