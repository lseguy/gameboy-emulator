from cpu.instruction import CPUInstruction
from cpu.instruction import Operands
from custom_types import u16
from debugger import Debugger
from mmu.memory import Memory
from cpu.opcodes import opcodes
from cpu.registers import Registers
from custom_types import u8
from utils.bit_operations import combine_bytes


class CPU:
    def __init__(self, memory: Memory, enable_debugger: bool):
        self.memory = memory
        self.registers = Registers()

        self.debugger = Debugger(self.registers, self.memory, enable_debugger)

        # Skip the bootrom for now and start directly with cartridge data
        self.registers.pc = 0x100
        self.registers.a = 0x11
        self.registers.f = 0x80
        self.registers.d = 0xff
        self.registers.e = 0x56
        self.registers.l = 0x0d
        self.registers.sp = 0xfffe

    def start(self) -> None:
        while True:
            byte = self.fetch()
            instruction = self.decode(byte)

            if instruction.args_length:
                args = Operands(bytes(self.fetch() for _ in range(instruction.args_length)))
            else:
                args = None

            self.debugger.debug(instruction, args)
            self.execute(instruction, args)

    def fetch(self) -> u8:
        data = self.memory.read(self.registers.pc)
        self.registers.pc = u16(self.registers.pc + 1)
        return data

    def decode(self, byte: u8) -> CPUInstruction:
        if self._is_prefixed_opcode(byte):
            opcode = combine_bytes(u8(0xcb), self.fetch())
        else:
            opcode = byte

        return opcodes[opcode]

    def execute(self, instruction: CPUInstruction, operands: Operands) -> None:
        instruction.run(self.registers, self.memory, operands)

    @staticmethod
    def _is_prefixed_opcode(byte: u8) -> bool:
        return byte == 0xcb
