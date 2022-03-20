from dataclasses import dataclass

from custom_types import u16
from custom_types import u8
from utils.bit_operations import combine_bytes
from utils.bit_operations import get_bit
from utils.bit_operations import set_bit
from utils.bit_operations import split_bytes

Z_FLAG_POSITION = 7
N_FLAG_POSITION = 6
H_FLAG_POSITION = 5
C_FLAG_POSITION = 4


class Register:
    def __set_name__(self, owner, name):
        self.private_name = f'_{name}'

    def __get__(self, instance, owner):
        return getattr(instance, self.private_name, 0)

    def __set__(self, instance, value):
        # TODO: Combine registers into 16 bits and add check 0xffff
        setattr(instance, self.private_name, value)


@dataclass
class Registers:
    a: u8 = Register()
    b: u8 = Register()
    c: u8 = Register()
    d: u8 = Register()
    e: u8 = Register()
    f: u8 = Register()
    h: u8 = Register()
    l: u8 = Register()
    sp: u16 = Register()
    pc: u16 = Register()

    ime: bool = False
    halted: bool = False

    @property
    def af(self) -> u16:
        return combine_bytes(self.a, self.f)

    @af.setter
    def af(self, value: u16) -> None:
        self.a, self.f = split_bytes(value)

    @property
    def bc(self) -> u16:
        return combine_bytes(self.b, self.c)

    @bc.setter
    def bc(self, value: u16) -> None:
        self.b, self.c = split_bytes(value)

    @property
    def de(self) -> u16:
        return combine_bytes(self.d, self.e)

    @de.setter
    def de(self, value: u16) -> None:
        self.d, self.e = split_bytes(value)

    @property
    def hl(self) -> u16:
        return combine_bytes(self.h, self.l)

    @hl.setter
    def hl(self, value: u16) -> None:
        self.h, self.l = split_bytes(value)

    @property
    def z_flag(self) -> bool:
        return self._get_flag(Z_FLAG_POSITION)

    @z_flag.setter
    def z_flag(self, value: bool) -> None:
        self._set_flag(Z_FLAG_POSITION, value)

    @property
    def n_flag(self) -> bool:
        return self._get_flag(N_FLAG_POSITION)

    @n_flag.setter
    def n_flag(self, value: bool) -> None:
        self._set_flag(N_FLAG_POSITION, value)

    @property
    def h_flag(self) -> bool:
        return self._get_flag(H_FLAG_POSITION)

    @h_flag.setter
    def h_flag(self, value: bool) -> None:
        self._set_flag(H_FLAG_POSITION, value)

    @property
    def c_flag(self) -> bool:
        return self._get_flag(C_FLAG_POSITION)

    @c_flag.setter
    def c_flag(self, value: bool) -> None:
        self._set_flag(C_FLAG_POSITION, value)

    def _set_flag(self, flag_position: int, value: bool) -> None:
        flags = set_bit(self.f, flag_position, int(value))
        self.f = u8(flags)

    def _get_flag(self, flag_position: int) -> bool:
        return get_bit(self.f, flag_position) != 0

    def __str__(self):
        def to_hex(value: u16) -> str:
            return f'{value:#06x}'

        return (
            f'AF={to_hex(self.af)}, BC={to_hex(self.bc)}, DE={to_hex(self.de)}, HL={to_hex(self.hl)}\n'
            f'SP={to_hex(self.sp)}, PC={to_hex(self.pc)}, IME={self.ime}\n'
            f'Z={self.z_flag}, N={self.n_flag}, H={self.h_flag}, C={self.c_flag}'
        )
