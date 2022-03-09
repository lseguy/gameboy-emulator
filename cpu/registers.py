from dataclasses import dataclass

from utils.bit_operations import get_bit
from utils.bit_operations import set_bit

Z_FLAG_POSITION = 7
N_FLAG_POSITION = 6
H_FLAG_POSITION = 5
C_FLAG_POSITION = 4


@dataclass
class Register:
    _value: int = 0

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, new_value: int) -> None:
        self._value = new_value & 0xff


@dataclass
class Registers:
    a: Register = Register()
    b: Register = Register()
    c: Register = Register()
    d: Register = Register()
    e: Register = Register()
    f: Register = Register()
    h: Register = Register()
    l: Register = Register()
    sp: Register = Register()
    pc: Register = Register()

    @property
    def af(self) -> int:
        return self._read_paired_registers(self.a, self.f)

    @af.setter
    def af(self, value: int):
        self._write_paired_registers(self.a, self.f, value)

    @property
    def bc(self) -> int:
        return self._read_paired_registers(self.b, self.c)

    @bc.setter
    def bc(self, value: int):
        self._write_paired_registers(self.b, self.c, value)

    @property
    def de(self) -> int:
        return self._read_paired_registers(self.d, self.e)

    @de.setter
    def de(self, value: int):
        self._write_paired_registers(self.d, self.e, value)

    @property
    def hl(self) -> int:
        return self._read_paired_registers(self.h, self.l)

    @hl.setter
    def hl(self, value: int):
        self._write_paired_registers(self.h, self.l, value)

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
        self.f.value = set_bit(self.f.value, flag_position, int(value))

    def _get_flag(self, flag_position: int) -> bool:
        return get_bit(self.f.value, flag_position) != 0

    @staticmethod
    def _read_paired_registers(left: Register, right: Register) -> int:
        return (left.value << 8) | right.value

    @staticmethod
    def _write_paired_registers(left: Register, right: Register, value: int) -> None:
        left.value = value >> 8
        right.value = value & 0xff
