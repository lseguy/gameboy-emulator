def get_bit(byte: int, bit_position: int) -> int:
    return (byte >> bit_position) & 1


def set_bit(byte: int, bit_position: int, new_value: int) -> int:
    mask = 0xff ^ (1 << bit_position)
    return byte & mask | new_value << bit_position


def read_signed(byte: int) -> int:
    # the number is negative if the MSB is 1
    if byte & (1 << 7):
        # compute the two's complement
        abs_value = (~byte & 0xff) + 1
        return -abs_value

    # the number is positive, clear the sign bit
    return set_bit(byte, 7, 0)
