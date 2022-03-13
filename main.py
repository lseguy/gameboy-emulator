import argparse

from cpu.cpu import CPU
from mmu.memory import Memory
from utils.files import read_binary_file


def start(filename: str, enable_debugger: bool) -> None:
    memory = Memory()
    rom_data = read_binary_file(filename)
    memory.load_rom(rom_data)

    cpu = CPU(memory, enable_debugger)
    cpu.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GameBoy Emulator.')
    parser.add_argument('filename', help='the filename of the ROM to run')
    parser.add_argument('-d', '--debugger', action='store_true', help='enable the debugger')
    args = parser.parse_args()

    start(args.filename, args.debugger)
