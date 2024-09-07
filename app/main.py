import asyncio
import multiprocessing
import socket
import threading
from concurrent.futures import ThreadPoolExecutor

from app.connection_async import handle_connection_async
from app.connection_sync import handle_connection


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


async def handle_connection_with_asyncio():
    """uses asyncio to handle the connections"""
    # Set up the async server
    server = await asyncio.start_server(
        client_connected_cb=handle_connection_async,
        host="localhost",
        port=4221,
        reuse_port=True,
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
    asyncio.run(handle_connection_with_asyncio())


if __name__ == "__main__":
    main()
