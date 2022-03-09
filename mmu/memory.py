SIZE = 65535


class Memory:
    def __init__(self):
        self.content = bytearray(SIZE)

    def load_boot_rom(self, data: bytes) -> None:
        self.content[0:256] = data

    def load_rom(self, data: bytes) -> None:
        self.content[336:16384] = data.ljust(16048, b'\x00')

    def read(self, address: int) -> int:
        return self.content[address]

    def write(self, address: int, value: int) -> None:
        self.content[address] = value

    def __str__(self) -> str:
        return (
            f'{self._dump_memory(0, 336)}'
            'Cartridge ROM Bank 0\n'
            f'{self._dump_memory(336, 16384)}'
            f'VRAM\n'
            f'{self._dump_memory(32768, 40960)}'
        )

    def __repr__(self) -> str:
        return self._dump_memory(0, len(self.content))

    def _dump_memory(self, start: int, end: int) -> str:
        return '\n'.join([f'{hex(i)} {self.content[i:i+16].hex(" ")}' for i in range(start, end, 16)])
