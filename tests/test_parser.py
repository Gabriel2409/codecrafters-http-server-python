from pyparsing import ParseException, Word, alphas
import pytest
from app.http import HttpMethod, HttpUrlPath, HttpVersion
from app.parser import method_parser, version_parser, urlpath_parser


def test_method_parser():
    m_parser = method_parser()("method")

    for msg in ["GET", "POST something", "DELETE ", " PUT"]:
        result = m_parser.parse_string(msg)
        # check that we can convert to a method and that the value is correct
        assert HttpMethod(result.method).value == msg.strip().split()[0]

    for msg in ["get", "Boom", "GET1"]:
        with pytest.raises(ParseException):
            m_parser.parse_string(msg)


def test_urlpath_parser():
    u_parser = urlpath_parser()
    for msg in [
        "https://example.com?a=bddf&c=w",
        "https://example.com/?a=b",
        "https://example.com:80",
        "https://example.com:80/",
        "https://example.com/a/b?qq=gg&ff=yy",
        "https://www.example.com:80/a/",
        "https://www.example.com:80/a/b/",
        "/",
        "/ bonjour",
        "/app followed",
        "/app/",
        "/app/",
        "/?a=b",
        "/a/b?a=b",
        "*",
    ]:
        result = u_parser.parse_string(msg).as_dict()

        query_params = dict(result.get("query_params", {}))
        # print(msg, result)
        # check that conversion to HttpUrlPath works
        http_url_path = HttpUrlPath(
            result.get("host"), result.get("path") or "", query_params
        )
        print(msg, http_url_path.path)

        print(http_url_path)


def test_version_parser():
    v_parser = version_parser()("version")
    for msg in [" HTTP/1.1 ", " HTTP/1.0 ", "HTTP/2.0"]:
        result = v_parser.parse_string(msg)
        print(result.version)
        # check that we can convert to a version and that the value is correct
        assert HttpVersion(result.version).value == msg.strip().split()[0]

    for msg in ["http/1.1", "test", "HTTP/3"]:
        with pytest.raises(ParseException):
            v_parser.parse_string(msg)


def test_combination_parser():
    comb_parser = method_parser() + urlpath_parser() + version_parser()
    msg = """GET / HTTP/1.1
Host: localhost:4221
User-Agent: curl/8.9.1
Accept: */*
    """
    msg = "GET /a HTTP/1.1"
    result = comb_parser.parse_string(msg).as_dict()
    print(result)
    print()
