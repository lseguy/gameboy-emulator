import sys

from cpu.instruction import CPUInstruction
from cpu.instruction import Operands
from cpu.registers import Registers
from mmu.memory import Memory

GREEN = '\033[32m'
BLUE = '\033[34m'
RESET = '\033[0m'


class Debugger:
    def __init__(self, registers: Registers, memory: Memory, enabled: bool):
        self.memory = memory
        self.registers = registers
        self.enabled = enabled
        self.jump_address = None
        self.skip = None

    def debug(self, instruction: CPUInstruction, operands: Operands) -> None:
        if not self.enabled:
            return

        if operands:
            print(f'{GREEN}{instruction} ${operands}{RESET}')
        else:
            print(f'{GREEN}{instruction}{RESET}')

        if self.jump_address and self.registers.pc < self.jump_address:
            return
        self.jump_address = None

        if self.skip and self.skip != 0:
            self.skip -= 1
            return
        self.skip = None

        self._prompt()

    def _print_memory(self) -> None:
        def prompt_address(text):
            address = -1

            while address < 0x0 or address > 0xffff:
                try:
                    address = int(input(text), 16)
                except ValueError:
                    pass

            return address

        start = prompt_address('hex address start? ')
        end = prompt_address('hex address end? ')

        print(f'{BLUE}{self.memory.dump_memory(start, end+1)}{RESET}')

    def _jump(self) -> None:
        print(f'current PC={self.registers.pc:#06x}')
        address = None

        while not address:
            try:
                address = int(input('minimum hex address of PC to stop: '), 16)
            except ValueError:
                pass

        self.jump_address = address


    def _step(self) -> None:
        step = None

        while not step:
            try:
                step = int(input('run number of instructions: '))
            except ValueError:
                pass

        # We'll already execute the current instruction
        self.skip = step - 1


    def _prompt(self) -> None:
        while True:
            choice = input(
                f'print [r]egisters / print [m]emory / [q]uit / [s]tep / '
                f'[j]ump / [d]isable debugger / [c]ontinue (default): '
            )
            if choice == '' or choice == 'c':
                return
            elif choice == 'q':
                sys.exit(0)
            elif choice == 'j':
                self._jump()
                return
            elif choice == 's':
                self._step()
                return
            elif choice == 'r':
                print(f'{BLUE}{self.registers}{RESET}')
            elif choice == 'm':
                self._print_memory()
            elif choice == 'd':
                self.enabled = False
                return
