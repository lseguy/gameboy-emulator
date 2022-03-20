from typing import Tuple
from typing import TypeVar

from custom_types import i8
from custom_types import u16
from custom_types import u8


def get_bit(byte: int, bit_position: int) -> int:
    return (byte >> bit_position) & 1


T = TypeVar('T', bound=int)


def set_bit(byte: T, bit_position: int, new_value: int) -> T:
    mask = 0xff ^ (1 << bit_position)
    return byte & mask | new_value << bit_position


def read_signed(byte: int) -> i8:
    # the number is negative if the MSB is 1
    if byte & (1 << 7):
        # compute the two's complement
        abs_value = (~byte & 0xff) + 1
        return i8(-abs_value)

    # the number is positive, clear the sign bit
    value = set_bit(byte, 7, 0)
    return i8(value)


def combine_bytes(left: u8, right: u8) -> u16:
    return u16((left << 8) | right)


def split_bytes(value: u16) -> Tuple[u8, u8]:
    return u8(value >> 8), u8(value & 0xff)
