from cpu.instruction import CPUInstruction
from cpu.registers import Register
from cpu.registers import Registers
from mmu.memory import Memory
from utils.bit_operations import get_bit
from utils.bit_operations import read_signed


def set_register(register: Register, value: int) -> None:
    register.value = value & 0xff


def set_hl(registers: Registers, value: int) -> None:
    registers.hl = value & 0xffff


def write_mem_dec_hl(registers: Registers, memory: Memory, value: int) -> None:
    memory.write(registers.hl, value)
    registers.hl -= 1


def xor(registers: Registers, lhs: int, rhs: int) -> None:
    result = lhs ^ rhs
    registers.a.value = lhs ^ rhs
    registers.z_flag = result == 0
    registers.n_flag = False
    registers.h_flag = False
    registers.c_flag = False


def test_bit(registers: Registers, byte: int, bit_position: int) -> None:
    is_set = get_bit(byte, bit_position)
    registers.z_flag = not is_set
    registers.n_flag = False
    registers.h_flag = True


def inc_c(registers: Registers) -> None:
    result = (registers.c.value + 1) & 0xff
    registers.z_flag = result == 0
    registers.n_flag = False
    registers.h_flag = (0x0f & result) < (0x0f & registers.c.value)
    registers.c.value = result


def jump_nz(registers: Registers, value: int) -> None:
    if not registers.z_flag:
        offset = read_signed(value)
        registers.pc.value += offset


