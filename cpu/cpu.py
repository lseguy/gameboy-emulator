from cpu.instruction import CPUInstruction
from cpu.instruction import Operands
from cpu.interrupts import InterruptsManager
from cpu.timer import Timer
from custom_types import u16
from debugger import Debugger
from mmu.memory import Memory
from cpu.opcodes import opcodes
from cpu.registers import Registers
from custom_types import u8
from utils.bit_operations import combine_bytes


class CPU:
    def __init__(self, memory: Memory, enable_debugger: bool):
        self._memory = memory
        self._registers = Registers()
        self._interrupts_manager = InterruptsManager(self._registers, self._memory)
        self._timer = Timer(self._memory, self._interrupts_manager)
        self._debugger = Debugger(self._registers, self._memory, self._timer, enable_debugger)

        # Skip the bootrom for now and start directly with cartridge data
        self._registers.pc = 0x100
        #self.registers.sp = 0xfffe

    def start(self) -> None:
        while True:
            if self._registers.halted:
                self._timer.tick(1)
                if self._interrupts_manager.is_any_interrupt_scheduled():
                    self._registers.halted = False
            else:
                byte = self._fetch()
                instruction = self._decode(byte)

                if instruction.args_length:
                    args = Operands(bytes(self._fetch() for _ in range(instruction.args_length)))
                else:
                    args = None

                self._debugger.debug(instruction, args)
                self._execute(instruction, args)

            self._interrupts_manager.handle_interrupts()

    def _fetch(self) -> u8:
        data = self._memory.read(self._registers.pc)
        self._registers.pc = u16(self._registers.pc + 1)
        return data

    def _decode(self, byte: u8) -> CPUInstruction:
        if self._is_prefixed_opcode(byte):
            opcode = combine_bytes(u8(0xcb), self._fetch())
        else:
            opcode = byte

        return opcodes[opcode]

    def _execute(self, instruction: CPUInstruction, operands: Operands) -> None:
        branched = instruction.run(self._registers, self._memory, operands)
        cycles = instruction.cycles_branch if branched else instruction.cycles_no_branch
        self._timer.tick(cycles)

    @staticmethod
    def _is_prefixed_opcode(byte: u8) -> bool:
        return byte == 0xcb
