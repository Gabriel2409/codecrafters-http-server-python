from pyparsing import (
    Combine,
    DelimitedList,
    FollowedBy,
    Or,
    ParserElement,
    Word,
    WordEnd,
    Literal,
    Optional,
    Regex,
    Suppress,
    nums,
)


def method_parser() -> ParserElement:
    """Parses GET, POST, DELETE, PUT if not followed by a character"""
    return Combine(
        Or((Literal("GET"), Literal("POST"), Literal("DELETE"), Literal("PUT")))
        + FollowedBy(WordEnd())
    ).set_results_name("method")


def urlpath_parser() -> ParserElement:
    """
    Url can have different patterns:
    - origin-form: absolute-path ["?" query], for ex: /where?q=now, /, /?p=here
    - absolute-form: url + absolute-path http://example.org/test
        (/ is optional for root address contrary to origin-form)
    - authority-form = uri-host ":" port
    - asterisk-form = "*"


    If using a as_dict after parsing string, will return the `host` (if provided), the
    `path` (without first training slash) as well as the `query_params` in a dict
    """

    http_parser = Literal("http") + Optional(Literal("s")) + Literal("://")
    host_parser = Regex(r"(([a-zA-Z0-9_-])+\.)+[a-z]{2,6}")
    port_parser = Literal(":") + Word(nums)
    full_host_parser = Combine(
        (
            (
                Suppress(http_parser)
                + host_parser
                + Optional(port_parser)
                + Suppress(Optional(Literal("/")))
            )
            | Suppress(Literal("/"))
        )
    )

    path_parser = Combine(
        Regex(r"(([a-zA-Z0-9_-])+/)+[a-zA-Z0-9_-]") + Suppress(Optional(Literal("/")))
    )

    key_val_parser = Regex(r"(([a-zA-Z0-9_-])+=([a-zA-Z0-9_-])+)")
    query_params_parser = Suppress(Literal("?")) + DelimitedList(
        key_val_parser, delim="&", allow_trailing_delim=False
    )

    return Or(
        (
            full_host_parser.set_results_name("host")
            + Optional(path_parser).set_results_name("path")
            + Optional(query_params_parser).set_results_name("query_params"),
            Literal("*").set_results_name("host"),
        )
    ) + FollowedBy(WordEnd())


def version_parser() -> ParserElement:
    """Parses HTTP/{1.0|1.1|1.2} if not followed by a character"""
    return Combine(
        Literal("HTTP/")
        + (Literal("1.0") | Literal("1.1") | Literal("2.0"))
        + FollowedBy(WordEnd())
    ).set_results_name("version")
