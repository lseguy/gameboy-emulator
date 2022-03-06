import argparse
from typing import BinaryIO
from typing import Optional

from opcodes import opcodes


def read_rom(filename):
    with open(filename, 'rb') as f:
        while True:
            operation = read_operation(f)
            if not operation:
                break

            print(operation)


def read_operation(file: BinaryIO) -> Optional[str]:
    byte = file.read(1)

    if not byte:
        return

    if is_prefixed_opcode(byte):
        opcode = opcodes[byte + file.read(1)]
    else:
        opcode = opcodes[byte]

    operands_bytes = file.read(opcode.args_length)
    return f'{opcode} ${read_operand(operands_bytes).hex()}'


def is_prefixed_opcode(byte):
    return byte == b'\xcb'


def read_operand(arg: bytes) -> bytes:
    # Arguments are little-endian
    return bytes(reversed(arg))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Decompiles a GameBoy ROM.')
    parser.add_argument('filename', help='the filename of the ROM to decompile')
    args = parser.parse_args()

    read_rom(args.filename)
