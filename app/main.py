import socket

from pyparsing import alphanums
from app.http import HttpRequest, HttpResponse, HttpStatus, HttpVersion, HttpMethod


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


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage

    with socket.create_server(("localhost", 4221), reuse_port=True) as server_socket:
        while True:
            conn, address = server_socket.accept()
            with conn:
                msg = receive_msg(conn=conn)
                req = HttpRequest.from_bytes(msg)

                print(req.urlpath.path)
                match req.urlpath.path:
                    case "":
                        res = HttpResponse.basic_content(status=HttpStatus.Ok200)
                    case x if x.startswith("echo/"):
                        print(x)
                        res = HttpResponse.basic_content(
                            status=HttpStatus.Ok200, content=x[5:]
                        )
                    case _:
                        res = HttpResponse.basic_content(status=HttpStatus.NotFound404)

                send_msg(conn=conn, msg=res.to_bytes())


if __name__ == "__main__":
    main()
