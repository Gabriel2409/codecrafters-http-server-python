from pyparsing import (
    Combine,
    FollowedBy,
    ParseException,
    ParserElement,
    Suppress,
    StringEnd,
    Word,
    WordEnd,
    alphas,
    Literal,
)


def method_parser() -> ParserElement:
    uppercase_word = Word(alphas.upper())
    valid_terminator = FollowedBy(WordEnd())

    return Combine(uppercase_word + valid_terminator)


def version_parser() -> ParserElement:
    return Combine(
        Literal("HTTP/") + (Literal("1.0") | Literal("1.1") | Literal("2.0"))
    )
