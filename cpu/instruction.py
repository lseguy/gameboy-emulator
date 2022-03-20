from dataclasses import dataclass
from typing import Callable

from cpu.registers import Registers
from custom_types import i8
from custom_types import u16
from custom_types import u8
from mmu.memory import Memory
from utils.bit_operations import combine_bytes
from utils.bit_operations import read_signed


class Operands:
    def __init__(self, data: bytes):
        if not data:
            raise ValueError('Operands cannot be empty')

        if len(data) > 2:
            raise ValueError('Operands cannot have more than two bytes')

        self._bytes = data

    def to_u8(self) -> u8:
        return u8(self._bytes[0])

    def to_i8(self) -> i8:
        return read_signed(self.to_u8())

    def to_u16(self) -> u16:
        if len(self._bytes) < 2:
            raise RuntimeError('Cannot convert 1 byte operand to u16')

        return combine_bytes(u8(self._bytes[1]), u8(self._bytes[0]))

    def __repr__(self) -> str:
        if len(self._bytes) == 1:
            return f'{self.to_u8():x}'

        return f'{self.to_u16():x}'


# The function returns whether the instruction branched or not
InstructionRunnable = Callable[[Registers, Memory, Operands], bool]


@dataclass
class CPUInstruction:
    name: str
    opcode: int
    length: int
    cycles_no_branch: int
    cycles_branch: int
    run: InstructionRunnable = None

    def __post_init__(self):
        def _default_operation(*args):
            raise NotImplementedError(f'[{self.opcode:#x}] {self.name} is not implemented')

        if self.run is None:
            self.run = _default_operation

    @property
    def args_length(self) -> int:
        opcode_length = 2 if self.opcode >= 0xcb00 else 1
        return self.length - opcode_length

    def __repr__(self) -> str:
        return f'[{self.opcode:#04x}] {self.name}'
