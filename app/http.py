from app.errors import CantParseRequest

from enum import Enum
from pyparsing import (
    Word,
    alphas,
    alphanums,
    Combine,
    Literal,
    Optional,
    ParseException,
)


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    PUT = "PUT"


class HttpVersion(Enum):
    V1_0 = "HTTP/1.0"
    V1_1 = "HTTP/1.1"
    V2_0 = "HTTP/2.0"


class HttpStatus(Enum):
    Ok200 = "200 OK"
    NotFound404 = "404 Not Found"
    Created201 = "201 Created"
    InternalServerError500 = "500 Internal Server Error"


class HttpRequest:
    def __init__(self, method: HttpMethod, path: str, version: HttpVersion):
        self.method = method
        self.path = path
        self.version = version

    @classmethod
    def from_bytes(cls, msg: bytes):
        method_parser = Word(alphas)
        path_parser = Combine(Literal("/") + Optional(Word(alphanums + "/?=&")))
        http_version_parser = Combine(Literal("HTTP/") + Word("1.0 1.1 2.0"))
        request_line = (
            method_parser("method")
            + path_parser("path")
            + http_version_parser("http_version")
        )
        try:
            result = request_line.parseString(msg.decode())
        except ParseException:
            raise CantParseRequest

        try:
            method = HttpMethod(result.method)
            version = HttpVersion(result.http_version)
        except ValueError:
            raise CantParseRequest
        return cls(method=method, path=result.path, version=version)


class HttpResponse:
    def __init__(self, version: HttpVersion, status: HttpStatus):
        self.version = version
        self.status = status

    def to_bytes(self) -> bytes:
        res = f"{self.version.value} {self.status.value}\r\n"

        res += "Content-Length:0\r\n\r\n"
        return res.encode()
