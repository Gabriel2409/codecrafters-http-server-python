from typing import Dict
from app.errors import CantParseRequest
from app.parser import method_parser, urlpath_parser, version_parser

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


class HttpUrlPath:
    def __init__(self, host: str | None, path: str, query_params: Dict[str, str]):
        self.host = host
        self.path = path
        self.query_params = query_params

    def __repr__(self):
        return f"{self.__class__.__name__}(host={self.host}, path={self.path}, query_params={self.query_params})"


class HttpRequest:
    def __init__(self, method: HttpMethod, path: HttpUrlPath, version: HttpVersion):
        self.method = method
        self.path = path
        self.version = version

    @classmethod
    def from_bytes(cls, msg_bytes: bytes):
        msg = msg_bytes.decode()

        request_line = method_parser() + urlpath_parser() + version_parser()
        try:
            print(msg)

            result = request_line.parse_string(msg).as_dict()
        except ParseException:
            # raise CantParseRequest
            raise

        try:
            method = HttpMethod(result.get("method"))

            path = result.get("path", "")
            host = result.get("host")
            query_params = dict(result.get("query_params") or {})

            urlpath = HttpUrlPath(
                host=host,
                path=path,
                query_params=query_params,
            )

            version = HttpVersion(result.get("version"))

        except ValueError:
            raise CantParseRequest
        return cls(method=method, path=urlpath, version=version)


class HttpResponse:
    def __init__(self, version: HttpVersion, status: HttpStatus):
        self.version = version
        self.status = status

    def to_bytes(self) -> bytes:
        res = f"{self.version.value} {self.status.value}\r\n"

        res += "Content-Length:0\r\n\r\n"
        return res.encode()
