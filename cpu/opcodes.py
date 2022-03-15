from cpu.instruction import CPUInstruction
from cpu.registers import Registers
from custom_types import i8
from custom_types import u16
from mmu.memory import Memory
from custom_types import u8
from utils.bit_operations import combine_bytes
from utils.bit_operations import get_bit
from utils.bit_operations import set_bit
from utils.bit_operations import split_bytes


def set_register(registers: Registers, register_name: str, value: int) -> None:
    setattr(registers, register_name, value)


def read_mem_inc_hl(registers: Registers, memory: Memory) -> u8:
    value = memory.read(registers.hl)
    registers.hl = u16(registers.hl + 1)
    return value


def read_mem_dec_hl(registers: Registers, memory: Memory) -> u8:
    value = memory.read(registers.hl)
    registers.hl = u16(registers.hl - 1)
    return value


def write_mem_dec_hl(registers: Registers, memory: Memory, value: u8) -> None:
    memory.write_u8(registers.hl, value)
    registers.hl = u16(registers.hl - 1)


def write_mem_inc_hl(registers: Registers, memory: Memory, value: u8) -> None:
    memory.write_u8(registers.hl, value)
    registers.hl = u16(registers.hl + 1)


# TODO: Move arithmetic operations to APU module
def xor(registers: Registers, lhs: u8, rhs: u8) -> None:
    result = lhs ^ rhs
    # The result always goes into register A
    registers.a = u8(result)
    registers.z_flag = result == 0
    registers.n_flag = False
    registers.h_flag = False
    registers.c_flag = False


def logical_or(registers: Registers, lhs: u8, rhs: u8) -> None:
    result = lhs | rhs
    # The result always goes into register A
    registers.a = u8(result)
    registers.z_flag = result == 0
    registers.n_flag = False
    registers.h_flag = False
    registers.c_flag = False


def logical_and(registers: Registers, lhs: u8, rhs: u8) -> None:
    result = lhs & rhs
    # The result always goes into register A
    registers.a = u8(result)
    registers.z_flag = result == 0
    registers.n_flag = False
    registers.h_flag = True
    registers.c_flag = False


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


def compare(registers: Registers, value: u8) -> None:
    subtract_u8(registers, registers.a, value)


def test_bit(registers: Registers, byte: int, bit_position: int) -> None:
    is_set = get_bit(byte, bit_position)
    registers.z_flag = not is_set
    registers.n_flag = False
    registers.h_flag = True


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


def complement(registers: Registers) -> None:
    registers.a = ~registers.a & 0xff
    registers.n_flag = True
    registers.h_flag = True


def complement_carry_flag(registers: Registers) -> None:
    registers.c_flag = not registers.c_flag
    registers.n_flag = False
    registers.h_flag = False


def set_carry_flag(registers: Registers) -> None:
    registers.c_flag = True
    registers.n_flag = False
    registers.h_flag = False


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


def jump(registers: Registers, dest: u16, condition: bool = True) -> None:
    if condition:
        registers.pc = dest


def relative_jump(registers: Registers, offset: i8, condition: bool = True) -> None:
    if condition:
        registers.pc = u16(registers.pc + offset)


def call(registers: Registers, memory: Memory, dest: u16, condition: bool = True) -> None:
    if condition:
        push_stack(registers, memory, registers.pc)
        registers.pc = dest


def disable_interrupts(memory: Memory) -> None:
    # TODO: Implement delay
    memory.ime = False
    pass


def enable_interrupts(memory: Memory) -> None:
    # TODO: Implement delay
    memory.ime = True
    pass


def ret(registers: Registers, memory: Memory, condition: bool = True) -> None:
    if condition:
        dest = pop_stack(registers, memory)
        registers.pc = dest


def reti(registers: Registers, memory: Memory) -> None:
    ret(registers, memory)
    enable_interrupts(memory)


def push_stack(registers: Registers, memory: Memory, value: u16) -> None:
    msb, lsb = split_bytes(value)

    registers.sp = u16(registers.sp - 1)
    memory.write_u8(registers.sp, msb)
    registers.sp = u16(registers.sp - 1)
    memory.write_u8(registers.sp, lsb)


def pop_stack(registers: Registers, memory: Memory) -> u16:
    lsb = memory.read(registers.sp)
    registers.sp = u16(registers.sp + 1)
    msb = memory.read(registers.sp)
    registers.sp = u16(registers.sp + 1)

    return combine_bytes(msb, lsb)


def restart(registers: Registers, memory: Memory, dest: u16) -> None:
    push_stack(registers, memory, registers.pc)
    jump(registers, dest)


def daa(registers: Registers) -> None:
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


def noop(*args) -> None:
    pass


