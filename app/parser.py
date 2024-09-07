from pyparsing import (
    Combine,
    DelimitedList,
    Dict,
    FollowedBy,
    Group,
    LineEnd,
    OneOrMore,
    Or,
    ParserElement,
    Word,
    WordEnd,
    Literal,
    Optional,
    Regex,
    Suppress,
    ZeroOrMore,
    alphanums,
    alphas,
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
    segment = Word(alphanums + "-_")
    dot = Literal(".")
    slash = Literal("/")
    tld = Word(alphas, min=2, max=6)

    http_parser = Literal("http") + Optional(Literal("s")) + Literal("://")
    host_parser = Combine(OneOrMore(segment + dot) + tld)
    port_parser = Literal(":") + Word(nums)
    full_host_parser = Combine(
        (
            (
                Suppress(http_parser)
                + host_parser
                + Optional(port_parser)
                + Suppress(Optional(slash))
            )
            | Suppress(slash)
        )
    )
    path_parser = Combine(
        segment + ZeroOrMore(slash + segment) + Suppress(Optional(slash))
    )

    key_val_parser = Group(segment + Suppress(Literal("=")) + segment)

    query_params_parser = Suppress(Literal("?")) + Dict(
        DelimitedList(key_val_parser, delim="&", allow_trailing_delim=False)
    )

    return Or(
        (
            Combine(
                full_host_parser.set_results_name("host")
                + Optional(path_parser).set_results_name("path")
                + Optional(query_params_parser).set_results_name("query_params")
            ),
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


def headers_parser() -> ParserElement:
    segment = Word(alphanums + "-_/*.")
    segment_with_colon = Word(alphanums + "-_/*.:")

    key_val_parser = Group(segment + Suppress(Literal(": ")) + segment_with_colon)
    return DelimitedList(
        key_val_parser, LineEnd(), allow_trailing_delim=True
    ).set_results_name("headers")
