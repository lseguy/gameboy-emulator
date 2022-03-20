from cpu.interrupts import InterruptFlag
from cpu.interrupts import InterruptsManager
from custom_types import u16
from mmu.memory import Memory
from utils.bit_operations import get_bit

FREQUENCY = 4_194_304  # Hertz
DIV_INCREMENT_STEP = FREQUENCY / 16_384
TIMER_FREQUENCIES = [4_096, 262_144, 65_536, 16_384]  # Configurable timer frequencies in Hertz

DIV_REGISTER_ADDRESS = u16(0xff04)
TIMA_REGISTER_ADDRESS = u16(0xff05)
TMA_REGISTER_ADDRESS = u16(0xff06)
TAC_REGISTER_ADDRESS = u16(0xff07)


class Timer:
    def __init__(self, memory: Memory, interrupts_manager: InterruptsManager):
        self._memory = memory
        self._interrupts_manager = interrupts_manager
        self._div_counter = 0
        self._tima_counter = 0

    def tick(self, cycles: int) -> None:
        self._div_counter += cycles

        # the longest instruction takes 24 cycles, it's impossible to overflow more than once
        if self._div_counter >= DIV_INCREMENT_STEP:
            self._div_counter -= DIV_INCREMENT_STEP
            self._memory.inc_u8(DIV_REGISTER_ADDRESS)

        # TIMA is not incremented when the timer is disabled
        if not self._is_timer_enabled():
            return

        self._tima_counter += cycles
        tima_increment_step = FREQUENCY // self._tima_inc_frequency()

        while self._tima_counter >= tima_increment_step:
            self._tima_counter -= tima_increment_step
            self._increment_tima()

    def _increment_tima(self):
        overflow = self._memory.inc_u8(TIMA_REGISTER_ADDRESS)

        if overflow:
            # TIMA overflowed, reset it to TMA's value
            tma = self._memory.read(TMA_REGISTER_ADDRESS)
            self._memory.write_u8(TIMA_REGISTER_ADDRESS, tma)

            # And trigger the interrupt
            self._interrupts_manager.set_interrupt(InterruptFlag.TIMER)

    def _tima_inc_frequency(self) -> int:
        timer_control = self._memory.read(TAC_REGISTER_ADDRESS)
        input_clock_selection = timer_control & 0x3
        return TIMER_FREQUENCIES[input_clock_selection]

    def _is_timer_enabled(self) -> bool:
        timer_control = self._memory.read(TAC_REGISTER_ADDRESS)
        return get_bit(timer_control, 2) == 1

    def __str__(self):
        return (
            f'enabled={self._is_timer_enabled()}, frequency={self._tima_inc_frequency()}Hz, '
            f'DIV={self._memory.read(DIV_REGISTER_ADDRESS)}, TIMA={self._memory.read(TIMA_REGISTER_ADDRESS)}'
        )