# TODO: Use opcode table structure and loops to generate some opcodes
opcodes = {
    0x00: CPUInstruction(
        name='NOP',
        length=1,
        cycles=4,
        opcode=0x00,
        run=noop,
    ),
    0x01: CPUInstruction(
        name='LD BC,u16',
        length=3,
        cycles=12,
        opcode=0x01,
        run=lambda r, m, o: set_register(r, 'bc', o.to_dword()),
    ),
    0x02: CPUInstruction(
        name='LD (BC),A',
        length=1,
        cycles=8,
        opcode=0x02,
        run=lambda r, m, o: m.write_u8(r.bc, r.a),
    ),
    0x03: CPUInstruction(
        name='INC BC',
        length=1,
        cycles=8,
        opcode=0x03,
        run=lambda r, m, o: set_register(r, 'bc', inc_u16(r.bc)),
    ),
    0x04: CPUInstruction(
        name='INC B',
        length=1,
        cycles=4,
        opcode=0x04,
        run=lambda r, m, o: set_register(r, 'b', inc_u8(r, r.b)),
    ),
    0x05: CPUInstruction(
        name='DEC B',
        length=1,
        cycles=4,
        opcode=0x05,
        run=lambda r, m, o: set_register(r, 'b', dec_u8(r, r.b)),
    ),
    0x06: CPUInstruction(
        name='LD B,u8',
        length=2,
        cycles=8,
        opcode=0x06,
        run=lambda r, m, o: set_register(r, 'b', o.to_word()),
    ),
    0x07: CPUInstruction(
        name='RLCA',
        length=1,
        cycles=4,
        opcode=0x07,
        run=lambda r, m, o: set_register(r, 'a', rotate_left(r, r.a, reset_z_flag=True)),
    ),
    0x08: CPUInstruction(
        name='LD (u16),SP',
        length=3,
        cycles=20,
        opcode=0x08,
        run=lambda r, m, o: m.write_u16(o.to_dword(), r.sp),
    ),
    0x09: CPUInstruction(
        name='ADD HL,BC',
        length=1,
        cycles=8,
        opcode=0x09,
        run=lambda r, m, o: set_register(r, 'hl', add_u16(r, r.hl, r.bc)),
    ),
    0x0a: CPUInstruction(
        name='LD A,(BC)',
        length=1,
        cycles=8,
        opcode=0x0a,
        run=lambda r, m, o: set_register(r, 'a', m.read(r.bc)),
    ),
    0x0b: CPUInstruction(
        name='DEC BC',
        length=1,
        cycles=8,
        opcode=0x0b,
        run=lambda r, m, o: set_register(r, 'bc', dec_u16(r.bc)),
    ),
    0x0c: CPUInstruction(
        name='INC C',
        length=1,
        cycles=4,
        opcode=0x0c,
        run=lambda r, m, o: set_register(r, 'c', inc_u8(r, r.c)),
    ),
    0x0d: CPUInstruction(
        name='DEC C',
        length=1,
        cycles=4,
        opcode=0x0d,
        run=lambda r, m, o: set_register(r, 'c', dec_u8(r, r.c)),
    ),
    0x0e: CPUInstruction(
        name='LD C,u8',
        length=2,
        cycles=8,
        opcode=0x0e,
        run=lambda r, m, o: set_register(r, 'c', o.to_word()),
    ),
    0x0f: CPUInstruction(
        name='RRCA',
        length=1,
        cycles=4,
        opcode=0x0f,
        run=lambda r, m, o: set_register(r, 'a', rotate_right(r, r.a, reset_z_flag=True)),
    ),
    0x10: CPUInstruction(
        name='STOP',
        length=1,
        cycles=4,
        opcode=0x10
    ),
    0x11: CPUInstruction(
        name='LD DE,u16',
        length=3,
        cycles=12,
        opcode=0x11,
        run=lambda r, m, o: set_register(r, 'de', o.to_dword()),
    ),
    0x12: CPUInstruction(
        name='LD (DE),A',
        length=1,
        cycles=8,
        opcode=0x12,
        run=lambda r, m, o: m.write_u8(r.de, r.a),
    ),
    0x13: CPUInstruction(
        name='INC DE',
        length=1,
        cycles=8,
        opcode=0x13,
        run=lambda r, m, o: set_register(r, 'de', inc_u16(r.de)),
    ),
    0x14: CPUInstruction(
        name='INC D',
        length=1,
        cycles=4,
        opcode=0x14,
        run=lambda r, m, o: set_register(r, 'd', inc_u8(r, r.d)),
    ),
    0x15: CPUInstruction(
        name='DEC D',
        length=1,
        cycles=4,
        opcode=0x15,
        run=lambda r, m, o: set_register(r, 'd', dec_u8(r, r.d)),
    ),
    0x16: CPUInstruction(
        name='LD D,u8',
        length=2,
        cycles=8,
        opcode=0x16,
        run=lambda r, m, o: set_register(r, 'd', o.to_word()),
    ),
    0x17: CPUInstruction(
        name='RLA',
        length=1,
        cycles=4,
        opcode=0x17,
        run=lambda r, m, o: set_register(r, 'a', rotate_left(r, r.a, through_carry=True, reset_z_flag=True)),
    ),
    0x18: CPUInstruction(
        name='JR i8',
        length=2,
        cycles=12,
        opcode=0x18,
        run=lambda r, m, o: relative_jump(r, o.to_signed_word()),
    ),
    0x19: CPUInstruction(
        name='ADD HL,DE',
        length=1,
        cycles=8,
        opcode=0x19,
        run=lambda r, m, o: set_register(r, 'hl', add_u16(r, r.hl, r.de)),
    ),
    0x1a: CPUInstruction(
        name='LD A,(DE)',
        length=1,
        cycles=8,
        opcode=0x1a,
        run=lambda r, m, o: set_register(r, 'a', m.read(r.de)),
    ),
    0x1b: CPUInstruction(
        name='DEC DE',
        length=1,
        cycles=8,
        opcode=0x1b,
        run=lambda r, m, o: set_register(r, 'de', dec_u16(r.de)),
    ),
    0x1c: CPUInstruction(
        name='INC E',
        length=1,
        cycles=4,
        opcode=0x1c,
        run=lambda r, m, o: set_register(r, 'e', inc_u8(r, r.e)),
    ),
    0x1d: CPUInstruction(
        name='DEC E',
        length=1,
        cycles=4,
        opcode=0x1d,
        run=lambda r, m, o: set_register(r, 'e', dec_u8(r, r.e)),
    ),
    0x1e: CPUInstruction(
        name='LD E,u8',
        length=2,
        cycles=8,
        opcode=0x1e,
        run=lambda r, m, o: set_register(r, 'e', o.to_word()),
    ),
    0x1f: CPUInstruction(
        name='RRA',
        length=1,
        cycles=4,
        opcode=0x1f,
        run=lambda r, m, o: set_register(r, 'a', rotate_right(r, r.a, through_carry=True, reset_z_flag=True)),
    ),
    0x20: CPUInstruction(
        name='JR NZ,i8',
        length=2,
        cycles=8,
        opcode=0x20,
        run=lambda r, m, o: relative_jump(r, o.to_signed_word(), condition=not r.z_flag),
    ),
    0x21: CPUInstruction(
        name='LD HL,u16',
        length=3,
        cycles=12,
        opcode=0x21,
        run=lambda r, m, o: set_register(r, 'hl', o.to_dword()),
    ),
    0x22: CPUInstruction(
        name='LD (HL+),A',
        length=1,
        cycles=8,
        opcode=0x22,
        run=lambda r, m, o: write_mem_inc_hl(r, m, r.a),
    ),
    0x23: CPUInstruction(
        name='INC HL',
        length=1,
        cycles=8,
        opcode=0x23,
        run=lambda r, m, o: set_register(r, 'hl', inc_u16(r.hl)),
    ),
    0x24: CPUInstruction(
        name='INC H',
        length=1,
        cycles=4,
        opcode=0x24,
        run=lambda r, m, o: set_register(r, 'h', inc_u8(r, r.h)),
    ),
    0x25: CPUInstruction(
        name='DEC H',
        length=1,
        cycles=4,
        opcode=0x25,
        run=lambda r, m, o: set_register(r, 'h', dec_u8(r, r.h)),
    ),
    0x26: CPUInstruction(
        name='LD H,u8',
        length=2,
        cycles=8,
        opcode=0x26,
        run=lambda r, m, o: set_register(r, 'h', o.to_word()),
    ),
    0x27: CPUInstruction(
        name='DAA',
        length=1,
        cycles=4,
        opcode=0x27,
        run=lambda r, m, o: daa(r),
    ),
    0x28: CPUInstruction(
        name='JR Z,i8',
        length=2,
        cycles=8,
        opcode=0x28,
        run=lambda r, m, o: relative_jump(r, o.to_signed_word(), condition=r.z_flag),
    ),
    0x29: CPUInstruction(
        name='ADD HL,HL',
        length=1,
        cycles=8,
        opcode=0x29,
        run=lambda r, m, o: set_register(r, 'hl', add_u16(r, r.hl, r.hl)),
    ),
    0x2a: CPUInstruction(
        name='LD A,(HL+)',
        length=1,
        cycles=8,
        opcode=0x2a,
        run=lambda r, m, o: set_register(r, 'a', read_mem_inc_hl(r, m)),
    ),
    0x2b: CPUInstruction(
        name='DEC HL',
        length=1,
        cycles=8,
        opcode=0x2b,
        run=lambda r, m, o: set_register(r, 'hl', dec_u16(r.hl)),
    ),
    0x2c: CPUInstruction(
        name='INC L',
        length=1,
        cycles=4,
        opcode=0x2c,
        run=lambda r, m, o: set_register(r, 'l', inc_u8(r, r.l)),
    ),
    0x2d: CPUInstruction(
        name='DEC L',
        length=1,
        cycles=4,
        opcode=0x2d,
        run=lambda r, m, o: set_register(r, 'l', dec_u8(r, r.l)),
    ),
    0x2e: CPUInstruction(
        name='LD L,u8',
        length=2,
        cycles=8,
        opcode=0x2e,
        run=lambda r, m, o: set_register(r, 'l', o.to_word()),
    ),
    0x2f: CPUInstruction(
        name='CPL',
        length=1,
        cycles=4,
        opcode=0x2f,
        run=lambda r, m, o: complement(r),
    ),
    0x30: CPUInstruction(
        name='JR NC,i8',
        length=2,
        cycles=8,
        opcode=0x30,
        run=lambda r, m, o: relative_jump(r, o.to_signed_word(), condition=not r.c_flag),
    ),
    0x31: CPUInstruction(
        name='LD SP,u16',
        length=3,
        cycles=12,
        opcode=0x31,
        run=lambda r, m, o: set_register(r, 'sp', o.to_dword()),
    ),
    0x32: CPUInstruction(
        name='LD (HL-),A',
        length=1,
        cycles=8,
        opcode=0x32,
        run=lambda r, m, o: write_mem_dec_hl(r, m, r.a),
    ),
    0x33: CPUInstruction(
        name='INC SP',
        length=1,
        cycles=8,
        opcode=0x33,
        run=lambda r, m, o: set_register(r, 'sp', inc_u16(r.sp)),
    ),
    0x34: CPUInstruction(
        name='INC (HL)',
        length=1,
        cycles=12,
        opcode=0x34,
        run=lambda r, m, o: m.write_u8(r.hl, inc_u8(r, m.read(r.hl))),
    ),
    0x35: CPUInstruction(
        name='DEC (HL)',
        length=1,
        cycles=12,
        opcode=0x35,
        run=lambda r, m, o: m.write_u8(r.hl, dec_u8(r, m.read(r.hl))),
    ),
    0x36: CPUInstruction(
        name='LD (HL),u8',
        length=2,
        cycles=12,
        opcode=0x36,
        run=lambda r, m, o: m.write_u8(r.hl, o.to_word()),
    ),
    0x37: CPUInstruction(
        name='SCF',
        length=1,
        cycles=4,
        opcode=0x37,
        run=lambda r, m, o: set_carry_flag(r),
    ),
    0x38: CPUInstruction(
        name='JR C,i8',
        length=2,
        cycles=8,
        opcode=0x38,
        run=lambda r, m, o: relative_jump(r, o.to_signed_word(), condition=r.c_flag),
    ),
    0x39: CPUInstruction(
        name='ADD HL,SP',
        length=1,
        cycles=8,
        opcode=0x39,
        run=lambda r, m, o: set_register(r, 'hl', add_u16(r, r.hl, r.sp)),
    ),
    0x3a: CPUInstruction(
        name='LD A,(HL-)',
        length=1,
        cycles=8,
        opcode=0x3a,
        run=lambda r, m, o: set_register(r, 'a', read_mem_dec_hl(r, m)),
    ),
    0x3b: CPUInstruction(
        name='DEC SP',
        length=1,
        cycles=8,
        opcode=0x3b,
        run=lambda r, m, o: set_register(r, 'sp', dec_u16(r.sp)),
    ),
    0x3c: CPUInstruction(
        name='INC A',
        length=1,
        cycles=4,
        opcode=0x3c,
        run=lambda r, m, o: set_register(r, 'a', inc_u8(r, r.a)),
    ),
    0x3d: CPUInstruction(
        name='DEC A',
        length=1,
        cycles=4,
        opcode=0x3d,
        run=lambda r, m, o: set_register(r, 'a', dec_u8(r, r.a)),
    ),
    0x3e: CPUInstruction(
        name='LD A,u8',
        length=2,
        cycles=8,
        opcode=0x3e,
        run=lambda r, m, o: set_register(r, 'a', o.to_word()),
    ),
    0x3f: CPUInstruction(
        name='CCF',
        length=1,
        cycles=4,
        opcode=0x3f,
        run=lambda r, m, o: complement_carry_flag(r),
    ),
    0x40: CPUInstruction(
        name='LD B,B',
        length=1,
        cycles=4,
        opcode=0x40,
        run=lambda r, m, o: set_register(r, 'b', r.b),
    ),
    0x41: CPUInstruction(
        name='LD B,C',
        length=1,
        cycles=4,
        opcode=0x41,
        run=lambda r, m, o: set_register(r, 'b', r.c),
    ),
    0x42: CPUInstruction(
        name='LD B,D',
        length=1,
        cycles=4,
        opcode=0x42,
        run=lambda r, m, o: set_register(r, 'b', r.d),
    ),
    0x43: CPUInstruction(
        name='LD B,E',
        length=1,
        cycles=4,
        opcode=0x43,
        run=lambda r, m, o: set_register(r, 'b', r.e),
    ),
    0x44: CPUInstruction(
        name='LD B,H',
        length=1,
        cycles=4,
        opcode=0x44,
        run=lambda r, m, o: set_register(r, 'b', r.h),
    ),
    0x45: CPUInstruction(
        name='LD B,L',
        length=1,
        cycles=4,
        opcode=0x45,
        run=lambda r, m, o: set_register(r, 'b', r.l),
    ),
    0x46: CPUInstruction(
        name='LD B,(HL)',
        length=1,
        cycles=8,
        opcode=0x46,
        run=lambda r, m, o: set_register(r, 'b', m.read(r.hl)),
    ),
    0x47: CPUInstruction(
        name='LD B,A',
        length=1,
        cycles=4,
        opcode=0x47,
        run=lambda r, m, o: set_register(r, 'b', r.a),
    ),
    0x48: CPUInstruction(
        name='LD C,B',
        length=1,
        cycles=4,
        opcode=0x48,
        run=lambda r, m, o: set_register(r, 'c', r.b),
    ),
    0x49: CPUInstruction(
        name='LD C,C',
        length=1,
        cycles=4,
        opcode=0x49,
        run=lambda r, m, o: set_register(r, 'c', r.c),
    ),
    0x4a: CPUInstruction(
        name='LD C,D',
        length=1,
        cycles=4,
        opcode=0x4a,
        run=lambda r, m, o: set_register(r, 'c', r.d),
    ),
    0x4b: CPUInstruction(
        name='LD C,E',
        length=1,
        cycles=4,
        opcode=0x4b,
        run=lambda r, m, o: set_register(r, 'c', r.e),
    ),
    0x4c: CPUInstruction(
        name='LD C,H',
        length=1,
        cycles=4,
        opcode=0x4c,
        run=lambda r, m, o: set_register(r, 'c', r.h),
    ),
    0x4d: CPUInstruction(
        name='LD C,L',
        length=1,
        cycles=4,
        opcode=0x4d,
        run=lambda r, m, o: set_register(r, 'c', r.l),
    ),
    0x4e: CPUInstruction(
        name='LD C,(HL)',
        length=1,
        cycles=8,
        opcode=0x4e,
        run=lambda r, m, o: set_register(r, 'c', m.read(r.hl)),
    ),
    0x4f: CPUInstruction(
        name='LD C,A',
        length=1,
        cycles=4,
        opcode=0x4f,
        run=lambda r, m, o: set_register(r, 'c', r.a),
    ),
    0x50: CPUInstruction(
        name='LD D,B',
        length=1,
        cycles=4,
        opcode=0x50,
        run=lambda r, m, o: set_register(r, 'd', r.b),
    ),
    0x51: CPUInstruction(
        name='LD D,C',
        length=1,
        cycles=4,
        opcode=0x51,
        run=lambda r, m, o: set_register(r, 'd', r.c),
    ),
    0x52: CPUInstruction(
        name='LD D,D',
        length=1,
        cycles=4,
        opcode=0x52,
        run=lambda r, m, o: set_register(r, 'd', r.d),
    ),
    0x53: CPUInstruction(
        name='LD D,E',
        length=1,
        cycles=4,
        opcode=0x53,
        run=lambda r, m, o: set_register(r, 'd', r.e),
    ),
    0x54: CPUInstruction(
        name='LD D,H',
        length=1,
        cycles=4,
        opcode=0x54,
        run=lambda r, m, o: set_register(r, 'd', r.h),
    ),
    0x55: CPUInstruction(
        name='LD D,L',
        length=1,
        cycles=4,
        opcode=0x55,
        run=lambda r, m, o: set_register(r, 'd', r.l),
    ),
    0x56: CPUInstruction(
        name='LD D,(HL)',
        length=1,
        cycles=8,
        opcode=0x56,
        run=lambda r, m, o: set_register(r, 'd', m.read(r.hl)),
    ),
    0x57: CPUInstruction(
        name='LD D,A',
        length=1,
        cycles=4,
        opcode=0x57,
        run=lambda r, m, o: set_register(r, 'd', r.a),
    ),
    0x58: CPUInstruction(
        name='LD E,B',
        length=1,
        cycles=4,
        opcode=0x58,
        run=lambda r, m, o: set_register(r, 'e', r.b),
    ),
    0x59: CPUInstruction(
        name='LD E,C',
        length=1,
        cycles=4,
        opcode=0x59,
        run=lambda r, m, o: set_register(r, 'e', r.c),
    ),
    0x5a: CPUInstruction(
        name='LD E,D',
        length=1,
        cycles=4,
        opcode=0x5a,
        run=lambda r, m, o: set_register(r, 'e', r.d),
    ),
    0x5b: CPUInstruction(
        name='LD E,E',
        length=1,
        cycles=4,
        opcode=0x5b,
        run=lambda r, m, o: set_register(r, 'e', r.e),
    ),
    0x5c: CPUInstruction(
        name='LD E,H',
        length=1,
        cycles=4,
        opcode=0x5c,
        run=lambda r, m, o: set_register(r, 'e', r.h),
    ),
    0x5d: CPUInstruction(
        name='LD E,L',
        length=1,
        cycles=4,
        opcode=0x5d,
        run=lambda r, m, o: set_register(r, 'e', r.l),
    ),
    0x5e: CPUInstruction(
        name='LD E,(HL)',
        length=1,
        cycles=8,
        opcode=0x5e,
        run=lambda r, m, o: set_register(r, 'e', m.read(r.hl)),
    ),
    0x5f: CPUInstruction(
        name='LD E,A',
        length=1,
        cycles=4,
        opcode=0x5f,
        run=lambda r, m, o: set_register(r, 'e', r.a),
    ),
    0x60: CPUInstruction(
        name='LD H,B',
        length=1,
        cycles=4,
        opcode=0x60,
        run=lambda r, m, o: set_register(r, 'h', r.b),
    ),
    0x61: CPUInstruction(
        name='LD H,C',
        length=1,
        cycles=4,
        opcode=0x61,
        run=lambda r, m, o: set_register(r, 'h', r.c),
    ),
    0x62: CPUInstruction(
        name='LD H,D',
        length=1,
        cycles=4,
        opcode=0x62,
        run=lambda r, m, o: set_register(r, 'h', r.d),
    ),
    0x63: CPUInstruction(
        name='LD H,E',
        length=1,
        cycles=4,
        opcode=0x63,
        run=lambda r, m, o: set_register(r, 'h', r.e),
    ),
    0x64: CPUInstruction(
        name='LD H,H',
        length=1,
        cycles=4,
        opcode=0x64,
        run=lambda r, m, o: set_register(r, 'h', r.h),
    ),
    0x65: CPUInstruction(
        name='LD H,L',
        length=1,
        cycles=4,
        opcode=0x65,
        run=lambda r, m, o: set_register(r, 'h', r.l),
    ),
    0x66: CPUInstruction(
        name='LD H,(HL)',
        length=1,
        cycles=8,
        opcode=0x66,
        run=lambda r, m, o: set_register(r, 'h', m.read(r.hl)),
    ),
    0x67: CPUInstruction(
        name='LD H,A',
        length=1,
        cycles=4,
        opcode=0x67,
        run=lambda r, m, o: set_register(r, 'h', r.a),
    ),
    0x68: CPUInstruction(
        name='LD L,B',
        length=1,
        cycles=4,
        opcode=0x68,
        run=lambda r, m, o: set_register(r, 'l', r.b),
    ),
    0x69: CPUInstruction(
        name='LD L,C',
        length=1,
        cycles=4,
        opcode=0x69,
        run=lambda r, m, o: set_register(r, 'l', r.c),
    ),
    0x6a: CPUInstruction(
        name='LD L,D',
        length=1,
        cycles=4,
        opcode=0x6a,
        run=lambda r, m, o: set_register(r, 'l', r.d),
    ),
    0x6b: CPUInstruction(
        name='LD L,E',
        length=1,
        cycles=4,
        opcode=0x6b,
        run=lambda r, m, o: set_register(r, 'l', r.e),
    ),
    0x6c: CPUInstruction(
        name='LD L,H',
        length=1,
        cycles=4,
        opcode=0x6c,
        run=lambda r, m, o: set_register(r, 'l', r.h),
    ),
    0x6d: CPUInstruction(
        name='LD L,L',
        length=1,
        cycles=4,
        opcode=0x6d,
        run=lambda r, m, o: set_register(r, 'l', r.l),
    ),
    0x6e: CPUInstruction(
        name='LD L,(HL)',
        length=1,
        cycles=8,
        opcode=0x6e,
        run=lambda r, m, o: set_register(r, 'l', m.read(r.hl)),
    ),
    0x6f: CPUInstruction(
        name='LD L,A',
        length=1,
        cycles=4,
        opcode=0x6f,
        run=lambda r, m, o: set_register(r, 'l', r.a),
    ),
    0x70: CPUInstruction(
        name='LD (HL),B',
        length=1,
        cycles=8,
        opcode=0x70,
        run=lambda r, m, o: m.write_u8(r.hl, r.b),
    ),
    0x71: CPUInstruction(
        name='LD (HL),C',
        length=1,
        cycles=8,
        opcode=0x71,
        run=lambda r, m, o: m.write_u8(r.hl, r.c),
    ),
    0x72: CPUInstruction(
        name='LD (HL),D',
        length=1,
        cycles=8,
        opcode=0x72,
        run=lambda r, m, o: m.write_u8(r.hl, r.d),
    ),
    0x73: CPUInstruction(
        name='LD (HL),E',
        length=1,
        cycles=8,
        opcode=0x73,
        run=lambda r, m, o: m.write_u8(r.hl, r.e),
    ),
    0x74: CPUInstruction(
        name='LD (HL),H',
        length=1,
        cycles=8,
        opcode=0x74,
        run=lambda r, m, o: m.write_u8(r.hl, r.h),
    ),
    0x75: CPUInstruction(
        name='LD (HL),L',
        length=1,
        cycles=8,
        opcode=0x75,
        run=lambda r, m, o: m.write_u8(r.hl, r.l),
    ),
    0x76: CPUInstruction(
        name='HALT',
        length=1,
        cycles=4,
        opcode=0x76
    ),
    0x77: CPUInstruction(
        name='LD (HL),A',
        length=1,
        cycles=8,
        opcode=0x77,
        run=lambda r, m, o: m.write_u8(r.hl, r.a),
    ),
    0x78: CPUInstruction(
        name='LD A,B',
        length=1,
        cycles=4,
        opcode=0x78,
        run=lambda r, m, o: set_register(r, 'a', r.b),
    ),
    0x79: CPUInstruction(
        name='LD A,C',
        length=1,
        cycles=4,
        opcode=0x79,
        run=lambda r, m, o: set_register(r, 'a', r.c),
    ),
    0x7a: CPUInstruction(
        name='LD A,D',
        length=1,
        cycles=4,
        opcode=0x7a,
        run=lambda r, m, o: set_register(r, 'a', r.d),
    ),
    0x7b: CPUInstruction(
        name='LD A,E',
        length=1,
        cycles=4,
        opcode=0x7b,
        run=lambda r, m, o: set_register(r, 'a', r.e),
    ),
    0x7c: CPUInstruction(
        name='LD A,H',
        length=1,
        cycles=4,
        opcode=0x7c,
        run=lambda r, m, o: set_register(r, 'a', r.h),
    ),
    0x7d: CPUInstruction(
        name='LD A,L',
        length=1,
        cycles=4,
        opcode=0x7d,
        run=lambda r, m, o: set_register(r, 'a', r.l),
    ),
    0x7e: CPUInstruction(
        name='LD A,(HL)',
        length=1,
        cycles=8,
        opcode=0x7e,
        run=lambda r, m, o: set_register(r, 'a', m.read(r.hl)),
    ),
    0x7f: CPUInstruction(
        name='LD A,A',
        length=1,
        cycles=4,
        opcode=0x7f,
        run=lambda r, m, o: set_register(r, 'a', r.a),
    ),
    0x80: CPUInstruction(
        name='ADD A,B',
        length=1,
        cycles=4,
        opcode=0x80,
        run=lambda r, m, o: set_register(r, 'a', add_u8(r, r.a, r.b)),
    ),
    0x81: CPUInstruction(
        name='ADD A,C',
        length=1,
        cycles=4,
        opcode=0x81,
        run=lambda r, m, o: set_register(r, 'a', add_u8(r, r.a, r.c)),
    ),
    0x82: CPUInstruction(
        name='ADD A,D',
        length=1,
        cycles=4,
        opcode=0x82,
        run=lambda r, m, o: set_register(r, 'a', add_u8(r, r.a, r.d)),
    ),
    0x83: CPUInstruction(
        name='ADD A,E',
        length=1,
        cycles=4,
        opcode=0x83,
        run=lambda r, m, o: set_register(r, 'a', add_u8(r, r.a, r.e)),
    ),
    0x84: CPUInstruction(
        name='ADD A,H',
        length=1,
        cycles=4,
        opcode=0x84,
        run=lambda r, m, o: set_register(r, 'a', add_u8(r, r.a, r.h)),
    ),
    0x85: CPUInstruction(
        name='ADD A,L',
        length=1,
        cycles=4,
        opcode=0x85,
        run=lambda r, m, o: set_register(r, 'a', add_u8(r, r.a, r.l)),
    ),
    0x86: CPUInstruction(
        name='ADD A,(HL)',
        length=1,
        cycles=8,
        opcode=0x86,
        run=lambda r, m, o: set_register(r, 'a', add_u8(r, r.a, m.read(r.hl))),
    ),
    0x87: CPUInstruction(
        name='ADD A,A',
        length=1,
        cycles=4,
        opcode=0x87,
        run=lambda r, m, o: set_register(r, 'a', add_u8(r, r.a, r.a)),
    ),
    0x88: CPUInstruction(
        name='ADC A,B',
        length=1,
        cycles=4,
        opcode=0x88,
        run=lambda r, m, o: set_register(r, 'a', add_u8_with_carry(r, r.a, r.b)),
    ),
    0x89: CPUInstruction(
        name='ADC A,C',
        length=1,
        cycles=4,
        opcode=0x89,
        run=lambda r, m, o: set_register(r, 'a', add_u8_with_carry(r, r.a, r.c)),
    ),
    0x8a: CPUInstruction(
        name='ADC A,D',
        length=1,
        cycles=4,
        opcode=0x8a,
        run=lambda r, m, o: set_register(r, 'a', add_u8_with_carry(r, r.a, r.d)),
    ),
    0x8b: CPUInstruction(
        name='ADC A,E',
        length=1,
        cycles=4,
        opcode=0x8b,
        run=lambda r, m, o: set_register(r, 'a', add_u8_with_carry(r, r.a, r.e)),
    ),
    0x8c: CPUInstruction(
        name='ADC A,H',
        length=1,
        cycles=4,
        opcode=0x8c,
        run=lambda r, m, o: set_register(r, 'a', add_u8_with_carry(r, r.a, r.h)),
    ),
    0x8d: CPUInstruction(
        name='ADC A,L',
        length=1,
        cycles=4,
        opcode=0x8d,
        run=lambda r, m, o: set_register(r, 'a', add_u8_with_carry(r, r.a, r.l)),
    ),
    0x8e: CPUInstruction(
        name='ADC A,(HL)',
        length=1,
        cycles=8,
        opcode=0x8e,
        run=lambda r, m, o: set_register(r, 'a', add_u8_with_carry(r, r.a, m.read(r.hl))),
    ),
    0x8f: CPUInstruction(
        name='ADC A,A',
        length=1,
        cycles=4,
        opcode=0x8f,
        run=lambda r, m, o: set_register(r, 'a', add_u8_with_carry(r, r.a, r.a)),
    ),
    0x90: CPUInstruction(
        name='SUB A,B',
        length=1,
        cycles=4,
        opcode=0x90,
        run=lambda r, m, o: set_register(r, 'a', subtract_u8(r, r.a, r.b)),
    ),
    0x91: CPUInstruction(
        name='SUB A,C',
        length=1,
        cycles=4,
        opcode=0x91,
        run=lambda r, m, o: set_register(r, 'a', subtract_u8(r, r.a, r.c)),
    ),
    0x92: CPUInstruction(
        name='SUB A,D',
        length=1,
        cycles=4,
        opcode=0x92,
        run=lambda r, m, o: set_register(r, 'a', subtract_u8(r, r.a, r.d)),
    ),
    0x93: CPUInstruction(
        name='SUB A,E',
        length=1,
        cycles=4,
        opcode=0x93,
        run=lambda r, m, o: set_register(r, 'a', subtract_u8(r, r.a, r.e)),
    ),
    0x94: CPUInstruction(
        name='SUB A,H',
        length=1,
        cycles=4,
        opcode=0x94,
        run=lambda r, m, o: set_register(r, 'a', subtract_u8(r, r.a, r.h)),
    ),
    0x95: CPUInstruction(
        name='SUB A,L',
        length=1,
        cycles=4,
        opcode=0x95,
        run=lambda r, m, o: set_register(r, 'a', subtract_u8(r, r.a, r.l)),
    ),
    0x96: CPUInstruction(
        name='SUB A,(HL)',
        length=1,
        cycles=8,
        opcode=0x96,
        run=lambda r, m, o: set_register(r, 'a', subtract_u8(r, r.a, m.read(r.hl))),
    ),
    0x97: CPUInstruction(
        name='SUB A,A',
        length=1,
        cycles=4,
        opcode=0x97,
        run=lambda r, m, o: set_register(r, 'a', subtract_u8(r, r.a, r.a)),
    ),
    0x98: CPUInstruction(
        name='SBC A,B',
        length=1,
        cycles=4,
        opcode=0x98,
        run=lambda r, m, o: set_register(r, 'a', subtract_u8_with_carry(r, r.a, r.b)),
    ),
    0x99: CPUInstruction(
        name='SBC A,C',
        length=1,
        cycles=4,
        opcode=0x99,
        run=lambda r, m, o: set_register(r, 'a', subtract_u8_with_carry(r, r.a, r.c)),
    ),
    0x9a: CPUInstruction(
        name='SBC A,D',
        length=1,
        cycles=4,
        opcode=0x9a,
        run=lambda r, m, o: set_register(r, 'a', subtract_u8_with_carry(r, r.a, r.d)),
    ),
    0x9b: CPUInstruction(
        name='SBC A,E',
        length=1,
        cycles=4,
        opcode=0x9b,
        run=lambda r, m, o: set_register(r, 'a', subtract_u8_with_carry(r, r.a, r.e)),
    ),
    0x9c: CPUInstruction(
        name='SBC A,H',
        length=1,
        cycles=4,
        opcode=0x9c,
        run=lambda r, m, o: set_register(r, 'a', subtract_u8_with_carry(r, r.a, r.h)),
    ),
    0x9d: CPUInstruction(
        name='SBC A,L',
        length=1,
        cycles=4,
        opcode=0x9d,
        run=lambda r, m, o: set_register(r, 'a', subtract_u8_with_carry(r, r.a, r.l)),
    ),
    0x9e: CPUInstruction(
        name='SBC A,(HL)',
        length=1,
        cycles=8,
        opcode=0x9e,
        run=lambda r, m, o: set_register(r, 'a', subtract_u8_with_carry(r, r.a, m.read(r.hl))),
    ),
    0x9f: CPUInstruction(
        name='SBC A,A',
        length=1,
        cycles=4,
        opcode=0x9f,
        run=lambda r, m, o: set_register(r, 'a', subtract_u8_with_carry(r, r.a, r.a)),
    ),
    0xa0: CPUInstruction(
        name='AND A,B',
        length=1,
        cycles=4,
        opcode=0xa0,
        run=lambda r, m, o: logical_and(r, r.a, r.b),
    ),
    0xa1: CPUInstruction(
        name='AND A,C',
        length=1,
        cycles=4,
        opcode=0xa1,
        run=lambda r, m, o: logical_and(r, r.a, r.c),
    ),
    0xa2: CPUInstruction(
        name='AND A,D',
        length=1,
        cycles=4,
        opcode=0xa2,
        run=lambda r, m, o: logical_and(r, r.a, r.d),
    ),
    0xa3: CPUInstruction(
        name='AND A,E',
        length=1,
        cycles=4,
        opcode=0xa3,
        run=lambda r, m, o: logical_and(r, r.a, r.e),
    ),
    0xa4: CPUInstruction(
        name='AND A,H',
        length=1,
        cycles=4,
        opcode=0xa4,
        run=lambda r, m, o: logical_and(r, r.a, r.h),
    ),
    0xa5: CPUInstruction(
        name='AND A,L',
        length=1,
        cycles=4,
        opcode=0xa5,
        run=lambda r, m, o: logical_and(r, r.a, r.l),
    ),
    0xa6: CPUInstruction(
        name='AND A,(HL)',
        length=1,
        cycles=8,
        opcode=0xa6,
        run=lambda r, m, o: logical_and(r, r.a, m.read(r.hl)),
    ),
    0xa7: CPUInstruction(
        name='AND A,A',
        length=1,
        cycles=4,
        opcode=0xa7,
        run=lambda r, m, o: logical_and(r, r.a, r.a),
    ),
    0xa8: CPUInstruction(
        name='XOR A,B',
        length=1,
        cycles=4,
        opcode=0xa8,
        run=lambda r, m, o: xor(r, r.a, r.b),
    ),
    0xa9: CPUInstruction(
        name='XOR A,C',
        length=1,
        cycles=4,
        opcode=0xa9,
        run=lambda r, m, o: xor(r, r.a, r.c),
    ),
    0xaa: CPUInstruction(
        name='XOR A,D',
        length=1,
        cycles=4,
        opcode=0xaa,
        run=lambda r, m, o: xor(r, r.a, r.d),
    ),
    0xab: CPUInstruction(
        name='XOR A,E',
        length=1,
        cycles=4,
        opcode=0xab,
        run=lambda r, m, o: xor(r, r.a, r.e),
    ),
    0xac: CPUInstruction(
        name='XOR A,H',
        length=1,
        cycles=4,
        opcode=0xac,
        run=lambda r, m, o: xor(r, r.a, r.h),
    ),
    0xad: CPUInstruction(
        name='XOR A,L',
        length=1,
        cycles=4,
        opcode=0xad,
        run=lambda r, m, o: xor(r, r.a, r.l),
    ),
    0xae: CPUInstruction(
        name='XOR A,(HL)',
        length=1,
        cycles=8,
        opcode=0xae,
        run=lambda r, m, o: xor(r, r.a, m.read(r.hl)),
    ),
    0xaf: CPUInstruction(
        name='XOR A,A',
        length=1,
        cycles=4,
        opcode=0xaf,
        run=lambda r, m, o: xor(r, r.a, r.a),
    ),
    0xb0: CPUInstruction(
        name='OR A,B',
        length=1,
        cycles=4,
        opcode=0xb0,
        run=lambda r, m, o: logical_or(r, r.a, r.b),
    ),
    0xb1: CPUInstruction(
        name='OR A,C',
        length=1,
        cycles=4,
        opcode=0xb1,
        run=lambda r, m, o: logical_or(r, r.a, r.c),
    ),
    0xb2: CPUInstruction(
        name='OR A,D',
        length=1,
        cycles=4,
        opcode=0xb2,
        run=lambda r, m, o: logical_or(r, r.a, r.d),
    ),
    0xb3: CPUInstruction(
        name='OR A,E',
        length=1,
        cycles=4,
        opcode=0xb3,
        run=lambda r, m, o: logical_or(r, r.a, r.e),
    ),
    0xb4: CPUInstruction(
        name='OR A,H',
        length=1,
        cycles=4,
        opcode=0xb4,
        run=lambda r, m, o: logical_or(r, r.a, r.h),
    ),
    0xb5: CPUInstruction(
        name='OR A,L',
        length=1,
        cycles=4,
        opcode=0xb5,
        run=lambda r, m, o: logical_or(r, r.a, r.l),
    ),
    0xb6: CPUInstruction(
        name='OR A,(HL)',
        length=1,
        cycles=8,
        opcode=0xb6,
        run=lambda r, m, o: logical_or(r, r.a, m.read(r.hl)),
    ),
    0xb7: CPUInstruction(
        name='OR A,A',
        length=1,
        cycles=4,
        opcode=0xb7,
        run=lambda r, m, o: logical_or(r, r.a, r.a),
    ),
    0xb8: CPUInstruction(
        name='CP A,B',
        length=1,
        cycles=4,
        opcode=0xb8,
        run=lambda r, m, o: compare(r, r.b),
    ),
    0xb9: CPUInstruction(
        name='CP A,C',
        length=1,
        cycles=4,
        opcode=0xb9,
        run=lambda r, m, o: compare(r, r.c),
    ),
    0xba: CPUInstruction(
        name='CP A,D',
        length=1,
        cycles=4,
        opcode=0xba,
        run=lambda r, m, o: compare(r, r.d),
),
    0xbb: CPUInstruction(
        name='CP A,E',
        length=1,
        cycles=4,
        opcode=0xbb,
        run=lambda r, m, o: compare(r, r.e),
    ),
    0xbc: CPUInstruction(
        name='CP A,H',
        length=1,
        cycles=4,
        opcode=0xbc,
        run=lambda r, m, o: compare(r, r.h),
    ),
    0xbd: CPUInstruction(
        name='CP A,L',
        length=1,
        cycles=4,
        opcode=0xbd,
        run=lambda r, m, o: compare(r, r.l),
    ),
    0xbe: CPUInstruction(
        name='CP A,(HL)',
        length=1,
        cycles=8,
        opcode=0xbe,
        run=lambda r, m, o: compare(r, m.read(r.hl)),
    ),
    0xbf: CPUInstruction(
        name='CP A,A',
        length=1,
        cycles=4,
        opcode=0xbf,
        run=lambda r, m, o: compare(r, r.a),
    ),
    0xc0: CPUInstruction(
        name='RET NZ',
        length=1,
        cycles=8,
        opcode=0xc0,
        run=lambda r, m, o: ret(r, m, condition=not r.z_flag),
    ),
    0xc1: CPUInstruction(
        name='POP BC',
        length=1,
        cycles=12,
        opcode=0xc1,
        run=lambda r, m, o: set_register(r, 'bc', pop_stack(r, m)),
    ),
    0xc2: CPUInstruction(
        name='JP NZ,u16',
        length=3,
        cycles=12,
        opcode=0xc2,
        run=lambda r, m, o: jump(r, o.to_dword(), condition=not r.z_flag),
    ),
    0xc3: CPUInstruction(
        name='JP u16',
        length=3,
        cycles=16,
        opcode=0xc3,
        run=lambda r, m, o: set_register(r, 'pc', o.to_dword()),
    ),
    0xc4: CPUInstruction(
        name='CALL NZ,u16',
        length=3,
        cycles=12,
        opcode=0xc4,
        run=lambda r, m, o: call(r, m, o.to_dword(), condition=not r.z_flag),
    ),
    0xc5: CPUInstruction(
        name='PUSH BC',
        length=1,
        cycles=16,
        opcode=0xc5,
        run=lambda r, m, o: push_stack(r, m, r.bc),
    ),
    0xc6: CPUInstruction(
        name='ADD A,u8',
        length=2,
        cycles=8,
        opcode=0xc6,
        run=lambda r, m, o: set_register(r, 'a', add_u8(r, r.a, o.to_word())),
    ),
    0xc7: CPUInstruction(
        name='RST 00h',
        length=1,
        cycles=16,
        opcode=0xc7,
        run=lambda r, m, o: restart(r, m, u16(0x00)),
    ),
    0xc8: CPUInstruction(
        name='RET Z',
        length=1,
        cycles=8,
        opcode=0xc8,
        run=lambda r, m, o: ret(r, m, condition=r.z_flag),
    ),
    0xc9: CPUInstruction(
        name='RET',
        length=1,
        cycles=16,
        opcode=0xc9,
        run=lambda r, m, o: ret(r, m),
    ),
    0xca: CPUInstruction(
        name='JP Z,u16',
        length=3,
        cycles=12,
        opcode=0xca,
        run=lambda r, m, o: jump(r, o.to_dword(), condition=r.z_flag),
    ),
    0xcb: CPUInstruction(
        name='PREFIX CB',
        length=1,
        cycles=4,
        opcode=0xcb
    ),
    0xcc: CPUInstruction(
        name='CALL Z,u16',
        length=3,
        cycles=12,
        opcode=0xcc,
        run=lambda r, m, o: call(r, m, o.to_dword(), condition=r.z_flag),
    ),
    0xcd: CPUInstruction(
        name='CALL u16',
        length=3,
        cycles=24,
        opcode=0xcd,
        run=lambda r, m, o: call(r, m, o.to_dword()),
    ),
    0xce: CPUInstruction(
        name='ADC A,u8',
        length=2,
        cycles=8,
        opcode=0xce,
        run=lambda r, m, o: set_register(r, 'a', add_u8_with_carry(r, r.a, o.to_word()))
    ),
    0xcf: CPUInstruction(
        name='RST 08h',
        length=1,
        cycles=16,
        opcode=0xcf,
        run=lambda r, m, o: restart(r, m, u16(0x08)),
    ),
    0xd0: CPUInstruction(
        name='RET NC',
        length=1,
        cycles=8,
        opcode=0xd0,
        run=lambda r, m, o: ret(r, m, condition=not r.c_flag),
    ),
    0xd1: CPUInstruction(
        name='POP DE',
        length=1,
        cycles=12,
        opcode=0xd1,
        run=lambda r, m, o: set_register(r, 'de', pop_stack(r, m)),
    ),
    0xd2: CPUInstruction(
        name='JP NC,u16',
        length=3,
        cycles=12,
        opcode=0xd2,
        run=lambda r, m, o: jump(r, o.to_dword(), condition=not r.c_flag),
    ),
    0xd3: CPUInstruction(
        name='UNUSED',
        length=1,
        cycles=0,
        opcode=0xd3
    ),
    0xd4: CPUInstruction(
        name='CALL NC,u16',
        length=3,
        cycles=12,
        opcode=0xd4,
        run=lambda r, m, o: call(r, m, o.to_dword(), condition=not r.c_flag),
    ),
    0xd5: CPUInstruction(
        name='PUSH DE',
        length=1,
        cycles=16,
        opcode=0xd5,
        run=lambda r, m, o: push_stack(r, m, r.de),
    ),
    0xd6: CPUInstruction(
        name='SUB A,u8',
        length=2,
        cycles=8,
        opcode=0xd6,
        run=lambda r, m, o: set_register(r, 'a', subtract_u8(r, r.a, o.to_word())),
    ),
    0xd7: CPUInstruction(
        name='RST 10h',
        length=1,
        cycles=16,
        opcode=0xd7,
        run=lambda r, m, o: restart(r, m, u16(0x10)),
    ),
    0xd8: CPUInstruction(
        name='RET C',
        length=1,
        cycles=8,
        opcode=0xd8,
        run=lambda r, m, o: ret(r, m, condition=r.c_flag),
    ),
    0xd9: CPUInstruction(
        name='RETI',
        length=1,
        cycles=16,
        opcode=0xd9,
        run=lambda r, m, o: reti(r, m),
    ),
    0xda: CPUInstruction(
        name='JP C,u16',
        length=3,
        cycles=12,
        opcode=0xda,
        run=lambda r, m, o: jump(r, o.to_dword(), condition=r.c_flag),
    ),
    0xdb: CPUInstruction(
        name='UNUSED',
        length=1,
        cycles=0,
        opcode=0xdb
    ),
    0xdc: CPUInstruction(
        name='CALL C,u16',
        length=3,
        cycles=12,
        opcode=0xdc,
        run=lambda r, m, o: call(r, m, o.to_dword(), condition=r.c_flag),
    ),
    0xdd: CPUInstruction(
        name='UNUSED',
        length=1,
        cycles=0,
        opcode=0xdd
    ),
    0xde: CPUInstruction(
        name='SBC A,u8',
        length=2,
        cycles=8,
        opcode=0xde,
        run=lambda r, m, o: set_register(r, 'a', subtract_u8_with_carry(r, r.a, o.to_word())),
    ),
    0xdf: CPUInstruction(
        name='RST 18h',
        length=1,
        cycles=16,
        opcode=0xdf,
        run=lambda r, m, o: restart(r, m, u16(0x18)),
    ),
    0xe0: CPUInstruction(
        name='LD (FF00+u8),A',
        length=2,
        cycles=12,
        opcode=0xe0,
        run=lambda r, m, o: m.write_u8(u16(0xff00 + o.to_word()), r.a),
    ),
    0xe1: CPUInstruction(
        name='POP HL',
        length=1,
        cycles=12,
        opcode=0xe1,
        run=lambda r, m, o: set_register(r, 'hl', pop_stack(r, m)),
    ),
    0xe2: CPUInstruction(
        name='LD (FF00+C),A',
        length=1,
        cycles=8,
        opcode=0xe2,
        run=lambda r, m, o: m.write_u8(u16(0xff00 + r.c), r.a),
    ),
    0xe3: CPUInstruction(
        name='UNUSED',
        length=1,
        cycles=0,
        opcode=0xe3
    ),
    0xe4: CPUInstruction(
        name='UNUSED',
        length=1,
        cycles=0,
        opcode=0xe4
    ),
    0xe5: CPUInstruction(
        name='PUSH HL',
        length=1,
        cycles=16,
        opcode=0xe5,
        run=lambda r, m, o: push_stack(r, m, r.hl),
    ),
    0xe6: CPUInstruction(
        name='AND A,u8',
        length=2,
        cycles=8,
        opcode=0xe6,
        run=lambda r, m, o: logical_and(r, r.a, o.to_word()),
    ),
    0xe7: CPUInstruction(
        name='RST 20h',
        length=1,
        cycles=16,
        opcode=0xe7,
        run=lambda r, m, o: restart(r, m, u16(0x20)),
    ),
    0xe8: CPUInstruction(
        name='ADD SP,i8',
        length=2,
        cycles=16,
        opcode=0xe8,
        run=lambda r, m, o: set_register(r, 'sp', add_sp(r, o.to_signed_word())),
    ),
    0xe9: CPUInstruction(
        name='JP HL',
        length=1,
        cycles=4,
        opcode=0xe9,
        run=lambda r, m, o: set_register(r, 'pc', r.hl)
),
    0xea: CPUInstruction(
        name='LD (u16),A',
        length=3,
        cycles=16,
        opcode=0xea,
        run=lambda r, m, o: m.write_u8(o.to_dword(), r.a),
    ),
    0xeb: CPUInstruction(
        name='UNUSED',
        length=1,
        cycles=0,
        opcode=0xeb
    ),
    0xec: CPUInstruction(
        name='UNUSED',
        length=1,
        cycles=0,
        opcode=0xec
    ),
    0xed: CPUInstruction(
        name='UNUSED',
        length=1,
        cycles=0,
        opcode=0xed
    ),
    0xee: CPUInstruction(
        name='XOR A,u8',
        length=2,
        cycles=8,
        opcode=0xee,
        run=lambda r, m, o: xor(r, r.a, o.to_word()),
    ),
    0xef: CPUInstruction(
        name='RST 28h',
        length=1,
        cycles=16,
        opcode=0xef,
        run=lambda r, m, o: restart(r, m, u16(0x28)),
    ),
    0xf0: CPUInstruction(
        name='LD A,(FF00+u8)',
        length=2,
        cycles=12,
        opcode=0xf0,
        run=lambda r, m, o: set_register(r, 'a', m.read(u16(0xff00 + o.to_word()))),
    ),
    0xf1: CPUInstruction(
        name='POP AF',
        length=1,
        cycles=12,
        opcode=0xf1,
        run=lambda r, m, o: set_register(r, 'af', pop_stack(r, m) & 0xfff0),  # last 4 bits of F register are always 0
    ),
    0xf2: CPUInstruction(
        name='LD A,(FF00+C)',
        length=1,
        cycles=8,
        opcode=0xf2,
        run=lambda r, m, o: set_register(r, 'a', m.read(u16(0xff00 + r.c))),
    ),
    0xf3: CPUInstruction(
        name='DI',
        length=1,
        cycles=4,
        opcode=0xf3,
        run=lambda r, m, o: disable_interrupts(m),
    ),
    0xf4: CPUInstruction(
        name='UNUSED',
        length=1,
        cycles=0,
        opcode=0xf4
    ),
    0xf5: CPUInstruction(
        name='PUSH AF',
        length=1,
        cycles=16,
        opcode=0xf5,
        run=lambda r, m, o: push_stack(r, m, r.af),
    ),
    0xf6: CPUInstruction(
        name='OR A,u8',
        length=2,
        cycles=8,
        opcode=0xf6,
        run=lambda r, m, o: logical_or(r, r.a, o.to_word()),
    ),
    0xf7: CPUInstruction(
        name='RST 30h',
        length=1,
        cycles=16,
        opcode=0xf7,
        run=lambda r, m, o: restart(r, m, u16(0x30)),
    ),
    0xf8: CPUInstruction(
        name='LD HL,SP+i8',
        length=2,
        cycles=12,
        opcode=0xf8,
        run=lambda r, m, o: set_register(r, 'hl', add_sp(r, o.to_signed_word())),
    ),
    0xf9: CPUInstruction(
        name='LD SP,HL',
        length=1,
        cycles=8,
        opcode=0xf9,
        run=lambda r, m, o: set_register(r, 'sp', r.hl),
    ),
    0xfa: CPUInstruction(
        name='LD A,(u16)',
        length=3,
        cycles=16,
        opcode=0xfa,
        run=lambda r, m, o: set_register(r, 'a', m.read(o.to_dword())),
    ),
    0xfb: CPUInstruction(
        name='EI',
        length=1,
        cycles=4,
        opcode=0xfb,
        run=lambda r, m, o: enable_interrupts(m),
    ),
    0xfc: CPUInstruction(
        name='UNUSED',
        length=1,
        cycles=0,
        opcode=0xfc
    ),
    0xfd: CPUInstruction(
        name='UNUSED',
        length=1,
        cycles=0,
        opcode=0xfd
    ),
    0xfe: CPUInstruction(
        name='CP A,u8',
        length=2,
        cycles=8,
        opcode=0xfe,
        run=lambda r, m, o: compare(r, o.to_word()),
    ),
    0xff: CPUInstruction(
        name='RST 38h',
        length=1,
        cycles=16,
        opcode=0xff,
        run=lambda r, m, o: restart(r, m, u16(0x38)),
    ),
    0xcb00: CPUInstruction(
        name='RLC B',
        length=2,
        cycles=8,
        opcode=0xcb00,
        run=lambda r, m, o: set_register(r, 'b', rotate_left(r, r.b)),
    ),
    0xcb01: CPUInstruction(
        name='RLC C',
        length=2,
        cycles=8,
        opcode=0xcb01,
        run=lambda r, m, o: set_register(r, 'c', rotate_left(r, r.c)),
    ),
    0xcb02: CPUInstruction(
        name='RLC D',
        length=2,
        cycles=8,
        opcode=0xcb02,
        run=lambda r, m, o: set_register(r, 'd', rotate_left(r, r.d)),
    ),
    0xcb03: CPUInstruction(
        name='RLC E',
        length=2,
        cycles=8,
        opcode=0xcb03,
        run=lambda r, m, o: set_register(r, 'e', rotate_left(r, r.e)),
    ),
    0xcb04: CPUInstruction(
        name='RLC H',
        length=2,
        cycles=8,
        opcode=0xcb04,
        run=lambda r, m, o: set_register(r, 'h', rotate_left(r, r.h)),
    ),
    0xcb05: CPUInstruction(
        name='RLC L',
        length=2,
        cycles=8,
        opcode=0xcb05,
        run=lambda r, m, o: set_register(r, 'l', rotate_left(r, r.l)),
    ),
    0xcb06: CPUInstruction(
        name='RLC (HL)',
        length=2,
        cycles=16,
        opcode=0xcb06,
        run=lambda r, m, o: m.write_u8(r.hl, rotate_left(r, m.read(r.hl))),
    ),
    0xcb07: CPUInstruction(
        name='RLC A',
        length=2,
        cycles=8,
        opcode=0xcb07,
        run=lambda r, m, o: set_register(r, 'a', rotate_left(r, r.a)),
    ),
    0xcb08: CPUInstruction(
        name='RRC B',
        length=2,
        cycles=8,
        opcode=0xcb08,
        run=lambda r, m, o: set_register(r, 'b', rotate_right(r, r.b)),
    ),
    0xcb09: CPUInstruction(
        name='RRC C',
        length=2,
        cycles=8,
        opcode=0xcb09,
        run=lambda r, m, o: set_register(r, 'c', rotate_right(r, r.c)),
    ),
    0xcb0a: CPUInstruction(
        name='RRC D',
        length=2,
        cycles=8,
        opcode=0xcb0a,
        run=lambda r, m, o: set_register(r, 'd', rotate_right(r, r.d)),
    ),
    0xcb0b: CPUInstruction(
        name='RRC E',
        length=2,
        cycles=8,
        opcode=0xcb0b,
        run=lambda r, m, o: set_register(r, 'e', rotate_right(r, r.e)),
    ),
    0xcb0c: CPUInstruction(
        name='RRC H',
        length=2,
        cycles=8,
        opcode=0xcb0c,
        run=lambda r, m, o: set_register(r, 'h', rotate_right(r, r.h)),
    ),
    0xcb0d: CPUInstruction(
        name='RRC L',
        length=2,
        cycles=8,
        opcode=0xcb0d,
        run=lambda r, m, o: set_register(r, 'l', rotate_right(r, r.l)),
    ),
    0xcb0e: CPUInstruction(
        name='RRC (HL)',
        length=2,
        cycles=16,
        opcode=0xcb0e,
        run=lambda r, m, o: m.write_u8(r.hl, rotate_right(r, m.read(r.hl))),
    ),
    0xcb0f: CPUInstruction(
        name='RRC A',
        length=2,
        cycles=8,
        opcode=0xcb0f,
        run=lambda r, m, o: set_register(r, 'a', rotate_right(r, r.a)),
    ),
    0xcb10: CPUInstruction(
        name='RL B',
        length=2,
        cycles=8,
        opcode=0xcb10,
        run=lambda r, m, o: set_register(r, 'b', rotate_left(r, r.b, through_carry=True)),
    ),
    0xcb11: CPUInstruction(
        name='RL C',
        length=2,
        cycles=8,
        opcode=0xcb11,
        run=lambda r, m, o: set_register(r, 'c', rotate_left(r, r.c, through_carry=True))
    ),
    0xcb12: CPUInstruction(
        name='RL D',
        length=2,
        cycles=8,
        opcode=0xcb12,
        run=lambda r, m, o: set_register(r, 'd', rotate_left(r, r.d, through_carry=True)),
    ),
    0xcb13: CPUInstruction(
        name='RL E',
        length=2,
        cycles=8,
        opcode=0xcb13,
        run=lambda r, m, o: set_register(r, 'e', rotate_left(r, r.e, through_carry=True)),
    ),
    0xcb14: CPUInstruction(
        name='RL H',
        length=2,
        cycles=8,
        opcode=0xcb14,
        run=lambda r, m, o: set_register(r, 'h', rotate_left(r, r.h, through_carry=True)),
    ),
    0xcb15: CPUInstruction(
        name='RL L',
        length=2,
        cycles=8,
        opcode=0xcb15,
        run=lambda r, m, o: set_register(r, 'l', rotate_left(r, r.l, through_carry=True)),
    ),
    0xcb16: CPUInstruction(
        name='RL (HL)',
        length=2,
        cycles=16,
        opcode=0xcb16,
        run=lambda r, m, o: m.write_u8(r.hl, rotate_left(r, m.read(r.hl), through_carry=True)),
    ),
    0xcb17: CPUInstruction(
        name='RL A',
        length=2,
        cycles=8,
        opcode=0xcb17,
        run=lambda r, m, o: set_register(r, 'a', rotate_left(r, r.a, through_carry=True)),
    ),
    0xcb18: CPUInstruction(
        name='RR B',
        length=2,
        cycles=8,
        opcode=0xcb18,
        run=lambda r, m, o: set_register(r, 'b', rotate_right(r, r.b, through_carry=True)),
    ),
    0xcb19: CPUInstruction(
        name='RR C',
        length=2,
        cycles=8,
        opcode=0xcb19,
        run=lambda r, m, o: set_register(r, 'c', rotate_right(r, r.c, through_carry=True)),
    ),
    0xcb1a: CPUInstruction(
        name='RR D',
        length=2,
        cycles=8,
        opcode=0xcb1a,
        run=lambda r, m, o: set_register(r, 'd', rotate_right(r, r.d, through_carry=True)),
    ),
    0xcb1b: CPUInstruction(
        name='RR E',
        length=2,
        cycles=8,
        opcode=0xcb1b,
        run=lambda r, m, o: set_register(r, 'e', rotate_right(r, r.e, through_carry=True)),
    ),
    0xcb1c: CPUInstruction(
        name='RR H',
        length=2,
        cycles=8,
        opcode=0xcb1c,
        run=lambda r, m, o: set_register(r, 'h', rotate_right(r, r.h, through_carry=True)),
    ),
    0xcb1d: CPUInstruction(
        name='RR L',
        length=2,
        cycles=8,
        opcode=0xcb1d,
        run=lambda r, m, o: set_register(r, 'l', rotate_right(r, r.l, through_carry=True)),
    ),
    0xcb1e: CPUInstruction(
        name='RR (HL)',
        length=2,
        cycles=16,
        opcode=0xcb1e,
        run=lambda r, m, o: m.write_u8(r.hl, rotate_right(r, m.read(r.hl), through_carry=True)),
    ),
    0xcb1f: CPUInstruction(
        name='RR A',
        length=2,
        cycles=8,
        opcode=0xcb1f,
        run=lambda r, m, o: set_register(r, 'a', rotate_right(r, r.a, through_carry=True)),
    ),
    0xcb20: CPUInstruction(
        name='SLA B',
        length=2,
        cycles=8,
        opcode=0xcb20,
        run=lambda r, m, o: set_register(r, 'b', shift_left(r, r.b)),
    ),
    0xcb21: CPUInstruction(
        name='SLA C',
        length=2,
        cycles=8,
        opcode=0xcb21,
        run=lambda r, m, o: set_register(r, 'c', shift_left(r, r.c)),
    ),
    0xcb22: CPUInstruction(
        name='SLA D',
        length=2,
        cycles=8,
        opcode=0xcb22,
        run=lambda r, m, o: set_register(r, 'd', shift_left(r, r.d)),
    ),
    0xcb23: CPUInstruction(
        name='SLA E',
        length=2,
        cycles=8,
        opcode=0xcb23,
        run=lambda r, m, o: set_register(r, 'e', shift_left(r, r.e)),
    ),
    0xcb24: CPUInstruction(
        name='SLA H',
        length=2,
        cycles=8,
        opcode=0xcb24,
        run=lambda r, m, o: set_register(r, 'h', shift_left(r, r.h)),
    ),
    0xcb25: CPUInstruction(
        name='SLA L',
        length=2,
        cycles=8,
        opcode=0xcb25,
        run=lambda r, m, o: set_register(r, 'l', shift_left(r, r.l)),
    ),
    0xcb26: CPUInstruction(
        name='SLA (HL)',
        length=2,
        cycles=16,
        opcode=0xcb26,
        run=lambda r, m, o: m.write_u8(r.hl, shift_left(r, m.read(r.hl))),
    ),
    0xcb27: CPUInstruction(
        name='SLA A',
        length=2,
        cycles=8,
        opcode=0xcb27,
        run=lambda r, m, o: set_register(r, 'a', shift_left(r, r.a)),
    ),
    0xcb28: CPUInstruction(
        name='SRA B',
        length=2,
        cycles=8,
        opcode=0xcb28,
        run=lambda r, m, o: set_register(r, 'b', shift_right_arithmetic(r, r.b)),
    ),
    0xcb29: CPUInstruction(
        name='SRA C',
        length=2,
        cycles=8,
        opcode=0xcb29,
        run=lambda r, m, o: set_register(r, 'c', shift_right_arithmetic(r, r.c)),
    ),
    0xcb2a: CPUInstruction(
        name='SRA D',
        length=2,
        cycles=8,
        opcode=0xcb2a,
        run=lambda r, m, o: set_register(r, 'd', shift_right_arithmetic(r, r.d)),
    ),
    0xcb2b: CPUInstruction(
        name='SRA E',
        length=2,
        cycles=8,
        opcode=0xcb2b,
        run=lambda r, m, o: set_register(r, 'e', shift_right_arithmetic(r, r.e)),
    ),
    0xcb2c: CPUInstruction(
        name='SRA H',
        length=2,
        cycles=8,
        opcode=0xcb2c,
        run=lambda r, m, o: set_register(r, 'h', shift_right_arithmetic(r, r.h)),
    ),
    0xcb2d: CPUInstruction(
        name='SRA L',
        length=2,
        cycles=8,
        opcode=0xcb2d,
        run=lambda r, m, o: set_register(r, 'l', shift_right_arithmetic(r, r.l)),
    ),
    0xcb2e: CPUInstruction(
        name='SRA (HL)',
        length=2,
        cycles=16,
        opcode=0xcb2e,
        run=lambda r, m, o: m.write_u8(r.hl, shift_right_arithmetic(r, m.read(r.hl))),
    ),
    0xcb2f: CPUInstruction(
        name='SRA A',
        length=2,
        cycles=8,
        opcode=0xcb2f,
        run=lambda r, m, o: set_register(r, 'a', shift_right_arithmetic(r, r.a)),
    ),
    0xcb30: CPUInstruction(
        name='SWAP B',
        length=2,
        cycles=8,
        opcode=0xcb30,
        run=lambda r, m, o: set_register(r, 'b', swap(r, r.b)),
    ),
    0xcb31: CPUInstruction(
        name='SWAP C',
        length=2,
        cycles=8,
        opcode=0xcb31,
        run=lambda r, m, o: set_register(r, 'c', swap(r, r.c)),
    ),
    0xcb32: CPUInstruction(
        name='SWAP D',
        length=2,
        cycles=8,
        opcode=0xcb32,
        run=lambda r, m, o: set_register(r, 'd', swap(r, r.d)),
    ),
    0xcb33: CPUInstruction(
        name='SWAP E',
        length=2,
        cycles=8,
        opcode=0xcb33,
        run=lambda r, m, o: set_register(r, 'e', swap(r, r.e)),
    ),
    0xcb34: CPUInstruction(
        name='SWAP H',
        length=2,
        cycles=8,
        opcode=0xcb34,
        run=lambda r, m, o: set_register(r, 'h', swap(r, r.h)),
    ),
    0xcb35: CPUInstruction(
        name='SWAP L',
        length=2,
        cycles=8,
        opcode=0xcb35,
        run=lambda r, m, o: set_register(r, 'l', swap(r, r.l)),
    ),
    0xcb36: CPUInstruction(
        name='SWAP (HL)',
        length=2,
        cycles=16,
        opcode=0xcb36,
        run=lambda r, m, o: m.write_u8(r.hl, swap(r, m.read(r.hl))),
    ),
    0xcb37: CPUInstruction(
        name='SWAP A',
        length=2,
        cycles=8,
        opcode=0xcb37,
        run=lambda r, m, o: set_register(r, 'a', swap(r, r.a)),
    ),
    0xcb38: CPUInstruction(
        name='SRL B',
        length=2,
        cycles=8,
        opcode=0xcb38,
        run=lambda r, m, o: set_register(r, 'b', shift_right_logical(r, r.b)),
    ),
    0xcb39: CPUInstruction(
        name='SRL C',
        length=2,
        cycles=8,
        opcode=0xcb39,
        run=lambda r, m, o: set_register(r, 'c', shift_right_logical(r, r.c)),
    ),
    0xcb3a: CPUInstruction(
        name='SRL D',
        length=2,
        cycles=8,
        opcode=0xcb3a,
        run=lambda r, m, o: set_register(r, 'd', shift_right_logical(r, r.d)),
    ),
    0xcb3b: CPUInstruction(
        name='SRL E',
        length=2,
        cycles=8,
        opcode=0xcb3b,
        run=lambda r, m, o: set_register(r, 'e', shift_right_logical(r, r.e)),
    ),
    0xcb3c: CPUInstruction(
        name='SRL H',
        length=2,
        cycles=8,
        opcode=0xcb3c,
        run=lambda r, m, o: set_register(r, 'h', shift_right_logical(r, r.h)),
    ),
    0xcb3d: CPUInstruction(
        name='SRL L',
        length=2,
        cycles=8,
        opcode=0xcb3d,
        run=lambda r, m, o: set_register(r, 'l', shift_right_logical(r, r.l)),
    ),
    0xcb3e: CPUInstruction(
        name='SRL (HL)',
        length=2,
        cycles=16,
        opcode=0xcb3e,
        run=lambda r, m, o: m.write_u8(r.hl, shift_right_logical(r, m.read(r.hl))),
    ),
    0xcb3f: CPUInstruction(
        name='SRL A',
        length=2,
        cycles=8,
        opcode=0xcb3f,
        run=lambda r, m, o: set_register(r, 'a', shift_right_logical(r, r.a)),
    ),
    0xcb40: CPUInstruction(
        name='BIT 0,B',
        length=2,
        cycles=8,
        opcode=0xcb40,
        run=lambda r, m, o: test_bit(r, r.b, 0),
    ),
    0xcb41: CPUInstruction(
        name='BIT 0,C',
        length=2,
        cycles=8,
        opcode=0xcb41,
        run=lambda r, m, o: test_bit(r, r.c, 0),
    ),
    0xcb42: CPUInstruction(
        name='BIT 0,D',
        length=2,
        cycles=8,
        opcode=0xcb42,
        run=lambda r, m, o: test_bit(r, r.d, 0),
    ),
    0xcb43: CPUInstruction(
        name='BIT 0,E',
        length=2,
        cycles=8,
        opcode=0xcb43,
        run=lambda r, m, o: test_bit(r, r.e, 0),
    ),
    0xcb44: CPUInstruction(
        name='BIT 0,H',
        length=2,
        cycles=8,
        opcode=0xcb44,
        run=lambda r, m, o: test_bit(r, r.h, 0),
    ),
    0xcb45: CPUInstruction(
        name='BIT 0,L',
        length=2,
        cycles=8,
        opcode=0xcb45,
        run=lambda r, m, o: test_bit(r, r.l, 0),
    ),
    0xcb46: CPUInstruction(
        name='BIT 0,(HL)',
        length=2,
        cycles=12,
        opcode=0xcb46,
        run=lambda r, m, o: test_bit(r, m.read(r.hl), 0),
    ),
    0xcb47: CPUInstruction(
        name='BIT 0,A',
        length=2,
        cycles=8,
        opcode=0xcb47,
        run=lambda r, m, o: test_bit(r, r.a, 0),
    ),
    0xcb48: CPUInstruction(
        name='BIT 1,B',
        length=2,
        cycles=8,
        opcode=0xcb48,
        run=lambda r, m, o: test_bit(r, r.b, 1),
    ),
    0xcb49: CPUInstruction(
        name='BIT 1,C',
        length=2,
        cycles=8,
        opcode=0xcb49,
        run=lambda r, m, o: test_bit(r, r.c, 1),
    ),
    0xcb4a: CPUInstruction(
        name='BIT 1,D',
        length=2,
        cycles=8,
        opcode=0xcb4a,
        run=lambda r, m, o: test_bit(r, r.d, 1),
    ),
    0xcb4b: CPUInstruction(
        name='BIT 1,E',
        length=2,
        cycles=8,
        opcode=0xcb4b,
        run=lambda r, m, o: test_bit(r, r.e, 1),
    ),
    0xcb4c: CPUInstruction(
        name='BIT 1,H',
        length=2,
        cycles=8,
        opcode=0xcb4c,
        run=lambda r, m, o: test_bit(r, r.h, 1),
    ),
    0xcb4d: CPUInstruction(
        name='BIT 1,L',
        length=2,
        cycles=8,
        opcode=0xcb4d,
        run=lambda r, m, o: test_bit(r, r.l, 1),
    ),
    0xcb4e: CPUInstruction(
        name='BIT 1,(HL)',
        length=2,
        cycles=12,
        opcode=0xcb4e,
        run=lambda r, m, o: test_bit(r, m.read(r.hl), 1),
    ),
    0xcb4f: CPUInstruction(
        name='BIT 1,A',
        length=2,
        cycles=8,
        opcode=0xcb4f,
        run=lambda r, m, o: test_bit(r, r.a, 1),
    ),
    0xcb50: CPUInstruction(
        name='BIT 2,B',
        length=2,
        cycles=8,
        opcode=0xcb50,
        run=lambda r, m, o: test_bit(r, r.b, 2),
    ),
    0xcb51: CPUInstruction(
        name='BIT 2,C',
        length=2,
        cycles=8,
        opcode=0xcb51,
        run=lambda r, m, o: test_bit(r, r.c, 2),
    ),
    0xcb52: CPUInstruction(
        name='BIT 2,D',
        length=2,
        cycles=8,
        opcode=0xcb52,
        run=lambda r, m, o: test_bit(r, r.d, 2),
    ),
    0xcb53: CPUInstruction(
        name='BIT 2,E',
        length=2,
        cycles=8,
        opcode=0xcb53,
        run=lambda r, m, o: test_bit(r, r.e, 2),
    ),
    0xcb54: CPUInstruction(
        name='BIT 2,H',
        length=2,
        cycles=8,
        opcode=0xcb54,
        run=lambda r, m, o: test_bit(r, r.h, 2),
    ),
    0xcb55: CPUInstruction(
        name='BIT 2,L',
        length=2,
        cycles=8,
        opcode=0xcb55,
        run=lambda r, m, o: test_bit(r, r.l, 2),
    ),
    0xcb56: CPUInstruction(
        name='BIT 2,(HL)',
        length=2,
        cycles=12,
        opcode=0xcb56,
        run=lambda r, m, o: test_bit(r, m.read(r.hl), 2),
    ),
    0xcb57: CPUInstruction(
        name='BIT 2,A',
        length=2,
        cycles=8,
        opcode=0xcb57,
        run=lambda r, m, o: test_bit(r, r.a, 2),
    ),
    0xcb58: CPUInstruction(
        name='BIT 3,B',
        length=2,
        cycles=8,
        opcode=0xcb58,
        run=lambda r, m, o: test_bit(r, r.b, 3),
    ),
    0xcb59: CPUInstruction(
        name='BIT 3,C',
        length=2,
        cycles=8,
        opcode=0xcb59,
        run=lambda r, m, o: test_bit(r, r.c, 3),
    ),
    0xcb5a: CPUInstruction(
        name='BIT 3,D',
        length=2,
        cycles=8,
        opcode=0xcb5a,
        run=lambda r, m, o: test_bit(r, r.d, 3),
    ),
    0xcb5b: CPUInstruction(
        name='BIT 3,E',
        length=2,
        cycles=8,
        opcode=0xcb5b,
        run=lambda r, m, o: test_bit(r, r.e, 3),
    ),
    0xcb5c: CPUInstruction(
        name='BIT 3,H',
        length=2,
        cycles=8,
        opcode=0xcb5c,
        run=lambda r, m, o: test_bit(r, r.h, 3),
    ),
    0xcb5d: CPUInstruction(
        name='BIT 3,L',
        length=2,
        cycles=8,
        opcode=0xcb5d,
        run=lambda r, m, o: test_bit(r, r.l, 3),
    ),
    0xcb5e: CPUInstruction(
        name='BIT 3,(HL)',
        length=2,
        cycles=12,
        opcode=0xcb5e,
        run=lambda r, m, o: test_bit(r, m.read(r.hl), 3),
    ),
    0xcb5f: CPUInstruction(
        name='BIT 3,A',
        length=2,
        cycles=8,
        opcode=0xcb5f,
        run=lambda r, m, o: test_bit(r, r.a, 3),
    ),
    0xcb60: CPUInstruction(
        name='BIT 4,B',
        length=2,
        cycles=8,
        opcode=0xcb60,
        run=lambda r, m, o: test_bit(r, r.b, 4),
    ),
    0xcb61: CPUInstruction(
        name='BIT 4,C',
        length=2,
        cycles=8,
        opcode=0xcb61,
        run=lambda r, m, o: test_bit(r, r.c, 4),
    ),
    0xcb62: CPUInstruction(
        name='BIT 4,D',
        length=2,
        cycles=8,
        opcode=0xcb62,
        run=lambda r, m, o: test_bit(r, r.d, 4),
    ),
    0xcb63: CPUInstruction(
        name='BIT 4,E',
        length=2,
        cycles=8,
        opcode=0xcb63,
        run=lambda r, m, o: test_bit(r, r.e, 4),
    ),
    0xcb64: CPUInstruction(
        name='BIT 4,H',
        length=2,
        cycles=8,
        opcode=0xcb64,
        run=lambda r, m, o: test_bit(r, r.h, 4),
    ),
    0xcb65: CPUInstruction(
        name='BIT 4,L',
        length=2,
        cycles=8,
        opcode=0xcb65,
        run=lambda r, m, o: test_bit(r, r.l, 4),
    ),
    0xcb66: CPUInstruction(
        name='BIT 4,(HL)',
        length=2,
        cycles=12,
        opcode=0xcb66,
        run=lambda r, m, o: test_bit(r, m.read(r.hl), 4),
    ),
    0xcb67: CPUInstruction(
        name='BIT 4,A',
        length=2,
        cycles=8,
        opcode=0xcb67,
        run=lambda r, m, o: test_bit(r, r.a, 4),
    ),
    0xcb68: CPUInstruction(
        name='BIT 5,B',
        length=2,
        cycles=8,
        opcode=0xcb68,
        run=lambda r, m, o: test_bit(r, r.b, 5),
    ),
    0xcb69: CPUInstruction(
        name='BIT 5,C',
        length=2,
        cycles=8,
        opcode=0xcb69,
        run=lambda r, m, o: test_bit(r, r.c, 5),
    ),
    0xcb6a: CPUInstruction(
        name='BIT 5,D',
        length=2,
        cycles=8,
        opcode=0xcb6a,
        run=lambda r, m, o: test_bit(r, r.d, 5),
    ),
    0xcb6b: CPUInstruction(
        name='BIT 5,E',
        length=2,
        cycles=8,
        opcode=0xcb6b,
        run=lambda r, m, o: test_bit(r, r.e, 5),
    ),
    0xcb6c: CPUInstruction(
        name='BIT 5,H',
        length=2,
        cycles=8,
        opcode=0xcb6c,
        run=lambda r, m, o: test_bit(r, r.h, 5),
    ),
    0xcb6d: CPUInstruction(
        name='BIT 5,L',
        length=2,
        cycles=8,
        opcode=0xcb6d,
        run=lambda r, m, o: test_bit(r, r.l, 5),
    ),
    0xcb6e: CPUInstruction(
        name='BIT 5,(HL)',
        length=2,
        cycles=12,
        opcode=0xcb6e,
        run=lambda r, m, o: test_bit(r, m.read(r.hl), 5),
    ),
    0xcb6f: CPUInstruction(
        name='BIT 5,A',
        length=2,
        cycles=8,
        opcode=0xcb6f,
        run=lambda r, m, o: test_bit(r, r.a, 5),
    ),
    0xcb70: CPUInstruction(
        name='BIT 6,B',
        length=2,
        cycles=8,
        opcode=0xcb70,
        run=lambda r, m, o: test_bit(r, r.b, 6),
    ),
    0xcb71: CPUInstruction(
        name='BIT 6,C',
        length=2,
        cycles=8,
        opcode=0xcb71,
        run=lambda r, m, o: test_bit(r, r.c, 6),
    ),
    0xcb72: CPUInstruction(
        name='BIT 6,D',
        length=2,
        cycles=8,
        opcode=0xcb72,
        run=lambda r, m, o: test_bit(r, r.d, 6),
    ),
    0xcb73: CPUInstruction(
        name='BIT 6,E',
        length=2,
        cycles=8,
        opcode=0xcb73,
        run=lambda r, m, o: test_bit(r, r.e, 6),
    ),
    0xcb74: CPUInstruction(
        name='BIT 6,H',
        length=2,
        cycles=8,
        opcode=0xcb74,
        run=lambda r, m, o: test_bit(r, r.h, 6),
    ),
    0xcb75: CPUInstruction(
        name='BIT 6,L',
        length=2,
        cycles=8,
        opcode=0xcb75,
        run=lambda r, m, o: test_bit(r, r.l, 6),
    ),
    0xcb76: CPUInstruction(
        name='BIT 6,(HL)',
        length=2,
        cycles=12,
        opcode=0xcb76,
        run=lambda r, m, o: test_bit(r, m.read(r.hl), 6),
    ),
    0xcb77: CPUInstruction(
        name='BIT 6,A',
        length=2,
        cycles=8,
        opcode=0xcb77,
        run=lambda r, m, o: test_bit(r, r.a, 6),
    ),
    0xcb78: CPUInstruction(
        name='BIT 7,B',
        length=2,
        cycles=8,
        opcode=0xcb78,
        run=lambda r, m, o: test_bit(r, r.b, 7),
    ),
    0xcb79: CPUInstruction(
        name='BIT 7,C',
        length=2,
        cycles=8,
        opcode=0xcb79,
        run=lambda r, m, o: test_bit(r, r.c, 7),
    ),
    0xcb7a: CPUInstruction(
        name='BIT 7,D',
        length=2,
        cycles=8,
        opcode=0xcb7a,
        run=lambda r, m, o: test_bit(r, r.d, 7),
    ),
    0xcb7b: CPUInstruction(
        name='BIT 7,E',
        length=2,
        cycles=8,
        opcode=0xcb7b,
        run=lambda r, m, o: test_bit(r, r.e, 7),
    ),
    0xcb7c: CPUInstruction(
        name='BIT 7,H',
        length=2,
        cycles=8,
        opcode=0xcb7c,
        run=lambda r, m, o: test_bit(r, r.h, 7),
    ),
    0xcb7d: CPUInstruction(
        name='BIT 7,L',
        length=2,
        cycles=8,
        opcode=0xcb7d,
        run=lambda r, m, o: test_bit(r, r.l, 7),
    ),
    0xcb7e: CPUInstruction(
        name='BIT 7,(HL)',
        length=2,
        cycles=12,
        opcode=0xcb7e,
        run=lambda r, m, o: test_bit(r, m.read(r.hl), 7),
    ),
    0xcb7f: CPUInstruction(
        name='BIT 7,A',
        length=2,
        cycles=8,
        opcode=0xcb7f,
        run=lambda r, m, o: test_bit(r, r.a, 7),
    ),
    0xcb80: CPUInstruction(
        name='RES 0,B',
        length=2,
        cycles=8,
        opcode=0xcb80,
        run=lambda r, m, o: setattr(r, 'b', set_bit(r.b, 0, 0)),
    ),
    0xcb81: CPUInstruction(
        name='RES 0,C',
        length=2,
        cycles=8,
        opcode=0xcb81,
        run=lambda r, m, o: setattr(r, 'c', set_bit(r.c, 0, 0)),
    ),
    0xcb82: CPUInstruction(
        name='RES 0,D',
        length=2,
        cycles=8,
        opcode=0xcb82,
        run=lambda r, m, o: setattr(r, 'd', set_bit(r.d, 0, 0)),
    ),
    0xcb83: CPUInstruction(
        name='RES 0,E',
        length=2,
        cycles=8,
        opcode=0xcb83,
        run=lambda r, m, o: setattr(r, 'e', set_bit(r.e, 0, 0)),
    ),
    0xcb84: CPUInstruction(
        name='RES 0,H',
        length=2,
        cycles=8,
        opcode=0xcb84,
        run=lambda r, m, o: setattr(r, 'h', set_bit(r.h, 0, 0)),
    ),
    0xcb85: CPUInstruction(
        name='RES 0,L',
        length=2,
        cycles=8,
        opcode=0xcb85,
        run=lambda r, m, o: setattr(r, 'l', set_bit(r.l, 0, 0)),
    ),
    0xcb86: CPUInstruction(
        name='RES 0,(HL)',
        length=2,
        cycles=16,
        opcode=0xcb86,
        run=lambda r, m, o: m.write(r.hl, set_bit(m.read(r.hl), 0, 0)),
    ),
    0xcb87: CPUInstruction(
        name='RES 0,A',
        length=2,
        cycles=8,
        opcode=0xcb87,
        run=lambda r, m, o: setattr(r, 'a', set_bit(r.a, 0, 0)),
    ),
    0xcb88: CPUInstruction(
        name='RES 1,B',
        length=2,
        cycles=8,
        opcode=0xcb88,
        run=lambda r, m, o: setattr(r, 'b', set_bit(r.b, 1, 0)),
    ),
    0xcb89: CPUInstruction(
        name='RES 1,C',
        length=2,
        cycles=8,
        opcode=0xcb89,
        run=lambda r, m, o: setattr(r, 'c', set_bit(r.c, 1, 0)),
    ),
    0xcb8a: CPUInstruction(
        name='RES 1,D',
        length=2,
        cycles=8,
        opcode=0xcb8a,
        run=lambda r, m, o: setattr(r, 'd', set_bit(r.d, 1, 0)),
    ),
    0xcb8b: CPUInstruction(
        name='RES 1,E',
        length=2,
        cycles=8,
        opcode=0xcb8b,
        run=lambda r, m, o: setattr(r, 'e', set_bit(r.e, 1, 0)),
    ),
    0xcb8c: CPUInstruction(
        name='RES 1,H',
        length=2,
        cycles=8,
        opcode=0xcb8c,
        run=lambda r, m, o: setattr(r, 'h', set_bit(r.h, 1, 0)),
    ),
    0xcb8d: CPUInstruction(
        name='RES 1,L',
        length=2,
        cycles=8,
        opcode=0xcb8d,
        run=lambda r, m, o: setattr(r, 'l', set_bit(r.l, 1, 0)),
    ),
    0xcb8e: CPUInstruction(
        name='RES 1,(HL)',
        length=2,
        cycles=16,
        opcode=0xcb8e,
        run=lambda r, m, o: m.write(r.hl, set_bit(m.read(r.hl), 1, 0)),
    ),
    0xcb8f: CPUInstruction(
        name='RES 1,A',
        length=2,
        cycles=8,
        opcode=0xcb8f,
        run=lambda r, m, o: setattr(r, 'a', set_bit(r.a, 1, 0)),
    ),
    0xcb90: CPUInstruction(
        name='RES 2,B',
        length=2,
        cycles=8,
        opcode=0xcb90,
        run=lambda r, m, o: setattr(r, 'b', set_bit(r.b, 2, 0)),
    ),
    0xcb91: CPUInstruction(
        name='RES 2,C',
        length=2,
        cycles=8,
        opcode=0xcb91,
        run=lambda r, m, o: setattr(r, 'c', set_bit(r.c, 2, 0)),
    ),
    0xcb92: CPUInstruction(
        name='RES 2,D',
        length=2,
        cycles=8,
        opcode=0xcb92,
        run=lambda r, m, o: setattr(r, 'd', set_bit(r.d, 2, 0)),
    ),
    0xcb93: CPUInstruction(
        name='RES 2,E',
        length=2,
        cycles=8,
        opcode=0xcb93,
        run=lambda r, m, o: setattr(r, 'e', set_bit(r.e, 2, 0)),
    ),
    0xcb94: CPUInstruction(
        name='RES 2,H',
        length=2,
        cycles=8,
        opcode=0xcb94,
        run=lambda r, m, o: setattr(r, 'h', set_bit(r.h, 2, 0)),
    ),
    0xcb95: CPUInstruction(
        name='RES 2,L',
        length=2,
        cycles=8,
        opcode=0xcb95,
        run=lambda r, m, o: setattr(r, 'l', set_bit(r.l, 2, 0)),
    ),
    0xcb96: CPUInstruction(
        name='RES 2,(HL)',
        length=2,
        cycles=16,
        opcode=0xcb96,
        run=lambda r, m, o: m.write(r.hl, set_bit(m.read(r.hl), 2, 0)),
    ),
    0xcb97: CPUInstruction(
        name='RES 2,A',
        length=2,
        cycles=8,
        opcode=0xcb97,
        run=lambda r, m, o: setattr(r, 'a', set_bit(r.a, 2, 0)),
    ),
    0xcb98: CPUInstruction(
        name='RES 3,B',
        length=2,
        cycles=8,
        opcode=0xcb98,
        run=lambda r, m, o: setattr(r, 'b', set_bit(r.b, 3, 0)),
    ),
    0xcb99: CPUInstruction(
        name='RES 3,C',
        length=2,
        cycles=8,
        opcode=0xcb99,
        run=lambda r, m, o: setattr(r, 'c', set_bit(r.c, 3, 0)),
    ),
    0xcb9a: CPUInstruction(
        name='RES 3,D',
        length=2,
        cycles=8,
        opcode=0xcb9a,
        run=lambda r, m, o: setattr(r, 'd', set_bit(r.d, 3, 0)),
    ),
    0xcb9b: CPUInstruction(
        name='RES 3,E',
        length=2,
        cycles=8,
        opcode=0xcb9b,
        run=lambda r, m, o: setattr(r, 'e', set_bit(r.e, 3, 0)),
    ),
    0xcb9c: CPUInstruction(
        name='RES 3,H',
        length=2,
        cycles=8,
        opcode=0xcb9c,
        run=lambda r, m, o: setattr(r, 'h', set_bit(r.h, 3, 0)),
    ),
    0xcb9d: CPUInstruction(
        name='RES 3,L',
        length=2,
        cycles=8,
        opcode=0xcb9d,
        run=lambda r, m, o: setattr(r, 'l', set_bit(r.l, 3, 0)),
    ),
    0xcb9e: CPUInstruction(
        name='RES 3,(HL)',
        length=2,
        cycles=16,
        opcode=0xcb9e,
        run=lambda r, m, o: m.write(r.hl, set_bit(m.read(r.hl), 3, 0)),
    ),
    0xcb9f: CPUInstruction(
        name='RES 3,A',
        length=2,
        cycles=8,
        opcode=0xcb9f,
        run=lambda r, m, o: setattr(r, 'a', set_bit(r.a, 3, 0)),
    ),
    0xcba0: CPUInstruction(
        name='RES 4,B',
        length=2,
        cycles=8,
        opcode=0xcba0,
        run=lambda r, m, o: setattr(r, 'b', set_bit(r.b, 4, 0)),
    ),
    0xcba1: CPUInstruction(
        name='RES 4,C',
        length=2,
        cycles=8,
        opcode=0xcba1,
        run=lambda r, m, o: setattr(r, 'c', set_bit(r.c, 4, 0)),
    ),
    0xcba2: CPUInstruction(
        name='RES 4,D',
        length=2,
        cycles=8,
        opcode=0xcba2,
        run=lambda r, m, o: setattr(r, 'd', set_bit(r.d, 4, 0)),
    ),
    0xcba3: CPUInstruction(
        name='RES 4,E',
        length=2,
        cycles=8,
        opcode=0xcba3,
        run=lambda r, m, o: setattr(r, 'e', set_bit(r.e, 4, 0)),
    ),
    0xcba4: CPUInstruction(
        name='RES 4,H',
        length=2,
        cycles=8,
        opcode=0xcba4,
        run=lambda r, m, o: setattr(r, 'h', set_bit(r.h, 4, 0)),
    ),
    0xcba5: CPUInstruction(
        name='RES 4,L',
        length=2,
        cycles=8,
        opcode=0xcba5,
        run=lambda r, m, o: setattr(r, 'l', set_bit(r.l, 4, 0)),
    ),
    0xcba6: CPUInstruction(
        name='RES 4,(HL)',
        length=2,
        cycles=16,
        opcode=0xcba6,
        run=lambda r, m, o: m.write(r.hl, set_bit(m.read(r.hl), 4, 0)),
    ),
    0xcba7: CPUInstruction(
        name='RES 4,A',
        length=2,
        cycles=8,
        opcode=0xcba7,
        run=lambda r, m, o: setattr(r, 'a', set_bit(r.a, 4, 0)),
    ),
    0xcba8: CPUInstruction(
        name='RES 5,B',
        length=2,
        cycles=8,
        opcode=0xcba8,
        run=lambda r, m, o: setattr(r, 'b', set_bit(r.b, 5, 0)),
    ),
    0xcba9: CPUInstruction(
        name='RES 5,C',
        length=2,
        cycles=8,
        opcode=0xcba9,
        run=lambda r, m, o: setattr(r, 'c', set_bit(r.c, 5, 0)),
    ),
    0xcbaa: CPUInstruction(
        name='RES 5,D',
        length=2,
        cycles=8,
        opcode=0xcbaa,
        run=lambda r, m, o: setattr(r, 'd', set_bit(r.d, 5, 0)),
    ),
    0xcbab: CPUInstruction(
        name='RES 5,E',
        length=2,
        cycles=8,
        opcode=0xcbab,
        run=lambda r, m, o: setattr(r, 'e', set_bit(r.e, 5, 0)),
    ),
    0xcbac: CPUInstruction(
        name='RES 5,H',
        length=2,
        cycles=8,
        opcode=0xcbac,
        run=lambda r, m, o: setattr(r, 'h', set_bit(r.h, 5, 0)),
    ),
    0xcbad: CPUInstruction(
        name='RES 5,L',
        length=2,
        cycles=8,
        opcode=0xcbad,
        run=lambda r, m, o: setattr(r, 'l', set_bit(r.l, 5, 0)),
    ),
    0xcbae: CPUInstruction(
        name='RES 5,(HL)',
        length=2,
        cycles=16,
        opcode=0xcbae,
        run=lambda r, m, o: m.write(r.hl, set_bit(m.read(r.hl), 5, 0)),
    ),
    0xcbaf: CPUInstruction(
        name='RES 5,A',
        length=2,
        cycles=8,
        opcode=0xcbaf,
        run=lambda r, m, o: setattr(r, 'a', set_bit(r.a, 5, 0)),
    ),
    0xcbb0: CPUInstruction(
        name='RES 6,B',
        length=2,
        cycles=8,
        opcode=0xcbb0,
        run=lambda r, m, o: setattr(r, 'b', set_bit(r.b, 6, 0)),
    ),
    0xcbb1: CPUInstruction(
        name='RES 6,C',
        length=2,
        cycles=8,
        opcode=0xcbb1,
        run=lambda r, m, o: setattr(r, 'c', set_bit(r.c, 6, 0)),
    ),
    0xcbb2: CPUInstruction(
        name='RES 6,D',
        length=2,
        cycles=8,
        opcode=0xcbb2,
        run=lambda r, m, o: setattr(r, 'd', set_bit(r.d, 6, 0)),
    ),
    0xcbb3: CPUInstruction(
        name='RES 6,E',
        length=2,
        cycles=8,
        opcode=0xcbb3,
        run=lambda r, m, o: setattr(r, 'e', set_bit(r.e, 6, 0)),
    ),
    0xcbb4: CPUInstruction(
        name='RES 6,H',
        length=2,
        cycles=8,
        opcode=0xcbb4,
        run=lambda r, m, o: setattr(r, 'h', set_bit(r.h, 6, 0)),
    ),
    0xcbb5: CPUInstruction(
        name='RES 6,L',
        length=2,
        cycles=8,
        opcode=0xcbb5,
        run=lambda r, m, o: setattr(r, 'l', set_bit(r.l, 6, 0)),
    ),
    0xcbb6: CPUInstruction(
        name='RES 6,(HL)',
        length=2,
        cycles=16,
        opcode=0xcbb6,
        run=lambda r, m, o: m.write(r.hl, set_bit(m.read(r.hl), 6, 0)),
    ),
    0xcbb7: CPUInstruction(
        name='RES 6,A',
        length=2,
        cycles=8,
        opcode=0xcbb7,
        run=lambda r, m, o: setattr(r, 'a', set_bit(r.a, 6, 0)),
    ),
    0xcbb8: CPUInstruction(
        name='RES 7,B',
        length=2,
        cycles=8,
        opcode=0xcbb8,
        run=lambda r, m, o: setattr(r, 'b', set_bit(r.b, 7, 0)),
    ),
    0xcbb9: CPUInstruction(
        name='RES 7,C',
        length=2,
        cycles=8,
        opcode=0xcbb9,
        run=lambda r, m, o: setattr(r, 'c', set_bit(r.c, 7, 0)),
    ),
    0xcbba: CPUInstruction(
        name='RES 7,D',
        length=2,
        cycles=8,
        opcode=0xcbba,
        run=lambda r, m, o: setattr(r, 'd', set_bit(r.d, 7, 0)),
    ),
    0xcbbb: CPUInstruction(
        name='RES 7,E',
        length=2,
        cycles=8,
        opcode=0xcbbb,
        run=lambda r, m, o: setattr(r, 'e', set_bit(r.e, 7, 0)),
    ),
    0xcbbc: CPUInstruction(
        name='RES 7,H',
        length=2,
        cycles=8,
        opcode=0xcbbc,
        run=lambda r, m, o: setattr(r, 'h', set_bit(r.h, 7, 0)),
    ),
    0xcbbd: CPUInstruction(
        name='RES 7,L',
        length=2,
        cycles=8,
        opcode=0xcbbd,
        run=lambda r, m, o: setattr(r, 'l', set_bit(r.l, 7, 0)),
    ),
    0xcbbe: CPUInstruction(
        name='RES 7,(HL)',
        length=2,
        cycles=16,
        opcode=0xcbbe,
        run=lambda r, m, o: m.write(r.hl, set_bit(m.read(r.hl), 7, 0)),
    ),
    0xcbbf: CPUInstruction(
        name='RES 7,A',
        length=2,
        cycles=8,
        opcode=0xcbbf,
        run=lambda r, m, o: setattr(r, 'a', set_bit(r.a, 7, 0)),
    ),
    0xcbc0: CPUInstruction(
        name='SET 0,B',
        length=2,
        cycles=8,
        opcode=0xcbc0,
        run=lambda r, m, o: setattr(r, 'b', set_bit(r.b, 0, 1)),
    ),
    0xcbc1: CPUInstruction(
        name='SET 0,C',
        length=2,
        cycles=8,
        opcode=0xcbc1,
        run=lambda r, m, o: setattr(r, 'c', set_bit(r.c, 0, 1)),
    ),
    0xcbc2: CPUInstruction(
        name='SET 0,D',
        length=2,
        cycles=8,
        opcode=0xcbc2,
        run=lambda r, m, o: setattr(r, 'd', set_bit(r.d, 0, 1)),
    ),
    0xcbc3: CPUInstruction(
        name='SET 0,E',
        length=2,
        cycles=8,
        opcode=0xcbc3,
        run=lambda r, m, o: setattr(r, 'e', set_bit(r.e, 0, 1)),
    ),
    0xcbc4: CPUInstruction(
        name='SET 0,H',
        length=2,
        cycles=8,
        opcode=0xcbc4,
        run=lambda r, m, o: setattr(r, 'h', set_bit(r.h, 0, 1)),
    ),
    0xcbc5: CPUInstruction(
        name='SET 0,L',
        length=2,
        cycles=8,
        opcode=0xcbc5,
        run=lambda r, m, o: setattr(r, 'l', set_bit(r.l, 0, 1)),
    ),
    0xcbc6: CPUInstruction(
        name='SET 0,(HL)',
        length=2,
        cycles=16,
        opcode=0xcbc6,
        run=lambda r, m, o: m.write(r.hl, set_bit(m.read(r.hl), 0, 1)),
    ),
    0xcbc7: CPUInstruction(
        name='SET 0,A',
        length=2,
        cycles=8,
        opcode=0xcbc7,
        run=lambda r, m, o: setattr(r, 'a', set_bit(r.a, 0, 1)),
    ),
    0xcbc8: CPUInstruction(
        name='SET 1,B',
        length=2,
        cycles=8,
        opcode=0xcbc8,
        run=lambda r, m, o: setattr(r, 'b', set_bit(r.b, 1, 1)),
    ),
    0xcbc9: CPUInstruction(
        name='SET 1,C',
        length=2,
        cycles=8,
        opcode=0xcbc9,
        run=lambda r, m, o: setattr(r, 'c', set_bit(r.c, 1, 1)),
    ),
    0xcbca: CPUInstruction(
        name='SET 1,D',
        length=2,
        cycles=8,
        opcode=0xcbca,
        run=lambda r, m, o: setattr(r, 'd', set_bit(r.d, 1, 1)),
    ),
    0xcbcb: CPUInstruction(
        name='SET 1,E',
        length=2,
        cycles=8,
        opcode=0xcbcb,
        run=lambda r, m, o: setattr(r, 'e', set_bit(r.e, 1, 1)),
    ),
    0xcbcc: CPUInstruction(
        name='SET 1,H',
        length=2,
        cycles=8,
        opcode=0xcbcc,
        run=lambda r, m, o: setattr(r, 'h', set_bit(r.h, 1, 1)),
    ),
    0xcbcd: CPUInstruction(
        name='SET 1,L',
        length=2,
        cycles=8,
        opcode=0xcbcd,
        run=lambda r, m, o: setattr(r, 'l', set_bit(r.l, 1, 1)),
    ),
    0xcbce: CPUInstruction(
        name='SET 1,(HL)',
        length=2,
        cycles=16,
        opcode=0xcbce,
        run=lambda r, m, o: m.write(r.hl, set_bit(m.read(r.hl), 1, 1)),
    ),
    0xcbcf: CPUInstruction(
        name='SET 1,A',
        length=2,
        cycles=8,
        opcode=0xcbcf,
        run=lambda r, m, o: setattr(r, 'a', set_bit(r.a, 1, 1)),
    ),
    0xcbd0: CPUInstruction(
        name='SET 2,B',
        length=2,
        cycles=8,
        opcode=0xcbd0,
        run=lambda r, m, o: setattr(r, 'b', set_bit(r.b, 2, 1)),
    ),
    0xcbd1: CPUInstruction(
        name='SET 2,C',
        length=2,
        cycles=8,
        opcode=0xcbd1,
        run=lambda r, m, o: setattr(r, 'c', set_bit(r.c, 2, 1)),
    ),
    0xcbd2: CPUInstruction(
        name='SET 2,D',
        length=2,
        cycles=8,
        opcode=0xcbd2,
        run=lambda r, m, o: setattr(r, 'd', set_bit(r.d, 2, 1)),
    ),
    0xcbd3: CPUInstruction(
        name='SET 2,E',
        length=2,
        cycles=8,
        opcode=0xcbd3,
        run=lambda r, m, o: setattr(r, 'e', set_bit(r.e, 2, 1)),
    ),
    0xcbd4: CPUInstruction(
        name='SET 2,H',
        length=2,
        cycles=8,
        opcode=0xcbd4,
        run=lambda r, m, o: setattr(r, 'h', set_bit(r.h, 2, 1)),
    ),
    0xcbd5: CPUInstruction(
        name='SET 2,L',
        length=2,
        cycles=8,
        opcode=0xcbd5,
        run=lambda r, m, o: setattr(r, 'l', set_bit(r.l, 2, 1)),
    ),
    0xcbd6: CPUInstruction(
        name='SET 2,(HL)',
        length=2,
        cycles=16,
        opcode=0xcbd6,
        run=lambda r, m, o: m.write(r.hl, set_bit(m.read(r.hl), 2, 1)),
    ),
    0xcbd7: CPUInstruction(
        name='SET 2,A',
        length=2,
        cycles=8,
        opcode=0xcbd7,
        run=lambda r, m, o: setattr(r, 'a', set_bit(r.a, 2, 1)),
    ),
    0xcbd8: CPUInstruction(
        name='SET 3,B',
        length=2,
        cycles=8,
        opcode=0xcbd8,
        run=lambda r, m, o: setattr(r, 'b', set_bit(r.b, 3, 1)),
    ),
    0xcbd9: CPUInstruction(
        name='SET 3,C',
        length=2,
        cycles=8,
        opcode=0xcbd9,
        run=lambda r, m, o: setattr(r, 'c', set_bit(r.c, 3, 1)),
    ),
    0xcbda: CPUInstruction(
        name='SET 3,D',
        length=2,
        cycles=8,
        opcode=0xcbda,
        run=lambda r, m, o: setattr(r, 'd', set_bit(r.d, 3, 1)),
    ),
    0xcbdb: CPUInstruction(
        name='SET 3,E',
        length=2,
        cycles=8,
        opcode=0xcbdb,
        run=lambda r, m, o: setattr(r, 'e', set_bit(r.e, 3, 1)),
    ),
    0xcbdc: CPUInstruction(
        name='SET 3,H',
        length=2,
        cycles=8,
        opcode=0xcbdc,
        run=lambda r, m, o: setattr(r, 'h', set_bit(r.h, 3, 1)),
    ),
    0xcbdd: CPUInstruction(
        name='SET 3,L',
        length=2,
        cycles=8,
        opcode=0xcbdd,
        run=lambda r, m, o: setattr(r, 'l', set_bit(r.l, 3, 1)),
    ),
    0xcbde: CPUInstruction(
        name='SET 3,(HL)',
        length=2,
        cycles=16,
        opcode=0xcbde,
        run=lambda r, m, o: m.write(r.hl, set_bit(m.read(r.hl), 3, 1)),
    ),
    0xcbdf: CPUInstruction(
        name='SET 3,A',
        length=2,
        cycles=8,
        opcode=0xcbdf,
        run=lambda r, m, o: setattr(r, 'a', set_bit(r.a, 3, 1)),
    ),
    0xcbe0: CPUInstruction(
        name='SET 4,B',
        length=2,
        cycles=8,
        opcode=0xcbe0,
        run=lambda r, m, o: setattr(r, 'b', set_bit(r.b, 4, 1)),
    ),
    0xcbe1: CPUInstruction(
        name='SET 4,C',
        length=2,
        cycles=8,
        opcode=0xcbe1,
        run=lambda r, m, o: setattr(r, 'c', set_bit(r.c, 4, 1)),
    ),
    0xcbe2: CPUInstruction(
        name='SET 4,D',
        length=2,
        cycles=8,
        opcode=0xcbe2,
        run=lambda r, m, o: setattr(r, 'd', set_bit(r.d, 4, 1)),
    ),
    0xcbe3: CPUInstruction(
        name='SET 4,E',
        length=2,
        cycles=8,
        opcode=0xcbe3,
        run=lambda r, m, o: setattr(r, 'e', set_bit(r.e, 4, 1)),
    ),
    0xcbe4: CPUInstruction(
        name='SET 4,H',
        length=2,
        cycles=8,
        opcode=0xcbe4,
        run=lambda r, m, o: setattr(r, 'h', set_bit(r.h, 4, 1)),
    ),
    0xcbe5: CPUInstruction(
        name='SET 4,L',
        length=2,
        cycles=8,
        opcode=0xcbe5,
        run=lambda r, m, o: setattr(r, 'l', set_bit(r.l, 4, 1)),
    ),
    0xcbe6: CPUInstruction(
        name='SET 4,(HL)',
        length=2,
        cycles=16,
        opcode=0xcbe6,
        run=lambda r, m, o: m.write(r.hl, set_bit(m.read(r.hl), 4, 1)),
    ),
    0xcbe7: CPUInstruction(
        name='SET 4,A',
        length=2,
        cycles=8,
        opcode=0xcbe7,
        run=lambda r, m, o: setattr(r, 'a', set_bit(r.a, 4, 1)),
    ),
    0xcbe8: CPUInstruction(
        name='SET 5,B',
        length=2,
        cycles=8,
        opcode=0xcbe8,
        run=lambda r, m, o: setattr(r, 'b', set_bit(r.b, 5, 1)),
    ),
    0xcbe9: CPUInstruction(
        name='SET 5,C',
        length=2,
        cycles=8,
        opcode=0xcbe9,
        run=lambda r, m, o: setattr(r, 'c', set_bit(r.c, 5, 1)),
    ),
    0xcbea: CPUInstruction(
        name='SET 5,D',
        length=2,
        cycles=8,
        opcode=0xcbea,
        run=lambda r, m, o: setattr(r, 'd', set_bit(r.d, 5, 1)),
    ),
    0xcbeb: CPUInstruction(
        name='SET 5,E',
        length=2,
        cycles=8,
        opcode=0xcbeb,
        run=lambda r, m, o: setattr(r, 'e', set_bit(r.e, 5, 1)),
    ),
    0xcbec: CPUInstruction(
        name='SET 5,H',
        length=2,
        cycles=8,
        opcode=0xcbec,
        run=lambda r, m, o: setattr(r, 'h', set_bit(r.h, 5, 1)),
    ),
    0xcbed: CPUInstruction(
        name='SET 5,L',
        length=2,
        cycles=8,
        opcode=0xcbed,
        run=lambda r, m, o: setattr(r, 'l', set_bit(r.l, 5, 1)),
    ),
    0xcbee: CPUInstruction(
        name='SET 5,(HL)',
        length=2,
        cycles=16,
        opcode=0xcbee,
        run=lambda r, m, o: m.write(r.hl, set_bit(m.read(r.hl), 4, 1)),
    ),
    0xcbef: CPUInstruction(
        name='SET 5,A',
        length=2,
        cycles=8,
        opcode=0xcbef,
        run=lambda r, m, o: setattr(r, 'a', set_bit(r.a, 5, 1)),
    ),
    0xcbf0: CPUInstruction(
        name='SET 6,B',
        length=2,
        cycles=8,
        opcode=0xcbf0,
        run=lambda r, m, o: setattr(r, 'b', set_bit(r.b, 6, 1)),
    ),
    0xcbf1: CPUInstruction(
        name='SET 6,C',
        length=2,
        cycles=8,
        opcode=0xcbf1,
        run=lambda r, m, o: setattr(r, 'c', set_bit(r.c, 6, 1)),
    ),
    0xcbf2: CPUInstruction(
        name='SET 6,D',
        length=2,
        cycles=8,
        opcode=0xcbf2,
        run=lambda r, m, o: setattr(r, 'd', set_bit(r.d, 6, 1)),
    ),
    0xcbf3: CPUInstruction(
        name='SET 6,E',
        length=2,
        cycles=8,
        opcode=0xcbf3,
        run=lambda r, m, o: setattr(r, 'e', set_bit(r.e, 6, 1)),
    ),
    0xcbf4: CPUInstruction(
        name='SET 6,H',
        length=2,
        cycles=8,
        opcode=0xcbf4,
        run=lambda r, m, o: setattr(r, 'h', set_bit(r.h, 6, 1)),
    ),
    0xcbf5: CPUInstruction(
        name='SET 6,L',
        length=2,
        cycles=8,
        opcode=0xcbf5,
        run=lambda r, m, o: setattr(r, 'l', set_bit(r.l, 6, 1)),
    ),
    0xcbf6: CPUInstruction(
        name='SET 6,(HL)',
        length=2,
        cycles=16,
        opcode=0xcbf6,
        run=lambda r, m, o: m.write(r.hl, set_bit(m.read(r.hl), 4, 1)),
    ),
    0xcbf7: CPUInstruction(
        name='SET 6,A',
        length=2,
        cycles=8,
        opcode=0xcbf7,
        run=lambda r, m, o: setattr(r, 'a', set_bit(r.a, 6, 1)),
    ),
    0xcbf8: CPUInstruction(
        name='SET 7,B',
        length=2,
        cycles=8,
        opcode=0xcbf8,
        run=lambda r, m, o: setattr(r, 'b', set_bit(r.b, 7, 1)),
    ),
    0xcbf9: CPUInstruction(
        name='SET 7,C',
        length=2,
        cycles=8,
        opcode=0xcbf9,
        run=lambda r, m, o: setattr(r, 'c', set_bit(r.c, 7, 1)),
    ),
    0xcbfa: CPUInstruction(
        name='SET 7,D',
        length=2,
        cycles=8,
        opcode=0xcbfa,
        run=lambda r, m, o: setattr(r, 'd', set_bit(r.d, 7, 1)),
    ),
    0xcbfb: CPUInstruction(
        name='SET 7,E',
        length=2,
        cycles=8,
        opcode=0xcbfb,
        run=lambda r, m, o: setattr(r, 'e', set_bit(r.e, 7, 1)),
    ),
    0xcbfc: CPUInstruction(
        name='SET 7,H',
        length=2,
        cycles=8,
        opcode=0xcbfc,
        run=lambda r, m, o: setattr(r, 'h', set_bit(r.h, 7, 1)),
    ),
    0xcbfd: CPUInstruction(
        name='SET 7,L',
        length=2,
        cycles=8,
        opcode=0xcbfd,
        run=lambda r, m, o: setattr(r, 'l', set_bit(r.l, 7, 1)),
    ),
    0xcbfe: CPUInstruction(
        name='SET 7,(HL)',
        length=2,
        cycles=16,
        opcode=0xcbfe,
        run=lambda r, m, o: m.write(r.hl, set_bit(m.read(r.hl), 4, 1)),
    ),
    0xcbff: CPUInstruction(
        name='SET 7,A',
        length=2,
        cycles=8,
        opcode=0xcbff,
        run=lambda r, m, o: setattr(r, 'a', set_bit(r.a, 7, 1)),
    ),
}
