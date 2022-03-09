import argparse
from typing import Iterator

from cpu.opcodes import opcodes
from utils.files import read_binary_file


def decompile(iterator: Iterator[int]) -> None:
    while True:
        opcode = next(iterator, None)
        if opcode is None:
            return

        if is_prefixed_opcode(opcode):
            opcode = opcode << 8 | next(iterator)

        instruction = opcodes[opcode]
        operand_bytes = bytes([next(iterator) for _ in range(instruction.args_length)])

        if len(operand_bytes) > 0:
            operands = read_operands(operand_bytes)
            print(f'{instruction} ${operands:x}')
        else:
            print(instruction)


def is_prefixed_opcode(byte: int) -> bool:
    return byte == 0xcb


def read_operands(arg: bytes) -> int:
    return int.from_bytes(arg, byteorder='little')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Decompiles a GameBoy ROM.')
    parser.add_argument('filename', help='the filename of the ROM to decompile')
    args = parser.parse_args()

    file_data = read_binary_file(args.filename)
    decompile(iter(file_data))
