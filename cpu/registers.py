from dataclasses import dataclass
from typing import Tuple

from utils.bit_operations import get_bit
from utils.bit_operations import set_bit

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
        setattr(instance, self.private_name, value & 0xff)


@dataclass
class Registers:
    a: int = Register()
    b: int = Register()
    c: int = Register()
    d: int = Register()
    e: int = Register()
    f: int = Register()
    h: int = Register()
    l: int = Register()
    sp: int = Register()
    pc: int = Register()

    @property
    def af(self) -> int:
        return self._combine_bytes(self.a, self.f)

    @af.setter
    def af(self, value: int) -> None:
        self.a, self.f = self._split_bytes(value)

    @property
    def bc(self) -> int:
        return self._combine_bytes(self.b, self.c)

    @bc.setter
    def bc(self, value: int) -> None:
        self.b, self.c = self._split_bytes(value)

    @property
    def de(self) -> int:
        return self._combine_bytes(self.d, self.e)

    @de.setter
    def de(self, value: int) -> None:
        self.d, self.e = self._split_bytes(value)

    @property
    def hl(self) -> int:
        return self._combine_bytes(self.h, self.l)

    @hl.setter
    def hl(self, value: int) -> None:
        self.h, self.l = self._split_bytes(value)

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
        self.f = set_bit(self.f, flag_position, int(value))

    def _get_flag(self, flag_position: int) -> bool:
        return get_bit(self.f, flag_position) != 0

    @staticmethod
    def _combine_bytes(left: int, right: int) -> int:
        return (left << 8) | right

    @staticmethod
    def _split_bytes(value: int) -> Tuple[int, int]:
        return value >> 8, value & 0xff
