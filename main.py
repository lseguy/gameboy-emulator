import argparse

from cpu.cpu import CPU
from mmu.memory import Memory
from utils.files import read_binary_file


def start(filename: str):
    memory = Memory()
    boot_rom_data = read_binary_file(filename)
    #memory.load_boot_rom(boot_rom_data)
    memory.load_rom(boot_rom_data)

    cpu = CPU(memory)
    cpu.registers.pc = 0x100
    cpu.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GameBoy Emulator.')
    parser.add_argument('filename', help='the filename of the ROM to run')
    args = parser.parse_args()

    start(args.filename)
