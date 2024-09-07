"""Alternative way to handle connections in an async way (for use with asyncio for ex)"""

import asyncio
import socket
from app.http import HttpRequest
from app.api import handle_req


async def receive_msg_async(reader: asyncio.StreamReader, buf_len: int = 1024) -> bytes:
    chunks = []
    while True:
        chunk = await reader.read(1024)
        if not chunk:
            break
        chunks.append(chunk)
        if len(chunk) < buf_len:
            break
    return b"".join(chunks)


async def send_msg_async(writer: asyncio.StreamWriter, msg: bytes):
    writer.write(msg)
    await writer.drain()


async def handle_connection_async(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter, directory: str | None
):
    """Synchronous way to handle one connection"""

    msg = await receive_msg_async(reader)
    req = HttpRequest.from_bytes(msg)
    res = handle_req(req, directory=directory)
    await send_msg_async(writer, msg=res.to_bytes())
    writer.close()
    await writer.wait_closed()
