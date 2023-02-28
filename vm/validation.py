
from typing import (
    Any,
    Sequence,
    Union,
)
from constants import ( MAX_UINT256 )

def validate_is_bytes(value: bytes, title: str = "Value") -> None:
    if not isinstance(value, bytes):
        raise Exception(
            f"{title} must be a byte string.  Got: {type(value)}"
        )


def validate_is_integer(value: Union[int, bool], title: str = "Value") -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise Exception(
            f"{title} must be a an integer.  Got: {type(value)}"
        )


def validate_length(value: Sequence[Any], length: int, title: str = "Value") -> None:
    if not len(value) == length:
        raise Exception(
            f"{title} must be of length {length}.  Got {value} of length {len(value)}"
        )

def validate_lte(value: int, maximum: int, title: str = "Value") -> None:
    if value > maximum:
        raise Exception(
            f"{title} {value} is not less than or equal to {maximum}"
        )
    validate_is_integer(value, title=title)

def validate_uint256(value: int, title: str = "Value") -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise Exception(
            f"{title} must be an integer: Got: {type(value)}"
        )
    if value < 0:
        raise Exception(
            f"{title} cannot be negative: Got: {value}"
        )
    if value > MAX_UINT256:
        raise Exception(
            f"{title} exceeds maximum UINT256 size.  Got: {value}"
        )
