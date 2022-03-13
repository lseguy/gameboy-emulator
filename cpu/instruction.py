from dataclasses import dataclass
from typing import Callable
from typing import Optional

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

        self.bytes = data

    def to_word(self) -> u8:
        return u8(self.bytes[0])

    def to_signed_word(self) -> i8:
        return read_signed(self.to_word())

    def to_dword(self) -> u16:
        if len(self.bytes) < 2:
            raise RuntimeError('Cannot convert 1 byte to dword')

        return combine_bytes(u8(self.bytes[1]), u8(self.bytes[0]))

    def __repr__(self) -> str:
        if len(self.bytes) == 1:
            return f'{self.to_word():x}'

        return f'{self.to_dword():x}'


@dataclass
class CPUInstruction:
    name: str
    opcode: int
    length: int
    cycles: int
    run: Callable[[Registers, Memory, Operands], None] = None

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
