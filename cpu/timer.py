from custom_types import u16
from custom_types import u8
from mmu.memory import Memory
from utils.bit_operations import get_bit
from utils.bit_operations import set_bit

FREQUENCY = 4_194_304  # Hertz
DIV_INC_STEP = FREQUENCY / 16_384

DIV_REGISTER_ADDRESS = u16(0xff04)
TIMA_REGISTER_ADDRESS = u16(0xff05)
TMA_REGISTER_ADDRESS = u16(0xff06)
TAC_REGISTER_ADDRESS = u16(0xff07)

IF_REGISTER_ADDRESS = u16(0xff0f)


class Timer:
    def __init__(self, memory: Memory):
        self._memory = memory
        self._cycles_since_last_div_inc = 0
        self._cycles_since_last_tima_inc = 0

    def inc(self, cycles: int) -> None:
        self._cycles_since_last_div_inc += cycles

        # the longest instruction takes 24 cycles, it's impossible to overflow more than once
        if self._cycles_since_last_div_inc >= DIV_INC_STEP:
            self._cycles_since_last_div_inc -= DIV_INC_STEP
            self._inc_div()

        if not self._is_timer_enabled():
            return

        self._cycles_since_last_tima_inc += cycles
        divider = FREQUENCY / self._tima_inc_frequency()

        while self._cycles_since_last_tima_inc >= divider:
            self._cycles_since_last_tima_inc -= divider
            self._inc_tima()

    def _inc_div(self):
        current_value = self._memory.read(DIV_REGISTER_ADDRESS)
        self._memory.write_u8(DIV_REGISTER_ADDRESS, u8(current_value + 1))

    def _inc_tima(self):
        current_value = self._memory.read(TIMA_REGISTER_ADDRESS)

        if current_value == 0xff:
            # TIMA overflows, reset to TMA's value
            tma = self._memory.read(TMA_REGISTER_ADDRESS)
            self._memory.write_u8(TIMA_REGISTER_ADDRESS, tma)
            # set interrupt
            interrupt_flags = self._memory.read(IF_REGISTER_ADDRESS)
            new_interrupt_flags = set_bit(interrupt_flags, 2, 1)
            self._memory.write_u8(IF_REGISTER_ADDRESS, u8(new_interrupt_flags))
        else:
            self._memory.write_u8(TIMA_REGISTER_ADDRESS, u8(current_value + 1))

    def _tima_inc_frequency(self) -> int:
        timer_control = self._memory.read(TAC_REGISTER_ADDRESS)
        input_clock_selection = timer_control & 0x3

        if input_clock_selection == 0x0:
            return 4_096
        elif input_clock_selection == 0x1:
            return 262_144
        elif input_clock_selection == 0x2:
            return 65_536
        elif input_clock_selection == 0x3:
            return 16_384

    def _is_timer_enabled(self) -> bool:
        timer_control = self._memory.read(TAC_REGISTER_ADDRESS)
        return get_bit(timer_control, 2) == 1

    def __repr__(self):
        return (
            f'enabled={self._is_timer_enabled()}, TIMA frequency={self._tima_inc_frequency()}Hz, '
            f'DIV={self._memory.read(DIV_REGISTER_ADDRESS)}, '
            f'TIMA={self._memory.read(TIMA_REGISTER_ADDRESS)}'
        )
