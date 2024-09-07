from typing import Dict, Self
from app.parser import method_parser, urlpath_parser, version_parser, headers_parser

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


HttpHeaders = dict
HttpBody = str


class HttpRequest:
    def __init__(
        self,
        method: HttpMethod,
        urlpath: HttpUrlPath,
        version: HttpVersion,
        headers: HttpHeaders,
    ):
        self.method = method
        self.urlpath = urlpath
        self.version = version
        self.headers = headers

    @classmethod
    def from_bytes(cls, msg_bytes: bytes):
        msg = msg_bytes.decode()

        request_line = (
            method_parser() + urlpath_parser() + version_parser() + headers_parser()
        )
        try:
            result = request_line.parse_string(msg).as_dict()
        except ParseException:
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

            # \r\n

            headers = HttpHeaders(result.get("headers") or {})

        except ValueError:
            raise
        return cls(method=method, urlpath=urlpath, version=version, headers=headers)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"method={self.method},"
            f"urlpath={self.urlpath},"
            f"version={self.version},"
            f"headers={self.headers},"
            ")"
        )


class HttpResponse:
    def __init__(
        self,
        version: HttpVersion,
        status: HttpStatus,
        headers: HttpHeaders,
        body: HttpBody,
    ):
        self.version = version
        self.status = status
        self.headers = headers
        self.body = body

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"version={self.version},"
            f"status={self.status},"
            f"headers={self.headers},"
            f"body={self.body},"
            ")"
        )

    def to_bytes(self) -> bytes:
        res = f"{self.version.value} {self.status.value}\r\n"

        for key, val in self.headers.items():
            res += f"{key}: {val}\r\n"

        res += "\r\n"
        if self.body:
            res += self.body

        return res.encode()

    @classmethod
    def basic_content(
        cls,
        version: HttpVersion = HttpVersion.V1_0,
        status: HttpStatus = HttpStatus.Ok200,
        content: str = "",
    ) -> Self:
        content_len = len(content)
        body = HttpBody(content)
        print(body)

        return cls(
            version=version,
            status=status,
            headers={"Content-Length": str(content_len)},
            body=body,
        )
