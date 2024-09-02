import socket


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage

    with socket.create_server(("localhost", 4221), reuse_port=True) as server_socket:
        while True:
            conn, address = server_socket.accept()
            res = b"HTTP/1.1 200 OK\r\n\r\n"
            print(res)
            conn.sendall(res)


if __name__ == "__main__":
    main()
