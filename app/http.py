import gzip
from io import BytesIO
from typing import Dict, Self
from app.parser import (
    body_parser,
    method_parser,
    urlpath_parser,
    version_parser,
    headers_parser,
)

from enum import Enum
from pyparsing import Optional, ParseException


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
    Conflict409 = "409 Conflict"
    InternalServerError500 = "500 Internal Server Error"


class HttpUrlPath:
    def __init__(self, host: str | None, path: str, query_params: Dict[str, str]):
        self.host = host
        self.path = path
        self.query_params = query_params

    def __repr__(self):
        return f"{self.__class__.__name__}(host={self.host}, path={self.path}, query_params={self.query_params})"


HttpHeaders = dict
HttpBody = str | bytes


class HttpRequest:
    def __init__(
        self,
        method: HttpMethod,
        urlpath: HttpUrlPath,
        version: HttpVersion,
        headers: HttpHeaders,
        body: HttpBody,
    ):
        self.method = method
        self.urlpath = urlpath
        self.version = version
        self.headers = headers
        self.body = body

    @classmethod
    def from_bytes(cls, msg_bytes: bytes):
        msg = msg_bytes.decode()

        request_line = (
            method_parser()
            + urlpath_parser()
            + version_parser()
            + Optional(headers_parser())
            + Optional(body_parser())
        )
        try:
            result = request_line.parse_string(msg).as_dict()
        except ParseException:
            print(msg)
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

            headers = HttpHeaders(result.get("headers", {}))
            body: str = result.get("body", "")

        except ValueError:
            raise
        return cls(
            method=method, urlpath=urlpath, version=version, headers=headers, body=body
        )

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
        res: str = f"{self.version.value} {self.status.value}\r\n"

        for key, val in self.headers.items():
            res += f"{key}: {val}\r\n"

        res += "\r\n"

        if self.body:
            if isinstance(self.body, bytes):
                return res.encode() + self.body
            elif isinstance(self.body, str):
                res += self.body
                return res.encode()
            else:
                return res.encode()
        else:
            return res.encode()

    @classmethod
    def empty(
        cls,
        version: HttpVersion = HttpVersion.V1_1,
        status: HttpStatus = HttpStatus.Ok200,
    ) -> Self:
        return cls(
            version=version,
            status=status,
            headers={"Content-Length": "0"},
            body="",
        )

    @classmethod
    def text_content(
        cls,
        version: HttpVersion = HttpVersion.V1_1,
        status: HttpStatus = HttpStatus.Ok200,
        content: str = "",
        content_type: str = "text/plain",
        content_encoding: str | None = None,
    ) -> Self:
        content_len = len(content)
        body = content
        headers = {"Content-Type": content_type, "Content-Length": str(content_len)}

        if content_encoding == "gzip":
            headers["Content-Encoding"] = "gzip"
            body = gzip.compress(content.encode(), compresslevel=6)
            headers["Content-Length"] = str(len(body))
        return cls(
            version=version,
            status=status,
            headers=headers,
            body=body,
        )
