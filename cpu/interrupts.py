from enum import Flag

from cpu.opcodes import call
from cpu.registers import Registers
from custom_types import u16

from mmu.memory import Memory
from utils.bit_operations import get_bit
from utils.bit_operations import set_bit


# Interrupt flags with their bit position
class InterruptFlag(Flag):
    VBLANK = 0
    LCD = 1
    TIMER = 2
    SERIAL = 3
    JOYPAD = 4


# Address of the ISR associated to each interrupt
INTERRUPT_SERVICE_ROUTINES = {
    InterruptFlag.VBLANK: u16(0x0040),
    InterruptFlag.LCD: u16(0x0048),
    InterruptFlag.TIMER: u16(0x0050),
    InterruptFlag.SERIAL: u16(0x0058),
    InterruptFlag.JOYPAD: u16(0x0060),
}


IF_REGISTER_ADDRESS = u16(0xff0f)
IE_REGISTER_ADDRESS = u16(0xffff)


class InterruptsManager:
    def __init__(self, registers: Registers, memory: Memory):
        self._registers = registers
        self._memory = memory

    def handle_interrupts(self) -> None:
        if not self._registers.ime:
            return

        for flag in InterruptFlag:
            if self._should_trigger_interrupt(flag):
                self._process_interrupt(flag)

    def set_interrupt(self, flag: InterruptFlag) -> None:
        self._update_interrupt_flag(flag, True)

    def reset_interrupt(self, flag: InterruptFlag) -> None:
        self._update_interrupt_flag(flag, False)

    def _update_interrupt_flag(self, flag: InterruptFlag, enabled: bool) -> None:
        interrupt_flags = self._memory.read(IF_REGISTER_ADDRESS)
        updated_interrupt_flags = set_bit(interrupt_flags, flag.value, int(enabled))
        self._memory.write_u8(IF_REGISTER_ADDRESS, updated_interrupt_flags)

    def is_any_interrupt_scheduled(self) -> bool:
        interrupt_enable = self._memory.read(IE_REGISTER_ADDRESS)
        interrupt_flags = self._memory.read(IF_REGISTER_ADDRESS)
        return interrupt_enable & interrupt_flags != 0x0

    def _process_interrupt(self, flag: InterruptFlag) -> None:
        self._registers.ime = False
        self.reset_interrupt(flag)

        isr_address = INTERRUPT_SERVICE_ROUTINES[flag]
        call(self._registers, self._memory, isr_address)

    def _should_trigger_interrupt(self, flag: InterruptFlag) -> bool:
        interrupt_enable = self._memory.read(IE_REGISTER_ADDRESS)
        interrupt_flags = self._memory.read(IF_REGISTER_ADDRESS)
        return get_bit(interrupt_flags & interrupt_enable, flag.value) == 1
