"""
Copyright (c) Cutleast
"""

import hashlib
from io import BytesIO
from typing import BinaryIO, TypeAlias

Stream: TypeAlias = BinaryIO
"""Type alias for a stream of bytes."""


def peek(stream: Stream, length: int) -> bytes:
    """
    Peeks into a stream and returns the next bytes in a given amount.

    Args:
        stream (Stream): Byte-stream.
        length (int): Amount of bytes to peek.

    Returns:
        bytes: Peeked bytes.
    """

    data = stream.read(length)

    stream.seek(-length, 1)

    return data


CHAR_WHITELIST = [
    "\n",
    "\r",
    "\t",
    "\u200b",
    "\xa0",
    "\u3000",
]


STRING_BLACKLIST = [
    "<p>",
]


STRING_WHITELIST = [
    "WoollyRhino",
    "CuSith",
]


def get_checksum(number: int) -> int:
    """
    Returns horizontal checksum of a number (sum of all digits).

    Args:
        number (int): Number.

    Returns:
        int: Horizontal checksum.
    """

    number = abs(number)

    return sum(int(digit) for digit in str(number))


def deterministic_hash(data: bytes) -> int:
    """
    Calculates the hash of a byte array in a deterministic manner.

    Args:
        data (bytes): Byte array

    Returns:
        int: Deterministic hash
    """

    return int(hashlib.blake2b(data, digest_size=8).hexdigest(), base=16)


def is_camel_case(text: str) -> bool:
    """
    Checks if a text is camelCase (or PascalCase) without spaces.

    Args:
        text (str): Text

    Returns:
        bool: True if the text is camelCase (or PascalCase), False otherwise.
    """

    if len(text) < 3:
        return False

    return (
        any(char.isupper() and char.isalpha() for char in text[2:])
        and not text.isupper()
        and text.isalnum()
    )


def is_snake_case(text: str) -> bool:
    """
    Checks if a text is snake_case without spaces.

    Args:
        text (str): Text

    Returns:
        bool: True if the text is snake_case, False otherwise.
    """

    return " " not in text and "_" in text


def is_valid_string(text: str) -> bool:
    """
    Checks if a text is likely to appear in-game.

    Args:
        text (str): Text

    Returns:
        bool: True if the text is likely to appear in-game, False otherwise.
    """

    if not text.strip() or text in STRING_BLACKLIST:
        return False

    if text in STRING_WHITELIST or "<Alias" in text:
        return True

    if is_camel_case(text) or is_snake_case(text):
        return False

    return all(char.isprintable() or char in CHAR_WHITELIST for char in text)


def get_stream(data: Stream | bytes) -> Stream:
    """
    Helper method to unify the type of a stream of bytes and a raw byte array.

    Args:
        data (Stream | bytes): Stream or byte array.

    Returns:
        Stream: Byte-stream.
    """

    if isinstance(data, bytes):
        return BytesIO(data)

    return data


def read_data(data: Stream | bytes, size: int) -> bytes:
    """
    Reads data from a given amount from a stream or byte array.

    Args:
        data (Stream | bytes): Stream or byte array.
        size (int): Amount of bytes to read.

    Returns:
        bytes: Read data.
    """

    if isinstance(data, bytes):
        return data[:size]
    else:
        return data.read(size)
