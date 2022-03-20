from cpu.registers import Registers
from custom_types import i8
from custom_types import u16
from custom_types import u8
from utils.bit_operations import get_bit
from utils.bit_operations import set_bit


def xor(registers: Registers, lhs: u8, rhs: u8) -> bool:
    result = lhs ^ rhs
    # The result always goes into register A
    registers.a = u8(result)
    registers.z_flag = result == 0
    registers.n_flag = False
    registers.h_flag = False
    registers.c_flag = False

    return False


def logical_or(registers: Registers, lhs: u8, rhs: u8) -> bool:
    result = lhs | rhs
    # The result always goes into register A
    registers.a = u8(result)
    registers.z_flag = result == 0
    registers.n_flag = False
    registers.h_flag = False
    registers.c_flag = False

    return False


def logical_and(registers: Registers, lhs: u8, rhs: u8) -> bool:
    result = lhs & rhs
    # The result always goes into register A
    registers.a = u8(result)
    registers.z_flag = result == 0
    registers.n_flag = False
    registers.h_flag = True
    registers.c_flag = False

    return False


def subtract_u8(registers: Registers, lhs: u8, rhs: u8) -> u8:
    result = (lhs - rhs) & 0xff
    # The result always goes into register A
    registers.z_flag = result == 0
    registers.n_flag = True
    registers.h_flag = (rhs & 0x0f) > (lhs & 0x0f)
    registers.c_flag = rhs > lhs

    return u8(result)


def subtract_u8_with_carry(registers: Registers, lhs: u8, rhs: u8) -> u8:
    carry = int(registers.c_flag)
    result = (lhs - rhs - carry) & 0xff

    registers.z_flag = result == 0
    registers.n_flag = True
    registers.h_flag = ((rhs & 0x0f) + carry) > (lhs & 0x0f)
    registers.c_flag = rhs + carry > lhs

    return u8(result)


def compare(registers: Registers, value: u8) -> bool:
    subtract_u8(registers, registers.a, value)
    return False


def test_bit(registers: Registers, byte: int, bit_position: int) -> bool:
    is_set = get_bit(byte, bit_position)
    registers.z_flag = not is_set
    registers.n_flag = False
    registers.h_flag = True

    return False


def swap(registers: Registers, byte: u8) -> u8:
    result = ((byte << 4) & 0xff) | byte >> 4
    registers.z_flag = result == 0
    registers.n_flag = False
    registers.h_flag = False
    registers.c_flag = False

    return u8(result)


def add_sp(registers: Registers, offset: i8) -> u16:
    result = (registers.sp + offset) & 0xffff
    registers.z_flag = False
    registers.n_flag = False
    registers.h_flag = (result & 0xf) <= (registers.sp & 0xf)
    registers.c_flag = (result & 0xff) < (registers.sp & 0xff)

    return u16(result)


def add_u8(registers: Registers, lhs: u8, rhs: u8) -> u8:
    result = (lhs + rhs) & 0xff

    registers.z_flag = result == 0
    registers.n_flag = False
    registers.h_flag = (lhs & 0x0f) + (rhs & 0x0f) > 0x0f
    registers.c_flag = (lhs + rhs) > 0xff

    return u8(result)


def add_u8_with_carry(registers: Registers, lhs: u8, rhs: u8) -> u8:
    carry = int(registers.c_flag)
    result = (lhs + rhs + carry) & 0xff

    registers.z_flag = result == 0
    registers.n_flag = False
    registers.h_flag = (lhs & 0x0f) + (rhs & 0x0f) + carry > 0x0f
    registers.c_flag = (lhs + rhs + carry) > 0xff

    return u8(result)


def add_u16(registers: Registers, lhs: u16, rhs: u16) -> u16:
    result = (lhs + rhs) & 0xffff

    registers.n_flag = False
    registers.h_flag = (lhs & 0x0fff) + (rhs & 0x0fff) > 0x0fff
    registers.c_flag = (lhs + rhs) > 0xffff

    return u16(result)


def inc_u8(registers: Registers, value: u8) -> u8:
    result = (value + 1) & 0xff
    registers.z_flag = result == 0
    registers.n_flag = False
    registers.h_flag = (0x0f & result) < (0x0f & value)

    return u8(result)


def inc_u16(value: u16) -> u16:
    result = (value + 1) & 0xffff
    # Flags are not affected for increments on u16 registers
    return u16(result)


def dec_u8(registers: Registers, value: u8) -> u8:
    result = (value - 1) & 0xff
    registers.z_flag = result == 0
    registers.n_flag = True
    registers.h_flag = (0x0f & value) == 0

    return u8(result)


def dec_u16(value: u16) -> u16:
    result = (value - 1) & 0xffff
    # Flags are not affected for decrements on u16 registers
    return u16(result)


def complement(registers: Registers) -> bool:
    registers.a = ~registers.a & 0xff
    registers.n_flag = True
    registers.h_flag = True

    return False


def complement_carry_flag(registers: Registers) -> bool:
    registers.c_flag = not registers.c_flag
    registers.n_flag = False
    registers.h_flag = False

    return False


def set_carry_flag(registers: Registers) -> bool:
    registers.c_flag = True
    registers.n_flag = False
    registers.h_flag = False

    return False


def rotate_left(registers: Registers, value: u8, through_carry: bool = False, reset_z_flag: bool = False) -> u8:
    result = (value << 1) & 0xff
    msb = get_bit(value, 7)

    if through_carry:
        result |= 0x1 if registers.c_flag else 0x0
    else:
        result |= msb

    if reset_z_flag:
        registers.z_flag = False
    else:
        registers.z_flag = result == 0
    registers.n_flag = False
    registers.h_flag = False
    registers.c_flag = msb != 0

    return u8(result)


def rotate_right(registers: Registers, value: u8, through_carry: bool = False, reset_z_flag: bool = False) -> u8:
    result = value >> 1
    lsb = get_bit(value, 0)

    if through_carry:
        result = set_bit(result, 7, 0x1 if registers.c_flag else 0x0)
    else:
        result = set_bit(result, 7, lsb)

    if reset_z_flag:
        registers.z_flag = False
    else:
        registers.z_flag = result == 0
    registers.n_flag = False
    registers.h_flag = False
    registers.c_flag = lsb != 0

    return u8(result)


def shift_right_logical(registers: Registers, value: u8) -> u8:
    result = value >> 1

    registers.z_flag = result == 0
    registers.n_flag = False
    registers.h_flag = False
    registers.c_flag = value & 0x1 != 0

    return u8(result)


def shift_right_arithmetic(registers: Registers, value: u8) -> u8:
    result = value >> 1

    msb = value >> 7
    result = set_bit(result, 7, msb)

    registers.z_flag = result == 0
    registers.n_flag = False
    registers.h_flag = False
    registers.c_flag = value & 0x1 != 0

    return u8(result)


def shift_left(registers: Registers, value: u8) -> u8:
    result = (value << 1) & 0xff

    registers.z_flag = result == 0
    registers.n_flag = False
    registers.h_flag = False
    registers.c_flag = get_bit(value, 7) != 0

    return u8(result)


def daa(registers: Registers) -> bool:
    result = registers.a

    if registers.n_flag:
        if registers.h_flag:
            result -= 0x06
        if registers.c_flag:
            result -= 0x60
    else:
        if (result & 0x0f) > 9 or registers.h_flag:
            result += 0x06
        if result > 0x9f or registers.c_flag:
            result += 0x60
            registers.c_flag = True

    result &= 0xff
    registers.z_flag = result == 0
    registers.h_flag = False

    registers.a = result

    return False
