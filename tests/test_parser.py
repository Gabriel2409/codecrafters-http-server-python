from pyparsing import ParseException, Word, alphas
import pytest
from app.http import HttpMethod, HttpVersion
from app.parser import method_parser, version_parser


def test_parse_method():
    m_parser = method_parser()("method")

    for msg in ["GET", "POST something", "DELETE ", " PUT"]:
        result = m_parser.parse_string(msg)
        # check that we can convert to a method and that the value is correct
        assert HttpMethod(result.method).value == msg.strip().split()[0]

    for msg in ["get", "Boom", "GET1"]:
        with pytest.raises(ParseException):
            m_parser.parse_string(msg)


def test_parse_version():
    v_parser = version_parser()("version")
    for msg in [" HTTP/1.1 ", " HTTP/1.0 ", "HTTP/2.0"]:
        result = v_parser.parse_string(msg)
        print(result.version)
        # check that we can convert to a version and that the value is correct
        assert HttpVersion(result.version).value == msg.strip().split()[0]

    for msg in ["http/1.1", "test", "HTTP/3"]:
        with pytest.raises(ParseException):
            v_parser.parse_string(msg)
