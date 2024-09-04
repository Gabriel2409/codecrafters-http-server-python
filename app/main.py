import socket
from app.http import HttpResponse, HttpStatus, HttpVersion


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage

    with socket.create_server(("localhost", 4221), reuse_port=True) as server_socket:
        while True:
            conn, address = server_socket.accept()
            with conn:
                req = conn.recv(1024)
                print(req.decode())

                res = HttpResponse(version=HttpVersion.V1_1, status=HttpStatus.Ok200)
                conn.sendall(res.to_bytes())


if __name__ == "__main__":
    main()
