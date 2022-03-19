from cpu.instruction import CPUInstruction
from cpu.instruction import Operands
from cpu.opcodes import call
from custom_types import u16
from debugger import Debugger
from mmu.memory import Memory
from cpu.opcodes import opcodes
from cpu.registers import Registers
from custom_types import u8
from utils.bit_operations import combine_bytes
from utils.bit_operations import get_bit
from utils.bit_operations import set_bit

# Interrupt Flags positions
IF_VBLANK_POSITION = 0
IF_LCD_POSITION = 1
IF_TIMER_POSITION = 2
IF_SERIAL_POSITION = 3
IF_JOYPAD_POSITION = 4

FREQUENCY = 1_048_576  # Hertz


class CPU:
    def __init__(self, memory: Memory, enable_debugger: bool):
        self.memory = memory
        self.registers = Registers()

        self.debugger = Debugger(self.registers, self.memory, enable_debugger)

        # Skip the bootrom for now and start directly with cartridge data
        self.registers.pc = 0x100

    def start(self) -> None:
        while True:
            byte = self._fetch()
            instruction = self._decode(byte)

            if instruction.args_length:
                args = Operands(bytes(self._fetch() for _ in range(instruction.args_length)))
            else:
                args = None

            self.debugger.debug(instruction, args)
            self._execute(instruction, args)
            self._check_interrupts()

    def _fetch(self) -> u8:
        data = self.memory.read(self.registers.pc)
        self.registers.pc = u16(self.registers.pc + 1)
        return data

    def _decode(self, byte: u8) -> CPUInstruction:
        if self._is_prefixed_opcode(byte):
            opcode = combine_bytes(u8(0xcb), self._fetch())
        else:
            opcode = byte

        return opcodes[opcode]

    def _execute(self, instruction: CPUInstruction, operands: Operands) -> None:
        instruction.run(self.registers, self.memory, operands)

    def _check_interrupts(self):
        if not self.registers.ime:
            return

        if self._should_trigger_interrupt(IF_VBLANK_POSITION):
            self._handle_interrupt(IF_VBLANK_POSITION, u16(0x0040))
        elif self._should_trigger_interrupt(IF_LCD_POSITION):
            self._handle_interrupt(IF_LCD_POSITION, u16(0x0048))
        elif self._should_trigger_interrupt(IF_TIMER_POSITION):
            self._handle_interrupt(IF_TIMER_POSITION, u16(0x0050))
        elif self._should_trigger_interrupt(IF_SERIAL_POSITION):
            self._handle_interrupt(IF_SERIAL_POSITION, u16(0x0058))
        elif self._should_trigger_interrupt(IF_JOYPAD_POSITION):
            self._handle_interrupt(IF_JOYPAD_POSITION, u16(0x0060))

    def _handle_interrupt(self, flag_position:int, isr_address: u16):
        self.registers.ime = False
        interrupt_flags = self.memory.read(u16(0xff0f))
        updated_interrupt_flags = set_bit(interrupt_flags, flag_position, 0)
        self.memory.write_u8(u16(0xff0f), updated_interrupt_flags)
        call(self.registers, self.memory, isr_address)

    def _should_trigger_interrupt(self, flag_position: int) -> bool:
        interrupt_enable = self.memory.read(u16(0xffff))
        interrupt_flags = self.memory.read(u16(0xff0f))
        return get_bit(interrupt_enable, flag_position) == 1 and get_bit(interrupt_flags, flag_position) == 1

    @staticmethod
    def _is_prefixed_opcode(byte: u8) -> bool:
        return byte == 0xcb
