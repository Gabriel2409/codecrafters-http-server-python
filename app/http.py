from enum import Enum


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"


class HttpVersion(Enum):
    V1_1 = "HTTP/1.1"


class HttpStatus(Enum):
    Ok200 = "200 OK"
    NotFound404 = "404 Not Found"
    Created201 = "201 Created"
    InternalServerError500 = "500 Internal Server Error"


class HttpResponse:
    def __init__(self, version: HttpVersion, status: HttpStatus):
        self.version = version
        self.status = status

    def to_bytes(self) -> bytes:
        res = f"{self.version.value} {self.status.value}\r\n"

        res += "Content-Length:0\r\n\r\n"
        return res.encode()
