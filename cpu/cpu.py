from cpu.instruction import CPUInstruction
from cpu.instruction import Operands
from mmu.memory import Memory
from cpu.opcodes import opcodes
from cpu.registers import Registers


class CPU:
    def __init__(self, memory: Memory):
        self.memory = memory
        self.registers = Registers()

    def start(self) -> None:
        while True:
            byte = self.fetch()
            instruction = self.decode(byte)

            if instruction.args_length:
                args = Operands(bytes(self.fetch() for _ in range(instruction.args_length)))
            else:
                args = None

            if args:
                print(f'{instruction} ${args}')
            else:
                print(instruction)

            self.execute(instruction, args)
            print(self.registers)

    def fetch(self) -> int:
        pc = self.registers.pc
        data = self.memory.read(pc.value)
        pc.value += 1
        return data

    def decode(self, byte: int) -> CPUInstruction:
        if self._is_prefixed_opcode(byte):
            opcode = 0xcb << 8 | self.fetch()
        else:
            opcode = byte

        return opcodes[opcode]

    def execute(self, instruction: CPUInstruction, operands: Operands) -> None:
        instruction.run(self.registers, self.memory, operands)

    @staticmethod
    def _is_prefixed_opcode(byte: int) -> bool:
        return byte == 0xcb
