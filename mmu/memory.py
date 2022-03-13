from typing import Union

from custom_types import u16
from custom_types import u8
from utils.bit_operations import split_bytes

SIZE = 65536  # 64KB
IME_ADDRESS = 0xffff


class Memory:
    def __init__(self):
        self.content = bytearray(SIZE)

    def load_boot_rom(self, data: bytes) -> None:
        self.content[0:256] = data

    def load_rom(self, data: bytes) -> None:
        self.content[0:0x8000] = data.ljust(0x8000, b'\x00')

    @property
    def ime(self) -> bool:
        return self.content[IME_ADDRESS] == 1

    @ime.setter
    def ime(self, value: bool) -> None:
        self.content[IME_ADDRESS] = int(value)

    def read(self, address: u16) -> u8:
        self._raise_for_invalid_address(address)
        return u8(self.content[address])

    def write_u8(self, address: u16, value: u8) -> None:
        self._raise_for_invalid_address(address)
        self.content[address] = value

        # Blargg serial test output
        if address == 0xff02 and value == 0x81:
            print(chr(self.content[0xff01]), end='')
            #self.content[0xff02] = 0x0

    def write_u16(self, address: u16, value: u16) -> None:
        self._raise_for_invalid_address(address)
        self._raise_for_invalid_address(address+1)
        msb, lsb = split_bytes(value)
        self.content[address] = lsb
        self.content[address+1] = msb

    @staticmethod
    def _raise_for_invalid_address(address):
        # 0xFFFF is the IME flag
        # It can only be manipulated with dedicated CPU instructions
        # TODO: Check if allowed to write to IME location
        #if address < 0 or address >= 0xffff:
        if address < 0 or address > 0xffff:
            raise ValueError('Invalid memory address')

    def __str__(self) -> str:
        return (
            'ROM\n'
            f'{self._dump_memory(0, 0x4000)}\n'
            'Switchable ROM Bank\n'
            f'{self._dump_memory(0x4000, 0x8000)}\n'
            #f'VRAM\n'
            #f'{self._dump_memory(32768, 40960)}\n'
        )

    def __repr__(self) -> str:
        return self._dump_memory(0, len(self.content))

    def _dump_memory(self, start: int, end: int) -> str:
        return '\n'.join([f'{hex(i)} {self.content[i:i+16].hex(" ")}' for i in range(start, end, 16)])