def noop(*args) -> None:
    pass


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
        opcode=0x01
    ),
    0x02: CPUInstruction(
        name='LD (BC),A',
        length=1,
        cycles=8,
        opcode=0x02
    ),
    0x03: CPUInstruction(
        name='INC BC',
        length=1,
        cycles=8,
        opcode=0x03
    ),
    0x04: CPUInstruction(
        name='INC B',
        length=1,
        cycles=4,
        opcode=0x04
    ),
    0x05: CPUInstruction(
        name='DEC B',
        length=1,
        cycles=4,
        opcode=0x05
    ),
    0x06: CPUInstruction(
        name='LD B,u8',
        length=2,
        cycles=8,
        opcode=0x06
    ),
    0x07: CPUInstruction(
        name='RLCA',
        length=1,
        cycles=4,
        opcode=0x07
    ),
    0x08: CPUInstruction(
        name='LD (u16),SP',
        length=3,
        cycles=20,
        opcode=0x08
    ),
    0x09: CPUInstruction(
        name='ADD HL,BC',
        length=1,
        cycles=8,
        opcode=0x09
    ),
    0x0a: CPUInstruction(
        name='LD A,(BC)',
        length=1,
        cycles=8,
        opcode=0x0a
    ),
    0x0b: CPUInstruction(
        name='DEC BC',
        length=1,
        cycles=8,
        opcode=0x0b
    ),
    0x0c: CPUInstruction(
        name='INC C',
        length=1,
        cycles=4,
        opcode=0x0c,
        run=lambda r, m, o: inc_c(r),
    ),
    0x0d: CPUInstruction(
        name='DEC C',
        length=1,
        cycles=4,
        opcode=0x0d
    ),
    0x0e: CPUInstruction(
        name='LD C,u8',
        length=2,
        cycles=8,
        opcode=0x0e,
        run=lambda r, m, o: set_register(r.c, o.to_word()),
    ),
    0x0f: CPUInstruction(
        name='RRCA',
        length=1,
        cycles=4,
        opcode=0x0f
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
        opcode=0x11
    ),
    0x12: CPUInstruction(
        name='LD (DE),A',
        length=1,
        cycles=8,
        opcode=0x12
    ),
    0x13: CPUInstruction(
        name='INC DE',
        length=1,
        cycles=8,
        opcode=0x13
    ),
    0x14: CPUInstruction(
        name='INC D',
        length=1,
        cycles=4,
        opcode=0x14
    ),
    0x15: CPUInstruction(
        name='DEC D',
        length=1,
        cycles=4,
        opcode=0x15
    ),
    0x16: CPUInstruction(
        name='LD D,u8',
        length=2,
        cycles=8,
        opcode=0x16
    ),
    0x17: CPUInstruction(
        name='RLA',
        length=1,
        cycles=4,
        opcode=0x17
    ),
    0x18: CPUInstruction(
        name='JR i8',
        length=2,
        cycles=12,
        opcode=0x18
    ),
    0x19: CPUInstruction(
        name='ADD HL,DE',
        length=1,
        cycles=8,
        opcode=0x19
    ),
    0x1a: CPUInstruction(
        name='LD A,(DE)',
        length=1,
        cycles=8,
        opcode=0x1a
    ),
    0x1b: CPUInstruction(
        name='DEC DE',
        length=1,
        cycles=8,
        opcode=0x1b
    ),
    0x1c: CPUInstruction(
        name='INC E',
        length=1,
        cycles=4,
        opcode=0x1c
    ),
    0x1d: CPUInstruction(
        name='DEC E',
        length=1,
        cycles=4,
        opcode=0x1d
    ),
    0x1e: CPUInstruction(
        name='LD E,u8',
        length=2,
        cycles=8,
        opcode=0x1e
    ),
    0x1f: CPUInstruction(
        name='RRA',
        length=1,
        cycles=4,
        opcode=0x1f
    ),
    0x20: CPUInstruction(
        name='JR NZ,i8',
        length=2,
        cycles=8,
        opcode=0x20,
        run=lambda r, m, o: jump_nz(r, o.to_word())
    ),
    0x21: CPUInstruction(
        name='LD HL,u16',
        length=3,
        cycles=12,
        opcode=0x21,
        run=lambda r, m, o: set_hl(r, o.to_dword()),
),
    0x22: CPUInstruction(
        name='LD (HL+),A',
        length=1,
        cycles=8,
        opcode=0x22
    ),
    0x23: CPUInstruction(
        name='INC HL',
        length=1,
        cycles=8,
        opcode=0x23
    ),
    0x24: CPUInstruction(
        name='INC H',
        length=1,
        cycles=4,
        opcode=0x24
    ),
    0x25: CPUInstruction(
        name='DEC H',
        length=1,
        cycles=4,
        opcode=0x25
    ),
    0x26: CPUInstruction(
        name='LD H,u8',
        length=2,
        cycles=8,
        opcode=0x26
    ),
    0x27: CPUInstruction(
        name='DAA',
        length=1,
        cycles=4,
        opcode=0x27
    ),
    0x28: CPUInstruction(
        name='JR Z,i8',
        length=2,
        cycles=8,
        opcode=0x28
    ),
    0x29: CPUInstruction(
        name='ADD HL,HL',
        length=1,
        cycles=8,
        opcode=0x29
    ),
    0x2a: CPUInstruction(
        name='LD A,(HL+)',
        length=1,
        cycles=8,
        opcode=0x2a
    ),
    0x2b: CPUInstruction(
        name='DEC HL',
        length=1,
        cycles=8,
        opcode=0x2b
    ),
    0x2c: CPUInstruction(
        name='INC L',
        length=1,
        cycles=4,
        opcode=0x2c
    ),
    0x2d: CPUInstruction(
        name='DEC L',
        length=1,
        cycles=4,
        opcode=0x2d
    ),
    0x2e: CPUInstruction(
        name='LD L,u8',
        length=2,
        cycles=8,
        opcode=0x2e
    ),
    0x2f: CPUInstruction(
        name='CPL',
        length=1,
        cycles=4,
        opcode=0x2f
    ),
    0x30: CPUInstruction(
        name='JR NC,i8',
        length=2,
        cycles=8,
        opcode=0x30
    ),
    0x31: CPUInstruction(
        name='LD SP,u16',
        length=3,
        cycles=12,
        opcode=0x31,
        run=lambda r, m, o: set_register(r.sp, o.to_dword()),
    ),
    0x32: CPUInstruction(
        name='LD (HL-),A',
        length=1,
        cycles=8,
        opcode=0x32,
        run=lambda r, m, o: write_mem_dec_hl(r, m, r.a.value),
    ),
    0x33: CPUInstruction(
        name='INC SP',
        length=1,
        cycles=8,
        opcode=0x33
    ),
    0x34: CPUInstruction(
        name='INC (HL)',
        length=1,
        cycles=12,
        opcode=0x34
    ),
    0x35: CPUInstruction(
        name='DEC (HL)',
        length=1,
        cycles=12,
        opcode=0x35
    ),
    0x36: CPUInstruction(
        name='LD (HL),u8',
        length=2,
        cycles=12,
        opcode=0x36
    ),
    0x37: CPUInstruction(
        name='SCF',
        length=1,
        cycles=4,
        opcode=0x37
    ),
    0x38: CPUInstruction(
        name='JR C,i8',
        length=2,
        cycles=8,
        opcode=0x38
    ),
    0x39: CPUInstruction(
        name='ADD HL,SP',
        length=1,
        cycles=8,
        opcode=0x39
    ),
    0x3a: CPUInstruction(
        name='LD A,(HL-)',
        length=1,
        cycles=8,
        opcode=0x3a
    ),
    0x3b: CPUInstruction(
        name='DEC SP',
        length=1,
        cycles=8,
        opcode=0x3b
    ),
    0x3c: CPUInstruction(
        name='INC A',
        length=1,
        cycles=4,
        opcode=0x3c
    ),
    0x3d: CPUInstruction(
        name='DEC A',
        length=1,
        cycles=4,
        opcode=0x3d
    ),
    0x3e: CPUInstruction(
        name='LD A,u8',
        length=2,
        cycles=8,
        opcode=0x3e,
        run=lambda r, m, o: set_register(r.a, o.to_word()),
    ),
    0x3f: CPUInstruction(
        name='CCF',
        length=1,
        cycles=4,
        opcode=0x3f
    ),
    0x40: CPUInstruction(
        name='LD B,B',
        length=1,
        cycles=4,
        opcode=0x40
    ),
    0x41: CPUInstruction(
        name='LD B,C',
        length=1,
        cycles=4,
        opcode=0x41
    ),
    0x42: CPUInstruction(
        name='LD B,D',
        length=1,
        cycles=4,
        opcode=0x42
    ),
    0x43: CPUInstruction(
        name='LD B,E',
        length=1,
        cycles=4,
        opcode=0x43
    ),
    0x44: CPUInstruction(
        name='LD B,H',
        length=1,
        cycles=4,
        opcode=0x44
    ),
    0x45: CPUInstruction(
        name='LD B,L',
        length=1,
        cycles=4,
        opcode=0x45
    ),
    0x46: CPUInstruction(
        name='LD B,(HL)',
        length=1,
        cycles=8,
        opcode=0x46
    ),
    0x47: CPUInstruction(
        name='LD B,A',
        length=1,
        cycles=4,
        opcode=0x47
    ),
    0x48: CPUInstruction(
        name='LD C,B',
        length=1,
        cycles=4,
        opcode=0x48
    ),
    0x49: CPUInstruction(
        name='LD C,C',
        length=1,
        cycles=4,
        opcode=0x49
    ),
    0x4a: CPUInstruction(
        name='LD C,D',
        length=1,
        cycles=4,
        opcode=0x4a
    ),
    0x4b: CPUInstruction(
        name='LD C,E',
        length=1,
        cycles=4,
        opcode=0x4b
    ),
    0x4c: CPUInstruction(
        name='LD C,H',
        length=1,
        cycles=4,
        opcode=0x4c
    ),
    0x4d: CPUInstruction(
        name='LD C,L',
        length=1,
        cycles=4,
        opcode=0x4d
    ),
    0x4e: CPUInstruction(
        name='LD C,(HL)',
        length=1,
        cycles=8,
        opcode=0x4e
    ),
    0x4f: CPUInstruction(
        name='LD C,A',
        length=1,
        cycles=4,
        opcode=0x4f
    ),
    0x50: CPUInstruction(
        name='LD D,B',
        length=1,
        cycles=4,
        opcode=0x50
    ),
    0x51: CPUInstruction(
        name='LD D,C',
        length=1,
        cycles=4,
        opcode=0x51
    ),
    0x52: CPUInstruction(
        name='LD D,D',
        length=1,
        cycles=4,
        opcode=0x52
    ),
    0x53: CPUInstruction(
        name='LD D,E',
        length=1,
        cycles=4,
        opcode=0x53
    ),
    0x54: CPUInstruction(
        name='LD D,H',
        length=1,
        cycles=4,
        opcode=0x54
    ),
    0x55: CPUInstruction(
        name='LD D,L',
        length=1,
        cycles=4,
        opcode=0x55
    ),
    0x56: CPUInstruction(
        name='LD D,(HL)',
        length=1,
        cycles=8,
        opcode=0x56
    ),
    0x57: CPUInstruction(
        name='LD D,A',
        length=1,
        cycles=4,
        opcode=0x57
    ),
    0x58: CPUInstruction(
        name='LD E,B',
        length=1,
        cycles=4,
        opcode=0x58
    ),
    0x59: CPUInstruction(
        name='LD E,C',
        length=1,
        cycles=4,
        opcode=0x59
    ),
    0x5a: CPUInstruction(
        name='LD E,D',
        length=1,
        cycles=4,
        opcode=0x5a
    ),
    0x5b: CPUInstruction(
        name='LD E,E',
        length=1,
        cycles=4,
        opcode=0x5b
    ),
    0x5c: CPUInstruction(
        name='LD E,H',
        length=1,
        cycles=4,
        opcode=0x5c
    ),
    0x5d: CPUInstruction(
        name='LD E,L',
        length=1,
        cycles=4,
        opcode=0x5d
    ),
    0x5e: CPUInstruction(
        name='LD E,(HL)',
        length=1,
        cycles=8,
        opcode=0x5e
    ),
    0x5f: CPUInstruction(
        name='LD E,A',
        length=1,
        cycles=4,
        opcode=0x5f
    ),
    0x60: CPUInstruction(
        name='LD H,B',
        length=1,
        cycles=4,
        opcode=0x60
    ),
    0x61: CPUInstruction(
        name='LD H,C',
        length=1,
        cycles=4,
        opcode=0x61
    ),
    0x62: CPUInstruction(
        name='LD H,D',
        length=1,
        cycles=4,
        opcode=0x62
    ),
    0x63: CPUInstruction(
        name='LD H,E',
        length=1,
        cycles=4,
        opcode=0x63
    ),
    0x64: CPUInstruction(
        name='LD H,H',
        length=1,
        cycles=4,
        opcode=0x64
    ),
    0x65: CPUInstruction(
        name='LD H,L',
        length=1,
        cycles=4,
        opcode=0x65
    ),
    0x66: CPUInstruction(
        name='LD H,(HL)',
        length=1,
        cycles=8,
        opcode=0x66
    ),
    0x67: CPUInstruction(
        name='LD H,A',
        length=1,
        cycles=4,
        opcode=0x67
    ),
    0x68: CPUInstruction(
        name='LD L,B',
        length=1,
        cycles=4,
        opcode=0x68
    ),
    0x69: CPUInstruction(
        name='LD L,C',
        length=1,
        cycles=4,
        opcode=0x69
    ),
    0x6a: CPUInstruction(
        name='LD L,D',
        length=1,
        cycles=4,
        opcode=0x6a
    ),
    0x6b: CPUInstruction(
        name='LD L,E',
        length=1,
        cycles=4,
        opcode=0x6b
    ),
    0x6c: CPUInstruction(
        name='LD L,H',
        length=1,
        cycles=4,
        opcode=0x6c
    ),
    0x6d: CPUInstruction(
        name='LD L,L',
        length=1,
        cycles=4,
        opcode=0x6d
    ),
    0x6e: CPUInstruction(
        name='LD L,(HL)',
        length=1,
        cycles=8,
        opcode=0x6e
    ),
    0x6f: CPUInstruction(
        name='LD L,A',
        length=1,
        cycles=4,
        opcode=0x6f
    ),
    0x70: CPUInstruction(
        name='LD (HL),B',
        length=1,
        cycles=8,
        opcode=0x70
    ),
    0x71: CPUInstruction(
        name='LD (HL),C',
        length=1,
        cycles=8,
        opcode=0x71
    ),
    0x72: CPUInstruction(
        name='LD (HL),D',
        length=1,
        cycles=8,
        opcode=0x72
    ),
    0x73: CPUInstruction(
        name='LD (HL),E',
        length=1,
        cycles=8,
        opcode=0x73
    ),
    0x74: CPUInstruction(
        name='LD (HL),H',
        length=1,
        cycles=8,
        opcode=0x74
    ),
    0x75: CPUInstruction(
        name='LD (HL),L',
        length=1,
        cycles=8,
        opcode=0x75
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
        run=lambda r, m, o: m.write(r.hl, r.a.value),
    ),
    0x78: CPUInstruction(
        name='LD A,B',
        length=1,
        cycles=4,
        opcode=0x78
    ),
    0x79: CPUInstruction(
        name='LD A,C',
        length=1,
        cycles=4,
        opcode=0x79
    ),
    0x7a: CPUInstruction(
        name='LD A,D',
        length=1,
        cycles=4,
        opcode=0x7a
    ),
    0x7b: CPUInstruction(
        name='LD A,E',
        length=1,
        cycles=4,
        opcode=0x7b
    ),
    0x7c: CPUInstruction(
        name='LD A,H',
        length=1,
        cycles=4,
        opcode=0x7c
    ),
    0x7d: CPUInstruction(
        name='LD A,L',
        length=1,
        cycles=4,
        opcode=0x7d
    ),
    0x7e: CPUInstruction(
        name='LD A,(HL)',
        length=1,
        cycles=8,
        opcode=0x7e
    ),
    0x7f: CPUInstruction(
        name='LD A,A',
        length=1,
        cycles=4,
        opcode=0x7f
    ),
    0x80: CPUInstruction(
        name='ADD A,B',
        length=1,
        cycles=4,
        opcode=0x80
    ),
    0x81: CPUInstruction(
        name='ADD A,C',
        length=1,
        cycles=4,
        opcode=0x81
    ),
    0x82: CPUInstruction(
        name='ADD A,D',
        length=1,
        cycles=4,
        opcode=0x82
    ),
    0x83: CPUInstruction(
        name='ADD A,E',
        length=1,
        cycles=4,
        opcode=0x83
    ),
    0x84: CPUInstruction(
        name='ADD A,H',
        length=1,
        cycles=4,
        opcode=0x84
    ),
    0x85: CPUInstruction(
        name='ADD A,L',
        length=1,
        cycles=4,
        opcode=0x85
    ),
    0x86: CPUInstruction(
        name='ADD A,(HL)',
        length=1,
        cycles=8,
        opcode=0x86
    ),
    0x87: CPUInstruction(
        name='ADD A,A',
        length=1,
        cycles=4,
        opcode=0x87
    ),
    0x88: CPUInstruction(
        name='ADC A,B',
        length=1,
        cycles=4,
        opcode=0x88
    ),
    0x89: CPUInstruction(
        name='ADC A,C',
        length=1,
        cycles=4,
        opcode=0x89
    ),
    0x8a: CPUInstruction(
        name='ADC A,D',
        length=1,
        cycles=4,
        opcode=0x8a
    ),
    0x8b: CPUInstruction(
        name='ADC A,E',
        length=1,
        cycles=4,
        opcode=0x8b
    ),
    0x8c: CPUInstruction(
        name='ADC A,H',
        length=1,
        cycles=4,
        opcode=0x8c
    ),
    0x8d: CPUInstruction(
        name='ADC A,L',
        length=1,
        cycles=4,
        opcode=0x8d
    ),
    0x8e: CPUInstruction(
        name='ADC A,(HL)',
        length=1,
        cycles=8,
        opcode=0x8e
    ),
    0x8f: CPUInstruction(
        name='ADC A,A',
        length=1,
        cycles=4,
        opcode=0x8f
    ),
    0x90: CPUInstruction(
        name='SUB A,B',
        length=1,
        cycles=4,
        opcode=0x90
    ),
    0x91: CPUInstruction(
        name='SUB A,C',
        length=1,
        cycles=4,
        opcode=0x91
    ),
    0x92: CPUInstruction(
        name='SUB A,D',
        length=1,
        cycles=4,
        opcode=0x92
    ),
    0x93: CPUInstruction(
        name='SUB A,E',
        length=1,
        cycles=4,
        opcode=0x93
    ),
    0x94: CPUInstruction(
        name='SUB A,H',
        length=1,
        cycles=4,
        opcode=0x94
    ),
    0x95: CPUInstruction(
        name='SUB A,L',
        length=1,
        cycles=4,
        opcode=0x95
    ),
    0x96: CPUInstruction(
        name='SUB A,(HL)',
        length=1,
        cycles=8,
        opcode=0x96
    ),
    0x97: CPUInstruction(
        name='SUB A,A',
        length=1,
        cycles=4,
        opcode=0x97
    ),
    0x98: CPUInstruction(
        name='SBC A,B',
        length=1,
        cycles=4,
        opcode=0x98
    ),
    0x99: CPUInstruction(
        name='SBC A,C',
        length=1,
        cycles=4,
        opcode=0x99
    ),
    0x9a: CPUInstruction(
        name='SBC A,D',
        length=1,
        cycles=4,
        opcode=0x9a
    ),
    0x9b: CPUInstruction(
        name='SBC A,E',
        length=1,
        cycles=4,
        opcode=0x9b
    ),
    0x9c: CPUInstruction(
        name='SBC A,H',
        length=1,
        cycles=4,
        opcode=0x9c
    ),
    0x9d: CPUInstruction(
        name='SBC A,L',
        length=1,
        cycles=4,
        opcode=0x9d
    ),
    0x9e: CPUInstruction(
        name='SBC A,(HL)',
        length=1,
        cycles=8,
        opcode=0x9e
    ),
    0x9f: CPUInstruction(
        name='SBC A,A',
        length=1,
        cycles=4,
        opcode=0x9f
    ),
    0xa0: CPUInstruction(
        name='AND A,B',
        length=1,
        cycles=4,
        opcode=0xa0
    ),
    0xa1: CPUInstruction(
        name='AND A,C',
        length=1,
        cycles=4,
        opcode=0xa1
    ),
    0xa2: CPUInstruction(
        name='AND A,D',
        length=1,
        cycles=4,
        opcode=0xa2
    ),
    0xa3: CPUInstruction(
        name='AND A,E',
        length=1,
        cycles=4,
        opcode=0xa3
    ),
    0xa4: CPUInstruction(
        name='AND A,H',
        length=1,
        cycles=4,
        opcode=0xa4
    ),
    0xa5: CPUInstruction(
        name='AND A,L',
        length=1,
        cycles=4,
        opcode=0xa5
    ),
    0xa6: CPUInstruction(
        name='AND A,(HL)',
        length=1,
        cycles=8,
        opcode=0xa6
    ),
    0xa7: CPUInstruction(
        name='AND A,A',
        length=1,
        cycles=4,
        opcode=0xa7
    ),
    0xa8: CPUInstruction(
        name='XOR A,B',
        length=1,
        cycles=4,
        opcode=0xa8
    ),
    0xa9: CPUInstruction(
        name='XOR A,C',
        length=1,
        cycles=4,
        opcode=0xa9
    ),
    0xaa: CPUInstruction(
        name='XOR A,D',
        length=1,
        cycles=4,
        opcode=0xaa
    ),
    0xab: CPUInstruction(
        name='XOR A,E',
        length=1,
        cycles=4,
        opcode=0xab
    ),
    0xac: CPUInstruction(
        name='XOR A,H',
        length=1,
        cycles=4,
        opcode=0xac
    ),
    0xad: CPUInstruction(
        name='XOR A,L',
        length=1,
        cycles=4,
        opcode=0xad
    ),
    0xae: CPUInstruction(
        name='XOR A,(HL)',
        length=1,
        cycles=8,
        opcode=0xae
    ),
    0xaf: CPUInstruction(
        name='XOR A,A',
        length=1,
        cycles=4,
        opcode=0xaf,
        run=lambda r, m, o: xor(r, r.a.value, r.a.value),
    ),
    0xb0: CPUInstruction(
        name='OR A,B',
        length=1,
        cycles=4,
        opcode=0xb0
    ),
    0xb1: CPUInstruction(
        name='OR A,C',
        length=1,
        cycles=4,
        opcode=0xb1
    ),
    0xb2: CPUInstruction(
        name='OR A,D',
        length=1,
        cycles=4,
        opcode=0xb2
    ),
    0xb3: CPUInstruction(
        name='OR A,E',
        length=1,
        cycles=4,
        opcode=0xb3
    ),
    0xb4: CPUInstruction(
        name='OR A,H',
        length=1,
        cycles=4,
        opcode=0xb4
    ),
    0xb5: CPUInstruction(
        name='OR A,L',
        length=1,
        cycles=4,
        opcode=0xb5
    ),
    0xb6: CPUInstruction(
        name='OR A,(HL)',
        length=1,
        cycles=8,
        opcode=0xb6
    ),
    0xb7: CPUInstruction(
        name='OR A,A',
        length=1,
        cycles=4,
        opcode=0xb7
    ),
    0xb8: CPUInstruction(
        name='CP A,B',
        length=1,
        cycles=4,
        opcode=0xb8
    ),
    0xb9: CPUInstruction(
        name='CP A,C',
        length=1,
        cycles=4,
        opcode=0xb9
    ),
    0xba: CPUInstruction(
        name='CP A,D',
        length=1,
        cycles=4,
        opcode=0xba
    ),
    0xbb: CPUInstruction(
        name='CP A,E',
        length=1,
        cycles=4,
        opcode=0xbb
    ),
    0xbc: CPUInstruction(
        name='CP A,H',
        length=1,
        cycles=4,
        opcode=0xbc
    ),
    0xbd: CPUInstruction(
        name='CP A,L',
        length=1,
        cycles=4,
        opcode=0xbd
    ),
    0xbe: CPUInstruction(
        name='CP A,(HL)',
        length=1,
        cycles=8,
        opcode=0xbe
    ),
    0xbf: CPUInstruction(
        name='CP A,A',
        length=1,
        cycles=4,
        opcode=0xbf
    ),
    0xc0: CPUInstruction(
        name='RET NZ',
        length=1,
        cycles=8,
        opcode=0xc0
    ),
    0xc1: CPUInstruction(
        name='POP BC',
        length=1,
        cycles=12,
        opcode=0xc1
    ),
    0xc2: CPUInstruction(
        name='JP NZ,u16',
        length=3,
        cycles=12,
        opcode=0xc2
    ),
    0xc3: CPUInstruction(
        name='JP u16',
        length=3,
        cycles=16,
        opcode=0xc3
    ),
    0xc4: CPUInstruction(
        name='CALL NZ,u16',
        length=3,
        cycles=12,
        opcode=0xc4
    ),
    0xc5: CPUInstruction(
        name='PUSH BC',
        length=1,
        cycles=16,
        opcode=0xc5
    ),
    0xc6: CPUInstruction(
        name='ADD A,u8',
        length=2,
        cycles=8,
        opcode=0xc6
    ),
    0xc7: CPUInstruction(
        name='RST 00h',
        length=1,
        cycles=16,
        opcode=0xc7
    ),
    0xc8: CPUInstruction(
        name='RET Z',
        length=1,
        cycles=8,
        opcode=0xc8
    ),
    0xc9: CPUInstruction(
        name='RET',
        length=1,
        cycles=16,
        opcode=0xc9
    ),
    0xca: CPUInstruction(
        name='JP Z,u16',
        length=3,
        cycles=12,
        opcode=0xca
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
        opcode=0xcc
    ),
    0xcd: CPUInstruction(
        name='CALL u16',
        length=3,
        cycles=24,
        opcode=0xcd
    ),
    0xce: CPUInstruction(
        name='ADC A,u8',
        length=2,
        cycles=8,
        opcode=0xce
    ),
    0xcf: CPUInstruction(
        name='RST 08h',
        length=1,
        cycles=16,
        opcode=0xcf
    ),
    0xd0: CPUInstruction(
        name='RET NC',
        length=1,
        cycles=8,
        opcode=0xd0
    ),
    0xd1: CPUInstruction(
        name='POP DE',
        length=1,
        cycles=12,
        opcode=0xd1
    ),
    0xd2: CPUInstruction(
        name='JP NC,u16',
        length=3,
        cycles=12,
        opcode=0xd2
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
        opcode=0xd4
    ),
    0xd5: CPUInstruction(
        name='PUSH DE',
        length=1,
        cycles=16,
        opcode=0xd5
    ),
    0xd6: CPUInstruction(
        name='SUB A,u8',
        length=2,
        cycles=8,
        opcode=0xd6
    ),
    0xd7: CPUInstruction(
        name='RST 10h',
        length=1,
        cycles=16,
        opcode=0xd7
    ),
    0xd8: CPUInstruction(
        name='RET C',
        length=1,
        cycles=8,
        opcode=0xd8
    ),
    0xd9: CPUInstruction(
        name='RETI',
        length=1,
        cycles=16,
        opcode=0xd9
    ),
    0xda: CPUInstruction(
        name='JP C,u16',
        length=3,
        cycles=12,
        opcode=0xda
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
        opcode=0xdc
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
        opcode=0xde
    ),
    0xdf: CPUInstruction(
        name='RST 18h',
        length=1,
        cycles=16,
        opcode=0xdf
    ),
    0xe0: CPUInstruction(
        name='LD (FF00+u8),A',
        length=2,
        cycles=12,
        opcode=0xe0,
        run=lambda r, m, o: m.write(0xff00 + o.to_word(), r.a.value),
    ),
    0xe1: CPUInstruction(
        name='POP HL',
        length=1,
        cycles=12,
        opcode=0xe1
    ),
    0xe2: CPUInstruction(
        name='LD (FF00+C),A',
        length=1,
        cycles=8,
        opcode=0xe2,
        run=lambda r, m, o: m.write(0xff00 + r.c.value, r.a.value),
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
        opcode=0xe5
    ),
    0xe6: CPUInstruction(
        name='AND A,u8',
        length=2,
        cycles=8,
        opcode=0xe6
    ),
    0xe7: CPUInstruction(
        name='RST 20h',
        length=1,
        cycles=16,
        opcode=0xe7
    ),
    0xe8: CPUInstruction(
        name='ADD SP,i8',
        length=2,
        cycles=16,
        opcode=0xe8
    ),
    0xe9: CPUInstruction(
        name='JP HL',
        length=1,
        cycles=4,
        opcode=0xe9
    ),
    0xea: CPUInstruction(
        name='LD (u16),A',
        length=3,
        cycles=16,
        opcode=0xea
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
        opcode=0xee
    ),
    0xef: CPUInstruction(
        name='RST 28h',
        length=1,
        cycles=16,
        opcode=0xef
    ),
    0xf0: CPUInstruction(
        name='LD A,(FF00+u8)',
        length=2,
        cycles=12,
        opcode=0xf0
    ),
    0xf1: CPUInstruction(
        name='POP AF',
        length=1,
        cycles=12,
        opcode=0xf1
    ),
    0xf2: CPUInstruction(
        name='LD A,(FF00+C)',
        length=1,
        cycles=8,
        opcode=0xf2
    ),
    0xf3: CPUInstruction(
        name='DI',
        length=1,
        cycles=4,
        opcode=0xf3
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
        opcode=0xf5
    ),
    0xf6: CPUInstruction(
        name='OR A,u8',
        length=2,
        cycles=8,
        opcode=0xf6
    ),
    0xf7: CPUInstruction(
        name='RST 30h',
        length=1,
        cycles=16,
        opcode=0xf7
    ),
    0xf8: CPUInstruction(
        name='LD HL,SP+i8',
        length=2,
        cycles=12,
        opcode=0xf8
    ),
    0xf9: CPUInstruction(
        name='LD SP,HL',
        length=1,
        cycles=8,
        opcode=0xf9
    ),
    0xfa: CPUInstruction(
        name='LD A,(u16)',
        length=3,
        cycles=16,
        opcode=0xfa
    ),
    0xfb: CPUInstruction(
        name='EI',
        length=1,
        cycles=4,
        opcode=0xfb
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
        opcode=0xfe
    ),
    0xff: CPUInstruction(
        name='RST 38h',
        length=1,
        cycles=16,
        opcode=0xff
    ),
    0xcb00: CPUInstruction(
        name='RLC B',
        length=2,
        cycles=8,
        opcode=0xcb00
    ),
    0xcb01: CPUInstruction(
        name='RLC C',
        length=2,
        cycles=8,
        opcode=0xcb01
    ),
    0xcb02: CPUInstruction(
        name='RLC D',
        length=2,
        cycles=8,
        opcode=0xcb02
    ),
    0xcb03: CPUInstruction(
        name='RLC E',
        length=2,
        cycles=8,
        opcode=0xcb03
    ),
    0xcb04: CPUInstruction(
        name='RLC H',
        length=2,
        cycles=8,
        opcode=0xcb04
    ),
    0xcb05: CPUInstruction(
        name='RLC L',
        length=2,
        cycles=8,
        opcode=0xcb05
    ),
    0xcb06: CPUInstruction(
        name='RLC (HL)',
        length=2,
        cycles=16,
        opcode=0xcb06
    ),
    0xcb07: CPUInstruction(
        name='RLC A',
        length=2,
        cycles=8,
        opcode=0xcb07
    ),
    0xcb08: CPUInstruction(
        name='RRC B',
        length=2,
        cycles=8,
        opcode=0xcb08
    ),
    0xcb09: CPUInstruction(
        name='RRC C',
        length=2,
        cycles=8,
        opcode=0xcb09
    ),
    0xcb0a: CPUInstruction(
        name='RRC D',
        length=2,
        cycles=8,
        opcode=0xcb0a
    ),
    0xcb0b: CPUInstruction(
        name='RRC E',
        length=2,
        cycles=8,
        opcode=0xcb0b
    ),
    0xcb0c: CPUInstruction(
        name='RRC H',
        length=2,
        cycles=8,
        opcode=0xcb0c
    ),
    0xcb0d: CPUInstruction(
        name='RRC L',
        length=2,
        cycles=8,
        opcode=0xcb0d
    ),
    0xcb0e: CPUInstruction(
        name='RRC (HL)',
        length=2,
        cycles=16,
        opcode=0xcb0e
    ),
    0xcb0f: CPUInstruction(
        name='RRC A',
        length=2,
        cycles=8,
        opcode=0xcb0f
    ),
    0xcb10: CPUInstruction(
        name='RL B',
        length=2,
        cycles=8,
        opcode=0xcb10
    ),
    0xcb11: CPUInstruction(
        name='RL C',
        length=2,
        cycles=8,
        opcode=0xcb11
    ),
    0xcb12: CPUInstruction(
        name='RL D',
        length=2,
        cycles=8,
        opcode=0xcb12
    ),
    0xcb13: CPUInstruction(
        name='RL E',
        length=2,
        cycles=8,
        opcode=0xcb13
    ),
    0xcb14: CPUInstruction(
        name='RL H',
        length=2,
        cycles=8,
        opcode=0xcb14
    ),
    0xcb15: CPUInstruction(
        name='RL L',
        length=2,
        cycles=8,
        opcode=0xcb15
    ),
    0xcb16: CPUInstruction(
        name='RL (HL)',
        length=2,
        cycles=16,
        opcode=0xcb16
    ),
    0xcb17: CPUInstruction(
        name='RL A',
        length=2,
        cycles=8,
        opcode=0xcb17
    ),
    0xcb18: CPUInstruction(
        name='RR B',
        length=2,
        cycles=8,
        opcode=0xcb18
    ),
    0xcb19: CPUInstruction(
        name='RR C',
        length=2,
        cycles=8,
        opcode=0xcb19
    ),
    0xcb1a: CPUInstruction(
        name='RR D',
        length=2,
        cycles=8,
        opcode=0xcb1a
    ),
    0xcb1b: CPUInstruction(
        name='RR E',
        length=2,
        cycles=8,
        opcode=0xcb1b
    ),
    0xcb1c: CPUInstruction(
        name='RR H',
        length=2,
        cycles=8,
        opcode=0xcb1c
    ),
    0xcb1d: CPUInstruction(
        name='RR L',
        length=2,
        cycles=8,
        opcode=0xcb1d
    ),
    0xcb1e: CPUInstruction(
        name='RR (HL)',
        length=2,
        cycles=16,
        opcode=0xcb1e
    ),
    0xcb1f: CPUInstruction(
        name='RR A',
        length=2,
        cycles=8,
        opcode=0xcb1f
    ),
    0xcb20: CPUInstruction(
        name='SLA B',
        length=2,
        cycles=8,
        opcode=0xcb20
    ),
    0xcb21: CPUInstruction(
        name='SLA C',
        length=2,
        cycles=8,
        opcode=0xcb21
    ),
    0xcb22: CPUInstruction(
        name='SLA D',
        length=2,
        cycles=8,
        opcode=0xcb22
    ),
    0xcb23: CPUInstruction(
        name='SLA E',
        length=2,
        cycles=8,
        opcode=0xcb23
    ),
    0xcb24: CPUInstruction(
        name='SLA H',
        length=2,
        cycles=8,
        opcode=0xcb24
    ),
    0xcb25: CPUInstruction(
        name='SLA L',
        length=2,
        cycles=8,
        opcode=0xcb25
    ),
    0xcb26: CPUInstruction(
        name='SLA (HL)',
        length=2,
        cycles=16,
        opcode=0xcb26
    ),
    0xcb27: CPUInstruction(
        name='SLA A',
        length=2,
        cycles=8,
        opcode=0xcb27
    ),
    0xcb28: CPUInstruction(
        name='SRA B',
        length=2,
        cycles=8,
        opcode=0xcb28
    ),
    0xcb29: CPUInstruction(
        name='SRA C',
        length=2,
        cycles=8,
        opcode=0xcb29
    ),
    0xcb2a: CPUInstruction(
        name='SRA D',
        length=2,
        cycles=8,
        opcode=0xcb2a
    ),
    0xcb2b: CPUInstruction(
        name='SRA E',
        length=2,
        cycles=8,
        opcode=0xcb2b
    ),
    0xcb2c: CPUInstruction(
        name='SRA H',
        length=2,
        cycles=8,
        opcode=0xcb2c
    ),
    0xcb2d: CPUInstruction(
        name='SRA L',
        length=2,
        cycles=8,
        opcode=0xcb2d
    ),
    0xcb2e: CPUInstruction(
        name='SRA (HL)',
        length=2,
        cycles=16,
        opcode=0xcb2e
    ),
    0xcb2f: CPUInstruction(
        name='SRA A',
        length=2,
        cycles=8,
        opcode=0xcb2f
    ),
    0xcb30: CPUInstruction(
        name='SWAP B',
        length=2,
        cycles=8,
        opcode=0xcb30
    ),
    0xcb31: CPUInstruction(
        name='SWAP C',
        length=2,
        cycles=8,
        opcode=0xcb31
    ),
    0xcb32: CPUInstruction(
        name='SWAP D',
        length=2,
        cycles=8,
        opcode=0xcb32
    ),
    0xcb33: CPUInstruction(
        name='SWAP E',
        length=2,
        cycles=8,
        opcode=0xcb33
    ),
    0xcb34: CPUInstruction(
        name='SWAP H',
        length=2,
        cycles=8,
        opcode=0xcb34
    ),
    0xcb35: CPUInstruction(
        name='SWAP L',
        length=2,
        cycles=8,
        opcode=0xcb35
    ),
    0xcb36: CPUInstruction(
        name='SWAP (HL)',
        length=2,
        cycles=16,
        opcode=0xcb36
    ),
    0xcb37: CPUInstruction(
        name='SWAP A',
        length=2,
        cycles=8,
        opcode=0xcb37
    ),
    0xcb38: CPUInstruction(
        name='SRL B',
        length=2,
        cycles=8,
        opcode=0xcb38
    ),
    0xcb39: CPUInstruction(
        name='SRL C',
        length=2,
        cycles=8,
        opcode=0xcb39
    ),
    0xcb3a: CPUInstruction(
        name='SRL D',
        length=2,
        cycles=8,
        opcode=0xcb3a
    ),
    0xcb3b: CPUInstruction(
        name='SRL E',
        length=2,
        cycles=8,
        opcode=0xcb3b
    ),
    0xcb3c: CPUInstruction(
        name='SRL H',
        length=2,
        cycles=8,
        opcode=0xcb3c
    ),
    0xcb3d: CPUInstruction(
        name='SRL L',
        length=2,
        cycles=8,
        opcode=0xcb3d
    ),
    0xcb3e: CPUInstruction(
        name='SRL (HL)',
        length=2,
        cycles=16,
        opcode=0xcb3e
    ),
    0xcb3f: CPUInstruction(
        name='SRL A',
        length=2,
        cycles=8,
        opcode=0xcb3f
    ),
    0xcb40: CPUInstruction(
        name='BIT 0,B',
        length=2,
        cycles=8,
        opcode=0xcb40
    ),
    0xcb41: CPUInstruction(
        name='BIT 0,C',
        length=2,
        cycles=8,
        opcode=0xcb41
    ),
    0xcb42: CPUInstruction(
        name='BIT 0,D',
        length=2,
        cycles=8,
        opcode=0xcb42
    ),
    0xcb43: CPUInstruction(
        name='BIT 0,E',
        length=2,
        cycles=8,
        opcode=0xcb43
    ),
    0xcb44: CPUInstruction(
        name='BIT 0,H',
        length=2,
        cycles=8,
        opcode=0xcb44
    ),
    0xcb45: CPUInstruction(
        name='BIT 0,L',
        length=2,
        cycles=8,
        opcode=0xcb45
    ),
    0xcb46: CPUInstruction(
        name='BIT 0,(HL)',
        length=2,
        cycles=12,
        opcode=0xcb46
    ),
    0xcb47: CPUInstruction(
        name='BIT 0,A',
        length=2,
        cycles=8,
        opcode=0xcb47
    ),
    0xcb48: CPUInstruction(
        name='BIT 1,B',
        length=2,
        cycles=8,
        opcode=0xcb48
    ),
    0xcb49: CPUInstruction(
        name='BIT 1,C',
        length=2,
        cycles=8,
        opcode=0xcb49
    ),
    0xcb4a: CPUInstruction(
        name='BIT 1,D',
        length=2,
        cycles=8,
        opcode=0xcb4a
    ),
    0xcb4b: CPUInstruction(
        name='BIT 1,E',
        length=2,
        cycles=8,
        opcode=0xcb4b
    ),
    0xcb4c: CPUInstruction(
        name='BIT 1,H',
        length=2,
        cycles=8,
        opcode=0xcb4c
    ),
    0xcb4d: CPUInstruction(
        name='BIT 1,L',
        length=2,
        cycles=8,
        opcode=0xcb4d
    ),
    0xcb4e: CPUInstruction(
        name='BIT 1,(HL)',
        length=2,
        cycles=12,
        opcode=0xcb4e
    ),
    0xcb4f: CPUInstruction(
        name='BIT 1,A',
        length=2,
        cycles=8,
        opcode=0xcb4f
    ),
    0xcb50: CPUInstruction(
        name='BIT 2,B',
        length=2,
        cycles=8,
        opcode=0xcb50
    ),
    0xcb51: CPUInstruction(
        name='BIT 2,C',
        length=2,
        cycles=8,
        opcode=0xcb51
    ),
    0xcb52: CPUInstruction(
        name='BIT 2,D',
        length=2,
        cycles=8,
        opcode=0xcb52
    ),
    0xcb53: CPUInstruction(
        name='BIT 2,E',
        length=2,
        cycles=8,
        opcode=0xcb53
    ),
    0xcb54: CPUInstruction(
        name='BIT 2,H',
        length=2,
        cycles=8,
        opcode=0xcb54
    ),
    0xcb55: CPUInstruction(
        name='BIT 2,L',
        length=2,
        cycles=8,
        opcode=0xcb55
    ),
    0xcb56: CPUInstruction(
        name='BIT 2,(HL)',
        length=2,
        cycles=12,
        opcode=0xcb56
    ),
    0xcb57: CPUInstruction(
        name='BIT 2,A',
        length=2,
        cycles=8,
        opcode=0xcb57
    ),
    0xcb58: CPUInstruction(
        name='BIT 3,B',
        length=2,
        cycles=8,
        opcode=0xcb58
    ),
    0xcb59: CPUInstruction(
        name='BIT 3,C',
        length=2,
        cycles=8,
        opcode=0xcb59
    ),
    0xcb5a: CPUInstruction(
        name='BIT 3,D',
        length=2,
        cycles=8,
        opcode=0xcb5a
    ),
    0xcb5b: CPUInstruction(
        name='BIT 3,E',
        length=2,
        cycles=8,
        opcode=0xcb5b
    ),
    0xcb5c: CPUInstruction(
        name='BIT 3,H',
        length=2,
        cycles=8,
        opcode=0xcb5c
    ),
    0xcb5d: CPUInstruction(
        name='BIT 3,L',
        length=2,
        cycles=8,
        opcode=0xcb5d
    ),
    0xcb5e: CPUInstruction(
        name='BIT 3,(HL)',
        length=2,
        cycles=12,
        opcode=0xcb5e
    ),
    0xcb5f: CPUInstruction(
        name='BIT 3,A',
        length=2,
        cycles=8,
        opcode=0xcb5f
    ),
    0xcb60: CPUInstruction(
        name='BIT 4,B',
        length=2,
        cycles=8,
        opcode=0xcb60
    ),
    0xcb61: CPUInstruction(
        name='BIT 4,C',
        length=2,
        cycles=8,
        opcode=0xcb61
    ),
    0xcb62: CPUInstruction(
        name='BIT 4,D',
        length=2,
        cycles=8,
        opcode=0xcb62
    ),
    0xcb63: CPUInstruction(
        name='BIT 4,E',
        length=2,
        cycles=8,
        opcode=0xcb63
    ),
    0xcb64: CPUInstruction(
        name='BIT 4,H',
        length=2,
        cycles=8,
        opcode=0xcb64
    ),
    0xcb65: CPUInstruction(
        name='BIT 4,L',
        length=2,
        cycles=8,
        opcode=0xcb65
    ),
    0xcb66: CPUInstruction(
        name='BIT 4,(HL)',
        length=2,
        cycles=12,
        opcode=0xcb66
    ),
    0xcb67: CPUInstruction(
        name='BIT 4,A',
        length=2,
        cycles=8,
        opcode=0xcb67
    ),
    0xcb68: CPUInstruction(
        name='BIT 5,B',
        length=2,
        cycles=8,
        opcode=0xcb68
    ),
    0xcb69: CPUInstruction(
        name='BIT 5,C',
        length=2,
        cycles=8,
        opcode=0xcb69
    ),
    0xcb6a: CPUInstruction(
        name='BIT 5,D',
        length=2,
        cycles=8,
        opcode=0xcb6a
    ),
    0xcb6b: CPUInstruction(
        name='BIT 5,E',
        length=2,
        cycles=8,
        opcode=0xcb6b
    ),
    0xcb6c: CPUInstruction(
        name='BIT 5,H',
        length=2,
        cycles=8,
        opcode=0xcb6c
    ),
    0xcb6d: CPUInstruction(
        name='BIT 5,L',
        length=2,
        cycles=8,
        opcode=0xcb6d
    ),
    0xcb6e: CPUInstruction(
        name='BIT 5,(HL)',
        length=2,
        cycles=12,
        opcode=0xcb6e
    ),
    0xcb6f: CPUInstruction(
        name='BIT 5,A',
        length=2,
        cycles=8,
        opcode=0xcb6f
    ),
    0xcb70: CPUInstruction(
        name='BIT 6,B',
        length=2,
        cycles=8,
        opcode=0xcb70
    ),
    0xcb71: CPUInstruction(
        name='BIT 6,C',
        length=2,
        cycles=8,
        opcode=0xcb71
    ),
    0xcb72: CPUInstruction(
        name='BIT 6,D',
        length=2,
        cycles=8,
        opcode=0xcb72
    ),
    0xcb73: CPUInstruction(
        name='BIT 6,E',
        length=2,
        cycles=8,
        opcode=0xcb73
    ),
    0xcb74: CPUInstruction(
        name='BIT 6,H',
        length=2,
        cycles=8,
        opcode=0xcb74
    ),
    0xcb75: CPUInstruction(
        name='BIT 6,L',
        length=2,
        cycles=8,
        opcode=0xcb75
    ),
    0xcb76: CPUInstruction(
        name='BIT 6,(HL)',
        length=2,
        cycles=12,
        opcode=0xcb76
    ),
    0xcb77: CPUInstruction(
        name='BIT 6,A',
        length=2,
        cycles=8,
        opcode=0xcb77
    ),
    0xcb78: CPUInstruction(
        name='BIT 7,B',
        length=2,
        cycles=8,
        opcode=0xcb78
    ),
    0xcb79: CPUInstruction(
        name='BIT 7,C',
        length=2,
        cycles=8,
        opcode=0xcb79
    ),
    0xcb7a: CPUInstruction(
        name='BIT 7,D',
        length=2,
        cycles=8,
        opcode=0xcb7a
    ),
    0xcb7b: CPUInstruction(
        name='BIT 7,E',
        length=2,
        cycles=8,
        opcode=0xcb7b
    ),
    0xcb7c: CPUInstruction(
        name='BIT 7,H',
        length=2,
        cycles=8,
        opcode=0xcb7c,
        run=lambda r, m, o: test_bit(r, r.h.value, 7),
    ),
    0xcb7d: CPUInstruction(
        name='BIT 7,L',
        length=2,
        cycles=8,
        opcode=0xcb7d
    ),
    0xcb7e: CPUInstruction(
        name='BIT 7,(HL)',
        length=2,
        cycles=12,
        opcode=0xcb7e
    ),
    0xcb7f: CPUInstruction(
        name='BIT 7,A',
        length=2,
        cycles=8,
        opcode=0xcb7f
    ),
    0xcb80: CPUInstruction(
        name='RES 0,B',
        length=2,
        cycles=8,
        opcode=0xcb80
    ),
    0xcb81: CPUInstruction(
        name='RES 0,C',
        length=2,
        cycles=8,
        opcode=0xcb81
    ),
    0xcb82: CPUInstruction(
        name='RES 0,D',
        length=2,
        cycles=8,
        opcode=0xcb82
    ),
    0xcb83: CPUInstruction(
        name='RES 0,E',
        length=2,
        cycles=8,
        opcode=0xcb83
    ),
    0xcb84: CPUInstruction(
        name='RES 0,H',
        length=2,
        cycles=8,
        opcode=0xcb84
    ),
    0xcb85: CPUInstruction(
        name='RES 0,L',
        length=2,
        cycles=8,
        opcode=0xcb85
    ),
    0xcb86: CPUInstruction(
        name='RES 0,(HL)',
        length=2,
        cycles=16,
        opcode=0xcb86
    ),
    0xcb87: CPUInstruction(
        name='RES 0,A',
        length=2,
        cycles=8,
        opcode=0xcb87
    ),
    0xcb88: CPUInstruction(
        name='RES 1,B',
        length=2,
        cycles=8,
        opcode=0xcb88
    ),
    0xcb89: CPUInstruction(
        name='RES 1,C',
        length=2,
        cycles=8,
        opcode=0xcb89
    ),
    0xcb8a: CPUInstruction(
        name='RES 1,D',
        length=2,
        cycles=8,
        opcode=0xcb8a
    ),
    0xcb8b: CPUInstruction(
        name='RES 1,E',
        length=2,
        cycles=8,
        opcode=0xcb8b
    ),
    0xcb8c: CPUInstruction(
        name='RES 1,H',
        length=2,
        cycles=8,
        opcode=0xcb8c
    ),
    0xcb8d: CPUInstruction(
        name='RES 1,L',
        length=2,
        cycles=8,
        opcode=0xcb8d
    ),
    0xcb8e: CPUInstruction(
        name='RES 1,(HL)',
        length=2,
        cycles=16,
        opcode=0xcb8e
    ),
    0xcb8f: CPUInstruction(
        name='RES 1,A',
        length=2,
        cycles=8,
        opcode=0xcb8f
    ),
    0xcb90: CPUInstruction(
        name='RES 2,B',
        length=2,
        cycles=8,
        opcode=0xcb90
    ),
    0xcb91: CPUInstruction(
        name='RES 2,C',
        length=2,
        cycles=8,
        opcode=0xcb91
    ),
    0xcb92: CPUInstruction(
        name='RES 2,D',
        length=2,
        cycles=8,
        opcode=0xcb92
    ),
    0xcb93: CPUInstruction(
        name='RES 2,E',
        length=2,
        cycles=8,
        opcode=0xcb93
    ),
    0xcb94: CPUInstruction(
        name='RES 2,H',
        length=2,
        cycles=8,
        opcode=0xcb94
    ),
    0xcb95: CPUInstruction(
        name='RES 2,L',
        length=2,
        cycles=8,
        opcode=0xcb95
    ),
    0xcb96: CPUInstruction(
        name='RES 2,(HL)',
        length=2,
        cycles=16,
        opcode=0xcb96
    ),
    0xcb97: CPUInstruction(
        name='RES 2,A',
        length=2,
        cycles=8,
        opcode=0xcb97
    ),
    0xcb98: CPUInstruction(
        name='RES 3,B',
        length=2,
        cycles=8,
        opcode=0xcb98
    ),
    0xcb99: CPUInstruction(
        name='RES 3,C',
        length=2,
        cycles=8,
        opcode=0xcb99
    ),
    0xcb9a: CPUInstruction(
        name='RES 3,D',
        length=2,
        cycles=8,
        opcode=0xcb9a
    ),
    0xcb9b: CPUInstruction(
        name='RES 3,E',
        length=2,
        cycles=8,
        opcode=0xcb9b
    ),
    0xcb9c: CPUInstruction(
        name='RES 3,H',
        length=2,
        cycles=8,
        opcode=0xcb9c
    ),
    0xcb9d: CPUInstruction(
        name='RES 3,L',
        length=2,
        cycles=8,
        opcode=0xcb9d
    ),
    0xcb9e: CPUInstruction(
        name='RES 3,(HL)',
        length=2,
        cycles=16,
        opcode=0xcb9e
    ),
    0xcb9f: CPUInstruction(
        name='RES 3,A',
        length=2,
        cycles=8,
        opcode=0xcb9f
    ),
    0xcba0: CPUInstruction(
        name='RES 4,B',
        length=2,
        cycles=8,
        opcode=0xcba0
    ),
    0xcba1: CPUInstruction(
        name='RES 4,C',
        length=2,
        cycles=8,
        opcode=0xcba1
    ),
    0xcba2: CPUInstruction(
        name='RES 4,D',
        length=2,
        cycles=8,
        opcode=0xcba2
    ),
    0xcba3: CPUInstruction(
        name='RES 4,E',
        length=2,
        cycles=8,
        opcode=0xcba3
    ),
    0xcba4: CPUInstruction(
        name='RES 4,H',
        length=2,
        cycles=8,
        opcode=0xcba4
    ),
    0xcba5: CPUInstruction(
        name='RES 4,L',
        length=2,
        cycles=8,
        opcode=0xcba5
    ),
    0xcba6: CPUInstruction(
        name='RES 4,(HL)',
        length=2,
        cycles=16,
        opcode=0xcba6
    ),
    0xcba7: CPUInstruction(
        name='RES 4,A',
        length=2,
        cycles=8,
        opcode=0xcba7
    ),
    0xcba8: CPUInstruction(
        name='RES 5,B',
        length=2,
        cycles=8,
        opcode=0xcba8
    ),
    0xcba9: CPUInstruction(
        name='RES 5,C',
        length=2,
        cycles=8,
        opcode=0xcba9
    ),
    0xcbaa: CPUInstruction(
        name='RES 5,D',
        length=2,
        cycles=8,
        opcode=0xcbaa
    ),
    0xcbab: CPUInstruction(
        name='RES 5,E',
        length=2,
        cycles=8,
        opcode=0xcbab
    ),
    0xcbac: CPUInstruction(
        name='RES 5,H',
        length=2,
        cycles=8,
        opcode=0xcbac
    ),
    0xcbad: CPUInstruction(
        name='RES 5,L',
        length=2,
        cycles=8,
        opcode=0xcbad
    ),
    0xcbae: CPUInstruction(
        name='RES 5,(HL)',
        length=2,
        cycles=16,
        opcode=0xcbae
    ),
    0xcbaf: CPUInstruction(
        name='RES 5,A',
        length=2,
        cycles=8,
        opcode=0xcbaf
    ),
    0xcbb0: CPUInstruction(
        name='RES 6,B',
        length=2,
        cycles=8,
        opcode=0xcbb0
    ),
    0xcbb1: CPUInstruction(
        name='RES 6,C',
        length=2,
        cycles=8,
        opcode=0xcbb1
    ),
    0xcbb2: CPUInstruction(
        name='RES 6,D',
        length=2,
        cycles=8,
        opcode=0xcbb2
    ),
    0xcbb3: CPUInstruction(
        name='RES 6,E',
        length=2,
        cycles=8,
        opcode=0xcbb3
    ),
    0xcbb4: CPUInstruction(
        name='RES 6,H',
        length=2,
        cycles=8,
        opcode=0xcbb4
    ),
    0xcbb5: CPUInstruction(
        name='RES 6,L',
        length=2,
        cycles=8,
        opcode=0xcbb5
    ),
    0xcbb6: CPUInstruction(
        name='RES 6,(HL)',
        length=2,
        cycles=16,
        opcode=0xcbb6
    ),
    0xcbb7: CPUInstruction(
        name='RES 6,A',
        length=2,
        cycles=8,
        opcode=0xcbb7
    ),
    0xcbb8: CPUInstruction(
        name='RES 7,B',
        length=2,
        cycles=8,
        opcode=0xcbb8
    ),
    0xcbb9: CPUInstruction(
        name='RES 7,C',
        length=2,
        cycles=8,
        opcode=0xcbb9
    ),
    0xcbba: CPUInstruction(
        name='RES 7,D',
        length=2,
        cycles=8,
        opcode=0xcbba
    ),
    0xcbbb: CPUInstruction(
        name='RES 7,E',
        length=2,
        cycles=8,
        opcode=0xcbbb
    ),
    0xcbbc: CPUInstruction(
        name='RES 7,H',
        length=2,
        cycles=8,
        opcode=0xcbbc
    ),
    0xcbbd: CPUInstruction(
        name='RES 7,L',
        length=2,
        cycles=8,
        opcode=0xcbbd
    ),
    0xcbbe: CPUInstruction(
        name='RES 7,(HL)',
        length=2,
        cycles=16,
        opcode=0xcbbe
    ),
    0xcbbf: CPUInstruction(
        name='RES 7,A',
        length=2,
        cycles=8,
        opcode=0xcbbf
    ),
    0xcbc0: CPUInstruction(
        name='SET 0,B',
        length=2,
        cycles=8,
        opcode=0xcbc0
    ),
    0xcbc1: CPUInstruction(
        name='SET 0,C',
        length=2,
        cycles=8,
        opcode=0xcbc1
    ),
    0xcbc2: CPUInstruction(
        name='SET 0,D',
        length=2,
        cycles=8,
        opcode=0xcbc2
    ),
    0xcbc3: CPUInstruction(
        name='SET 0,E',
        length=2,
        cycles=8,
        opcode=0xcbc3
    ),
    0xcbc4: CPUInstruction(
        name='SET 0,H',
        length=2,
        cycles=8,
        opcode=0xcbc4
    ),
    0xcbc5: CPUInstruction(
        name='SET 0,L',
        length=2,
        cycles=8,
        opcode=0xcbc5
    ),
    0xcbc6: CPUInstruction(
        name='SET 0,(HL)',
        length=2,
        cycles=16,
        opcode=0xcbc6
    ),
    0xcbc7: CPUInstruction(
        name='SET 0,A',
        length=2,
        cycles=8,
        opcode=0xcbc7
    ),
    0xcbc8: CPUInstruction(
        name='SET 1,B',
        length=2,
        cycles=8,
        opcode=0xcbc8
    ),
    0xcbc9: CPUInstruction(
        name='SET 1,C',
        length=2,
        cycles=8,
        opcode=0xcbc9
    ),
    0xcbca: CPUInstruction(
        name='SET 1,D',
        length=2,
        cycles=8,
        opcode=0xcbca
    ),
    0xcbcb: CPUInstruction(
        name='SET 1,E',
        length=2,
        cycles=8,
        opcode=0xcbcb
    ),
    0xcbcc: CPUInstruction(
        name='SET 1,H',
        length=2,
        cycles=8,
        opcode=0xcbcc
    ),
    0xcbcd: CPUInstruction(
        name='SET 1,L',
        length=2,
        cycles=8,
        opcode=0xcbcd
    ),
    0xcbce: CPUInstruction(
        name='SET 1,(HL)',
        length=2,
        cycles=16,
        opcode=0xcbce
    ),
    0xcbcf: CPUInstruction(
        name='SET 1,A',
        length=2,
        cycles=8,
        opcode=0xcbcf
    ),
    0xcbd0: CPUInstruction(
        name='SET 2,B',
        length=2,
        cycles=8,
        opcode=0xcbd0
    ),
    0xcbd1: CPUInstruction(
        name='SET 2,C',
        length=2,
        cycles=8,
        opcode=0xcbd1
    ),
    0xcbd2: CPUInstruction(
        name='SET 2,D',
        length=2,
        cycles=8,
        opcode=0xcbd2
    ),
    0xcbd3: CPUInstruction(
        name='SET 2,E',
        length=2,
        cycles=8,
        opcode=0xcbd3
    ),
    0xcbd4: CPUInstruction(
        name='SET 2,H',
        length=2,
        cycles=8,
        opcode=0xcbd4
    ),
    0xcbd5: CPUInstruction(
        name='SET 2,L',
        length=2,
        cycles=8,
        opcode=0xcbd5
    ),
    0xcbd6: CPUInstruction(
        name='SET 2,(HL)',
        length=2,
        cycles=16,
        opcode=0xcbd6
    ),
    0xcbd7: CPUInstruction(
        name='SET 2,A',
        length=2,
        cycles=8,
        opcode=0xcbd7
    ),
    0xcbd8: CPUInstruction(
        name='SET 3,B',
        length=2,
        cycles=8,
        opcode=0xcbd8
    ),
    0xcbd9: CPUInstruction(
        name='SET 3,C',
        length=2,
        cycles=8,
        opcode=0xcbd9
    ),
    0xcbda: CPUInstruction(
        name='SET 3,D',
        length=2,
        cycles=8,
        opcode=0xcbda
    ),
    0xcbdb: CPUInstruction(
        name='SET 3,E',
        length=2,
        cycles=8,
        opcode=0xcbdb
    ),
    0xcbdc: CPUInstruction(
        name='SET 3,H',
        length=2,
        cycles=8,
        opcode=0xcbdc
    ),
    0xcbdd: CPUInstruction(
        name='SET 3,L',
        length=2,
        cycles=8,
        opcode=0xcbdd
    ),
    0xcbde: CPUInstruction(
        name='SET 3,(HL)',
        length=2,
        cycles=16,
        opcode=0xcbde
    ),
    0xcbdf: CPUInstruction(
        name='SET 3,A',
        length=2,
        cycles=8,
        opcode=0xcbdf
    ),
    0xcbe0: CPUInstruction(
        name='SET 4,B',
        length=2,
        cycles=8,
        opcode=0xcbe0
    ),
    0xcbe1: CPUInstruction(
        name='SET 4,C',
        length=2,
        cycles=8,
        opcode=0xcbe1
    ),
    0xcbe2: CPUInstruction(
        name='SET 4,D',
        length=2,
        cycles=8,
        opcode=0xcbe2
    ),
    0xcbe3: CPUInstruction(
        name='SET 4,E',
        length=2,
        cycles=8,
        opcode=0xcbe3
    ),
    0xcbe4: CPUInstruction(
        name='SET 4,H',
        length=2,
        cycles=8,
        opcode=0xcbe4
    ),
    0xcbe5: CPUInstruction(
        name='SET 4,L',
        length=2,
        cycles=8,
        opcode=0xcbe5
    ),
    0xcbe6: CPUInstruction(
        name='SET 4,(HL)',
        length=2,
        cycles=16,
        opcode=0xcbe6
    ),
    0xcbe7: CPUInstruction(
        name='SET 4,A',
        length=2,
        cycles=8,
        opcode=0xcbe7
    ),
    0xcbe8: CPUInstruction(
        name='SET 5,B',
        length=2,
        cycles=8,
        opcode=0xcbe8
    ),
    0xcbe9: CPUInstruction(
        name='SET 5,C',
        length=2,
        cycles=8,
        opcode=0xcbe9
    ),
    0xcbea: CPUInstruction(
        name='SET 5,D',
        length=2,
        cycles=8,
        opcode=0xcbea
    ),
    0xcbeb: CPUInstruction(
        name='SET 5,E',
        length=2,
        cycles=8,
        opcode=0xcbeb
    ),
    0xcbec: CPUInstruction(
        name='SET 5,H',
        length=2,
        cycles=8,
        opcode=0xcbec
    ),
    0xcbed: CPUInstruction(
        name='SET 5,L',
        length=2,
        cycles=8,
        opcode=0xcbed
    ),
    0xcbee: CPUInstruction(
        name='SET 5,(HL)',
        length=2,
        cycles=16,
        opcode=0xcbee
    ),
    0xcbef: CPUInstruction(
        name='SET 5,A',
        length=2,
        cycles=8,
        opcode=0xcbef
    ),
    0xcbf0: CPUInstruction(
        name='SET 6,B',
        length=2,
        cycles=8,
        opcode=0xcbf0
    ),
    0xcbf1: CPUInstruction(
        name='SET 6,C',
        length=2,
        cycles=8,
        opcode=0xcbf1
    ),
    0xcbf2: CPUInstruction(
        name='SET 6,D',
        length=2,
        cycles=8,
        opcode=0xcbf2
    ),
    0xcbf3: CPUInstruction(
        name='SET 6,E',
        length=2,
        cycles=8,
        opcode=0xcbf3
    ),
    0xcbf4: CPUInstruction(
        name='SET 6,H',
        length=2,
        cycles=8,
        opcode=0xcbf4
    ),
    0xcbf5: CPUInstruction(
        name='SET 6,L',
        length=2,
        cycles=8,
        opcode=0xcbf5
    ),
    0xcbf6: CPUInstruction(
        name='SET 6,(HL)',
        length=2,
        cycles=16,
        opcode=0xcbf6
    ),
    0xcbf7: CPUInstruction(
        name='SET 6,A',
        length=2,
        cycles=8,
        opcode=0xcbf7
    ),
    0xcbf8: CPUInstruction(
        name='SET 7,B',
        length=2,
        cycles=8,
        opcode=0xcbf8
    ),
    0xcbf9: CPUInstruction(
        name='SET 7,C',
        length=2,
        cycles=8,
        opcode=0xcbf9
    ),
    0xcbfa: CPUInstruction(
        name='SET 7,D',
        length=2,
        cycles=8,
        opcode=0xcbfa
    ),
    0xcbfb: CPUInstruction(
        name='SET 7,E',
        length=2,
        cycles=8,
        opcode=0xcbfb
    ),
    0xcbfc: CPUInstruction(
        name='SET 7,H',
        length=2,
        cycles=8,
        opcode=0xcbfc
    ),
    0xcbfd: CPUInstruction(
        name='SET 7,L',
        length=2,
        cycles=8,
        opcode=0xcbfd
    ),
    0xcbfe: CPUInstruction(
        name='SET 7,(HL)',
        length=2,
        cycles=16,
        opcode=0xcbfe
    ),
    0xcbff: CPUInstruction(
        name='SET 7,A',
        length=2,
        cycles=8,
        opcode=0xcbff
    ),
}
