from dataclasses import dataclass
from typing import Callable

from cpu.registers import Registers
from mmu.memory import Memory


class Operands:
    def __init__(self, data: bytes):
        if not data:
            raise ValueError('Operands cannot be empty')

        if len(data) > 2:
            raise ValueError('Operands cannot have more than two bytes')

        self.bytes = data

    def to_word(self) -> int:
        return self.bytes[0]

    def to_dword(self) -> int:
        if len(self.bytes) < 2:
            raise RuntimeError('Cannot convert 1 byte to dword')

        return self.bytes[1] << 8 | self.bytes[0]

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
            raise NotImplementedError(f'{self.name} is not implemented')

        if self.run is None:
            self.run = _default_operation

    @property
    def args_length(self) -> int:
        opcode_length = 2 if self.opcode >= 0xcb00 else 1
        return self.length - opcode_length

    def __repr__(self) -> str:
        return f'[{self.opcode:#04x}] {self.name}'
