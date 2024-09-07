import asyncio
import multiprocessing
import socket
import threading
from concurrent.futures import ThreadPoolExecutor
import argparse

from app.connection_async import handle_connection_async
from app.connection_sync import handle_connection


def handle_connection_with_multiprocessing_pool(directory: str):
    """uses a pool of workers to handle concurrent connections"""
    pool = multiprocessing.Pool(processes=4)
    with socket.create_server(("localhost", 4221), reuse_port=True) as server_socket:
        with pool:
            while True:
                conn, address = server_socket.accept()

                # handle_connection(conn)
                pool.apply_async(handle_connection, (conn, directory))


def handle_connection_with_multithreading_naive(directory):
    """Spawns a new thread per connection. A bit naive because we can spawn a very
    large nb of threads"""
    threads = []
    try:
        with socket.create_server(
            ("localhost", 4221), reuse_port=True
        ) as server_socket:
            while True:
                conn, address = server_socket.accept()
                thread = threading.Thread(
                    target=handle_connection, args=(conn, directory)
                )
                thread.start()
                threads.append(thread)
    except KeyboardInterrupt:
        for thread in threads:
            thread.join()

    print("All threads have finished")


def handle_connection_with_thread_pool(directory):
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
                    executor.submit(handle_connection, conn=conn, directory=directory)
    except KeyboardInterrupt:
        print("Shutting down")


async def handle_connection_with_asyncio(directory):
    """uses asyncio to handle the connections"""
    # Set up the async server
    server = await asyncio.start_server(
        client_connected_cb=lambda r, w: handle_connection_async(r, w, directory),
        host="localhost",
        port=4221,
        reuse_port=True,
    )

    async with server:
        print("Server listening on port 4221...")
        await server.serve_forever()


def main():
    """Launches tcp server
    Current benchmark with `oha -n 100 --burst-delay 2ms --burst-rate 4 http://localhost:4221`
    - handle_connection_with_multiprocessing_pool() -> 93/100
    - handle_connection_with_multithreading_naive() -> 83/100
    - handle_connection_with_thread_pool() -> 83/100
    - asyncio.run(handle_connection_with_asyncio()) -> 68/100

    Note: Benchmark in the rust implementation: 100/100
    """

    print("Logs from your program will appear here!")
    parser = argparse.ArgumentParser(
        prog="Http server", description="A simple http server"
    )
    parser.add_argument("--directory", help="directory where files are stored")
    args = parser.parse_args()

    # Uncomment this to pass the first stage

    # Multiprocessing solution ####################
    # handle_connection_with_multiprocessing_pool(directory=args.directory)

    # Multithreading naive solution ###############
    # handle_connection_with_multithreading_naive(directory=args.directory)

    # Multithreading thread pool solution ########
    handle_connection_with_thread_pool(directory=args.directory)

    # Asyncio solution #########################
    # asyncio.run(handle_connection_with_asyncio(directory=args.directory))


if __name__ == "__main__":
    main()
