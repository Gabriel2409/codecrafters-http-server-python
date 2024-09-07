import multiprocessing
import socket
import threading
from concurrent.futures import ThreadPoolExecutor
import asyncio

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


def handle_connection(conn: socket.socket):
    with conn:
        msg = receive_msg(conn=conn)
        req = HttpRequest.from_bytes(msg)

        match req.urlpath.path:
            case "":
                res = HttpResponse.empty(status=HttpStatus.Ok200)

            case "user-agent":
                user_agent = req.headers.get("User-Agent", "")
                res = HttpResponse.text_content(
                    status=HttpStatus.Ok200, content=user_agent
                )

            case x if x.startswith("echo/"):
                res = HttpResponse.text_content(status=HttpStatus.Ok200, content=x[5:])
            case _:
                res = HttpResponse.empty(status=HttpStatus.NotFound404)

        send_msg(conn=conn, msg=res.to_bytes())


def handle_connection_with_multiprocessing_pool():
    """uses a pool of workers to handle concurrent connections"""
    pool = multiprocessing.Pool(processes=4)
    with socket.create_server(("localhost", 4221), reuse_port=True) as server_socket:
        with pool:
            while True:
                conn, address = server_socket.accept()

                # handle_connection(conn)
                pool.apply_async(handle_connection, (conn,))


def handle_connection_with_multithreading_naive():
    """Spawns a new thread per connection. A bit naive because we can spawn a very
    large nb of threads"""
    threads = []
    try:
        with socket.create_server(
            ("localhost", 4221), reuse_port=True
        ) as server_socket:
            while True:
                conn, address = server_socket.accept()
                thread = threading.Thread(target=handle_connection, args=(conn,))
                thread.start()
                threads.append(thread)
    except KeyboardInterrupt:
        for thread in threads:
            thread.join()

    print("All threads have finished")


def handle_connection_with_thread_pool():
    """Uses the high level interface from concurrent futures to manage a
    threadpool"""
    max_threads = 4
    try:
        with socket.create_server(
            ("localhost", 4221), reuse_port=True
        ) as server_socket:
            with ThreadPoolExecutor(max_threads) as executor:
                while True:
                    conn, address = server_socket.accept()
                    executor.submit(handle_connection, conn)
    except KeyboardInterrupt:
        print("Shutting down")


# Wrapper to run synchronous function in an executor
async def handle_connection_async(reader, writer, semaphore):
    async with semaphore:
        loop = asyncio.get_event_loop()
        conn = writer.transport.get_extra_info("socket")

        # Run the synchronous function in a separate thread
        await loop.run_in_executor(None, handle_connection, conn)

        writer.close()
        await writer.wait_closed()


async def handle_connection_with_asyncio():
    """uses asyncio to handle the connections"""
    max_connections = 4
    semaphore = asyncio.Semaphore(max_connections)
    server = await asyncio.start_server(
        lambda r, w: handle_connection_async(r, w, semaphore), "localhost", 4221
    )
    async with server:
        print("Server listening on port 4221...")
        await server.serve_forever()


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage

    # Multiprocessing solution ####################
    # handle_connection_with_multiprocessing_pool()

    # Multithreading naive solution ###############
    # handle_connection_with_multithreading_naive()

    # Multithreading thread pool solution ########
    # handle_connection_with_thread_pool()

    # Asyncio solution #########################
    # asyncio.run(handle_connection_with_asyncio())


if __name__ == "__main__":
    main()
